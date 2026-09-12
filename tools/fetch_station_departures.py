"""Snapshot the published departure board of every trunk station, for the wagon each service uses.

The board comes from a service named in tools/en_vivo.local.json, which is not versioned; without
that file this does nothing. Its `stop` field names the boarding point the operator publishes — "Mandalay A - 2 ó 5",
"Portal Américas T5" — which is what the station signage and the on-board screens show, and what
this project so far could only estimate with a hash.

Whitelists transport fields; no personal data is stored.

Network is only needed at data-import time. Reference date is a Thursday matching the catalogue
snapshot, and four windows are enough: measured at Avenida Jiménez, they cover every service the
catalogue lists for the station.
"""
import hashlib
import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CREDENTIAL = ROOT / 'tools/en_vivo.local.json'

def settings():
    """Direcciones y cabeceras del servicio, desde el archivo local que no se versiona."""
    if not CREDENTIAL.exists():
        raise SystemExit('Falta tools/en_vivo.local.json con la configuración del servicio.')
    return json.loads(CREDENTIAL.read_text())

REFERENCE_DATE = '2026-09-10'
WINDOWS = ['05:30', '08:00', '12:00', '16:00', '20:00']
DURATION = 180
# El tablero devuelve las próximas N salidas, no un muestreo de la ventana: con 60 una estación
# concurrida solo enseña doce minutos y la mitad de sus servicios se pierde. Con 300 cubre cerca de
# una hora, sin pedir más peticiones.
MAX_JOURNEYS = 300
PAUSE = 0.6
FIELDS = ['line', 'lineId', 'num', 'operator', 'operatorCode', 'date', 'time', 'destination',
          'destinationMainMastName', 'originMainMastName', 'stop', 'stopmain', 'stopExtId', 'stopCode']

def now():
    return datetime.now(timezone.utc).isoformat()

def board(station_id, window):
    body = {'id': station_id, 'date': REFERENCE_DATE, 'time': window, 'maxJourneys': MAX_JOURNEYS,
            'duration': DURATION, 'rtMode': 'SERVER_DEFAULT', 'type': 'DEP_STATION'}
    cfg = settings()
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json',
               'User-Agent': 'BogotaTransmi-local-research/0.2'}
    if cfg.get('planner_origin'):
        headers['Origin'] = cfg['planner_origin']
    request = urllib.request.Request(cfg['planner_board_url'], data=json.dumps(body).encode(),
                                     method='POST', headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read()
    return json.loads(raw).get('data') or [], hashlib.sha256(raw).hexdigest()

def save(path, data):
    payload = (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode()
    path.write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()

def main():
    services = json.loads((ROOT / 'app/dist/services.json').read_text())
    stations = [s for s in services['stations'] if s['kind'] == 'station']
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    folder = ROOT / 'data/raw/station_departures' / stamp
    folder.mkdir(parents=True, exist_ok=False)
    boards, failures, responses = {}, [], 0
    for index, station in enumerate(stations, 1):
        # El identificador de estación del proyecto es el mismo del planificador; el que no lo sea
        # responde 400 y se anota como pendiente en vez de buscarle un equivalente por cercanía.
        departures, seen = [], set()
        for window in WINDOWS:
            try:
                data, digest = board(station['id'], window)
            except urllib.error.HTTPError as error:
                failures.append({'station_id': station['id'], 'name': station['name'],
                                 'window': window, 'status': error.code})
                break
            except (urllib.error.URLError, TimeoutError, ValueError, OSError) as error:
                failures.append({'station_id': station['id'], 'name': station['name'],
                                 'window': window, 'error': str(error)})
                continue
            responses += 1
            for entry in data:
                key = (entry.get('line'), entry.get('destinationMainMastName'), entry.get('stop'))
                if key in seen:
                    continue
                seen.add(key)
                departures.append({k: entry.get(k) for k in FIELDS})
            time.sleep(PAUSE)
        if departures:
            boards[station['id']] = {'name': station['name'], 'departures': departures}
        print(f"[{index}/{len(stations)}] {station['id']:>6} {station['name'][:34]:34} "
              f"{len(departures):3d} salidas distintas", flush=True)
    digest = save(folder / 'boards.json', {'reference_date': REFERENCE_DATE, 'windows': WINDOWS,
                                           'duration_min': DURATION, 'stations': boards})
    save(folder / 'manifest.json', {
        'schema_version': 1, 'snapshot': stamp, 'source': 'servicio configurado localmente',
        'queried_at': now(), 'reference_date': REFERENCE_DATE, 'windows': WINDOWS,
        'duration_min': DURATION, 'max_journeys': MAX_JOURNEYS,
        'stations_requested': len(stations), 'stations_with_board': len(boards),
        'responses': responses, 'failures': failures, 'raw_file': 'boards.json', 'raw_sha256': digest,
        'license': 'Horarios publicados por TRANSMILENIO S.A. a través del planificador de MaaS; '
                   'servicio sin condiciones de uso publicadas. Solo campos de transporte.'})
    save(ROOT / 'data/raw/station_departures/latest.json', {'snapshot': stamp})
    print(f'STATION_DEPARTURES {len(boards)}/{len(stations)} estaciones · {responses} respuestas · '
          f'{len(failures)} fallos · {folder}')

if __name__ == '__main__':
    main()
