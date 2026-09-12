"""Record how many trunk and dual vehicles are placed, every quarter hour for days.

The service consulted is the one named in tools/en_vivo.local.json, which is not versioned.
Without that file this does nothing.

The simulator dispatches on a binary rule —four minutes on a weekday between 6 and 9 and between
16 and 20, eight minutes the rest of the time and all Saturday and Sunday— and nobody has ever
measured what the system actually runs. This writes that measurement down so the rule can be
replaced by an observed curve per hour and day type instead of a guess.

Counts only. A full response carries the timetable of every vehicle and weighs about 1,3 MB; a
week of those would be half a gigabyte to answer a question about how many buses there are. Each
snapshot here is a few kilobytes: the total, the split by operator and the count per line.

Standard library only, so it runs on Windows with a plain Python install and on macOS with the
system one. Append-only: stopping it and starting it again loses nothing and repeats nothing.
"""
import argparse
import json
import socket
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOGOTA = timezone(timedelta(hours=-5))
CREDENTIAL = ROOT / 'tools/en_vivo.local.json'

def settings():
    """Direcciones y cabeceras del servicio, desde el archivo local que no se versiona."""
    if not CREDENTIAL.exists():
        raise SystemExit('Falta tools/en_vivo.local.json con la configuración del servicio.')
    return json.loads(CREDENTIAL.read_text())

BBOX = {'llLat': 4.45, 'llLon': -74.25, 'urLat': 4.85, 'urLon': -73.99}
MAX_JOURNEYS = 1000
TRUNK = ('Transmilenio-Troncal', 'Transmilenio-Dual')
TIMEOUT = 45

def quadrants(box):
    mid_lat = (box['llLat'] + box['urLat']) / 2
    mid_lon = (box['llLon'] + box['urLon']) / 2
    return [{'llLat': lo, 'llLon': le, 'urLat': up, 'urLon': ri}
            for lo, up in ((box['llLat'], mid_lat), (mid_lat, box['urLat']))
            for le, ri in ((box['llLon'], mid_lon), (mid_lon, box['urLon']))]

def journeys(box, attempts=3):
    """Una consulta, reintentando si el servicio contesta 5xx.

    Se le ha visto devolver 503 tras una ráfaga y recuperarse en menos de un minuto. En una
    captura de días, perder una lectura por eso sería tirar información sin necesidad.
    """
    body = {**box, 'maxJny': str(MAX_JOURNEYS), 'positionMode': 'CALC_REPORT'}
    cfg = settings()
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json',
               'User-Agent': 'BogotaTransmi-fleet-capture/0.1'}
    if cfg.get('planner_origin'):
        headers['Origin'] = cfg['planner_origin']
    request = urllib.request.Request(cfg['planner_positions_url'], data=json.dumps(body).encode(),
                                     method='POST', headers=headers)
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                return json.loads(response.read(60_000_000)).get('data') or []
        except urllib.error.HTTPError as error:
            if error.code < 500 or attempt == attempts - 1:
                raise
            time.sleep(20 * (attempt + 1))

def snapshot():
    """One reading. Splits into quadrants only when the flat request comes back at the cap."""
    raw = journeys(BBOX)
    truncated, boxes = len(raw) >= MAX_JOURNEYS, 1
    if truncated:
        merged, truncated = {}, False
        for box in quadrants(BBOX):
            piece = journeys(box)
            truncated = truncated or len(piece) >= MAX_JOURNEYS
            for journey in piece:
                merged[journey.get('journeyDetailRef') or repr(journey)] = journey
            boxes += 1
        raw = list(merged.values())
    trunk = [j for j in raw if j.get('operator') in TRUNK]
    now = datetime.now(BOGOTA)
    return {
        'at': now.isoformat(timespec='seconds'),
        'weekday': now.strftime('%a'),
        'hour': now.hour + now.minute / 60,
        'seen': len(raw), 'boxes': boxes, 'truncated': truncated,
        'trunk': len(trunk),
        'by_operator': dict(Counter(j.get('operator') for j in raw)),
        'by_line': dict(Counter(j.get('line') for j in trunk)),
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', default='data/raw/fleet_capture/fleet.jsonl', help='Archivo al que se añade cada lectura')
    parser.add_argument('--every', type=int, default=15, help='Minutos entre lecturas')
    parser.add_argument('--from-hour', type=float, default=6, help='Hora de Bogotá a la que empieza cada día')
    parser.add_argument('--to-hour', type=float, default=22, help='Hora de Bogotá a la que termina cada día')
    parser.add_argument('--days', type=int, default=8, help='Días que se queda corriendo')
    parser.add_argument('--once', action='store_true', help='Una sola lectura y termina, para probar')
    args = parser.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if args.once:
        reading = snapshot()
        print(json.dumps({k: reading[k] for k in ('at', 'trunk', 'seen', 'boxes', 'truncated')}, ensure_ascii=False))
        with out.open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(reading, ensure_ascii=False) + '\n')
        return

    deadline = datetime.now(BOGOTA) + timedelta(days=args.days)
    print(f'Escribiendo en {out.resolve()}', flush=True)
    print(f'Cada {args.every} min, de {args.from_hour:g} a {args.to_hour:g} hora de Bogotá, hasta {deadline:%Y-%m-%d %H:%M}.', flush=True)
    print('Ctrl+C para parar. Volver a arrancarlo continúa el mismo archivo.', flush=True)
    while datetime.now(BOGOTA) < deadline:
        now = datetime.now(BOGOTA)
        if args.from_hour <= now.hour + now.minute / 60 < args.to_hour:
            try:
                reading = snapshot()
                with out.open('a', encoding='utf-8') as handle:
                    handle.write(json.dumps(reading, ensure_ascii=False) + '\n')
                aviso = ' TRUNCADO' if reading['truncated'] else ''
                print(f"{reading['at']}  troncal+dual {reading['trunk']:4d}  de {reading['seen']:4d} en {reading['boxes']} recuadro(s){aviso}", flush=True)
            except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, socket.timeout, ValueError, OSError) as error:
                # Una lectura perdida no interrumpe la semana: se anota y se sigue.
                fallo = {'at': datetime.now(BOGOTA).isoformat(timespec='seconds'), 'error': str(error)}
                with out.open('a', encoding='utf-8') as handle:
                    handle.write(json.dumps(fallo, ensure_ascii=False) + '\n')
                print(f"{fallo['at']}  fallo: {error}", flush=True)
        # Alinear con el reloj: las lecturas caen en :00, :15, :30 y :45.
        step = args.every * 60
        time.sleep(max(5, step - (time.time() % step)))

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nDetenido. El archivo conserva todo lo leído.')
        sys.exit(0)
