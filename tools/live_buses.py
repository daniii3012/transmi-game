"""Live vehicles of one service, read from a service configured locally and projected to the frame.

Only the per-service view lives here. The snapshot of the whole network moved to live_network.py,
which reads the published realtime feed: open data, no credential, and it cannot truncate. What
this module still adds over that feed is what the feed does not carry —occupancy, accessibility and
how far along its route a bus is— for one service at a time.

Where these readings come from is not part of this repository: the addresses and the credential live
in tools/en_vivo.local.json, which is not versioned. Without that file nothing is requested and the
tab says so, while the network-wide view keeps working on its own. Services answer only to requests that do not carry a browser Origin, or that
carry one they expect, so the page cannot call them and this proxy exists for that reason.

Only the standard library, because the simulator is served by the system Python; the projection
is reimplemented here to stay identical to the pyproj definition in geo.py.
"""
import json
import math
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
SERVICES = ROOT / 'app/dist/services.json'
CREDENTIAL = ROOT / 'tools/en_vivo.local.json'
# Todo lo que identifica a los servicios está en la configuración local, nunca aquí.
ATTRIBUTION = 'Lectura de un servicio configurado localmente'
# La instantánea de toda la red no sale de ahí, y sí se puede nombrar: es dato abierto publicado.
NETWORK_ATTRIBUTION = 'GTFS-Realtime de TRANSMILENIO S.A., datos abiertos'
BOGOTA = ZoneInfo('America/Bogota')
CACHE_TTL = 15.0
MIN_INTERVAL = 2.0
# El tablero de una estación cambia minuto a minuto; 25 s lo mantiene fresco sin repetir la
# consulta cada vez que se vuelve a dibujar la ficha. Doce salidas cubren de sobra lo que cabe
# en el panel.
BOARD_TTL = 25.0
BOARD_JOURNEYS = 12
TIMEOUT = 12.0  # Rechazar una ruta le toma al servicio hasta diez segundos; cortar antes esconde el motivo.

def aeqd(lon, lat, origin):
    """Azimuthal equidistant metres from origin on the WGS84 ellipsoid, as in geo.py.

    Ellipsoidal AEQD is the geodesic distance and azimuth from the origin read as polar
    coordinates, so Vincenty's inverse gives exactly what pyproj gives: the spherical
    shortcut drifts more than eighty metres over Suba and would put buses off the busway.
    """
    a, f = 6378137.0, 1 / 298.257223563
    b = (1 - f) * a
    L = math.radians(lon - origin[0])
    U1, U2 = math.atan((1 - f) * math.tan(math.radians(origin[1]))), math.atan((1 - f) * math.tan(math.radians(lat)))
    sU1, cU1, sU2, cU2 = math.sin(U1), math.cos(U1), math.sin(U2), math.cos(U2)
    lam, sin_sigma, cos_sigma, sigma, cos2_alpha, cos_2sm = L, 0.0, 1.0, 0.0, 1.0, 0.0
    for _ in range(200):
        sin_lam, cos_lam = math.sin(lam), math.cos(lam)
        sin_sigma = math.hypot(cU2 * sin_lam, cU1 * sU2 - sU1 * cU2 * cos_lam)
        if sin_sigma == 0:
            return (0.0, 0.0)
        cos_sigma = sU1 * sU2 + cU1 * cU2 * cos_lam
        sigma = math.atan2(sin_sigma, cos_sigma)
        sin_alpha = cU1 * cU2 * sin_lam / sin_sigma
        cos2_alpha = 1 - sin_alpha * sin_alpha
        cos_2sm = cos_sigma - 2 * sU1 * sU2 / cos2_alpha if cos2_alpha else 0.0
        C = f / 16 * cos2_alpha * (4 + f * (4 - 3 * cos2_alpha))
        previous, lam = lam, L + (1 - C) * f * sin_alpha * (sigma + C * sin_sigma * (cos_2sm + C * cos_sigma * (-1 + 2 * cos_2sm ** 2)))
        if abs(lam - previous) < 1e-12:
            break
    u2 = cos2_alpha * (a * a - b * b) / (b * b)
    A = 1 + u2 / 16384 * (4096 + u2 * (-768 + u2 * (320 - 175 * u2)))
    B = u2 / 1024 * (256 + u2 * (-128 + u2 * (74 - 47 * u2)))
    delta = B * sin_sigma * (cos_2sm + B / 4 * (cos_sigma * (-1 + 2 * cos_2sm ** 2) - B / 6 * cos_2sm * (-3 + 4 * sin_sigma ** 2) * (-3 + 4 * cos_2sm ** 2)))
    distance = b * A * (sigma - delta)
    azimuth = math.atan2(cU2 * math.sin(lam), cU1 * sU2 - sU1 * cU2 * math.cos(lam))
    return (distance * math.sin(azimuth), distance * math.cos(azimuth))

def reported_age(lasttime, now):
    """Seconds between the GPS report and Bogotá's clock, or None when the stamp is unusable."""
    try:
        stamp = datetime.strptime(str(lasttime).strip(), '%I:%M:%S %p')
    except (ValueError, TypeError):
        return None
    age = (now.hour * 3600 + now.minute * 60 + now.second) - (stamp.hour * 3600 + stamp.minute * 60 + stamp.second)
    if age < -60:
        age += 86400  # Lectura de ayer leída después de medianoche.
    return max(0, age)

def normalise(entry, origin, now):
    """One upstream bus as the simulator uses it, or None when its position is unusable."""
    try:
        lon, lat = float(entry['longitude']), float(entry['latitude'])
    except (KeyError, TypeError, ValueError):
        return None
    if not (-75.5 < lon < -73 and 3.5 < lat < 5.5):
        return None  # Fuera de Bogotá y su sabana: no se dibuja una coordenada que no se entiende.
    x, y = aeqd(lon, lat, origin)
    return {
        'id': str(entry.get('id') or ''),
        'label': str(entry.get('label') or '').strip(),
        'xy': [round(x, 2), round(y, 2)],
        'lonlat': [lon, lat],
        'heading': float(entry.get('angulo') or 0),
        'destination': str(entry.get('destino_limpio') or '').strip(),
        'occupancy': str(entry.get('ocupacion_bus') or '').strip(),
        'accessibility': str(entry.get('accesibilidad') or '').strip(),
        'route_id': entry.get('route_id'),
        'travelled_m': entry.get('posicion'),
        'reported': str(entry.get('lasttime') or '').strip(),
        'reported_age_s': reported_age(entry.get('lasttime'), now),
    }

class LiveBuses:
    """Ask the configured service for one route at a time, cached and rate limited."""

    def __init__(self, services=SERVICES):
        self.services = services
        self.lock = threading.Lock()
        self.cache = {}
        self.last_call = 0.0
        self._catalogue = None
        self._stations = None
        self.board_lock = threading.Lock()
        self.boards = {}

    def catalogue(self):
        """Route codes and projection origin, read from the same services.json the page loads."""
        if self._catalogue is None:
            data = json.loads(self.services.read_text())
            codes = sorted({r['code'] for r in data['routes'] if r.get('ready')}, key=lambda c: (len(c), c))
            self._catalogue = (codes, tuple(data['origin_lon_lat']))
        return self._catalogue

    def settings(self):
        """Addresses, headers and credential, all from the untracked local file. Never committed.

        Missing or incomplete, every live call reports itself unconfigured and asks for nothing.
        """
        if not CREDENTIAL.exists():
            return {}
        try:
            return json.loads(CREDENTIAL.read_text())
        except (ValueError, OSError):
            return {}

    def configured(self):
        s = self.settings()
        return bool(s.get('appid') and s.get('buses_url'))

    def status(self, network_ready=False):
        """Qué puede responder este servidor. La red y el seguimiento por servicio son independientes:
        la primera sale de datos abiertos y la segunda de la configuración local, así que la página
        tiene que poder ofrecer una sin la otra."""
        codes, _ = self.catalogue()
        return {'available': True, 'configured': self.configured(), 'network': bool(network_ready),
                'codes': codes, 'interval_s': 20, 'attribution': ATTRIBUTION,
                'network_attribution': NETWORK_ATTRIBUTION}

    def buses(self, code):
        """(status, payload) for one route code. Status is ok, unknown_route, not_configured or upstream."""
        codes, origin = self.catalogue()
        if code not in codes:
            return 'unknown_route', None
        if not self.configured():
            return 'not_configured', None
        # La caché se mira antes del candado: una ruta ya leída no espera detrás de la consulta
        # de otra, que puede tardar segundos.
        cached = self.cache.get(code)
        if cached and time.time() - cached['fetched'] < CACHE_TTL:
            return 'ok', self.payload(code, cached)
        with self.lock:
            cached = self.cache.get(code)
            if cached and time.time() - cached['fetched'] < CACHE_TTL:
                return 'ok', self.payload(code, cached)
            wait = MIN_INTERVAL - (time.time() - self.last_call)
            if wait > 0:
                # Un piso entre llamadas: varias pestañas o dispositivos no multiplican la carga.
                if cached:
                    return 'ok', self.payload(code, cached)
                time.sleep(min(wait, MIN_INTERVAL))
            try:
                raw = self.request(code)
            except urllib.error.HTTPError as error:
                self.last_call = time.time()
                # El 400 no distingue entre una ruta que no existe y una que no está operando:
                # fuera de horario todas responden así. No se afirma cuál de las dos es.
                detail = ('El servicio no está entregando datos de esta ruta ahora. Puede estar fuera de su '
                          'horario de operación.') if error.code == 400 else f'El servicio respondió {error.code}.'
                return 'upstream', {'detail': detail, 'code': error.code}
            except (urllib.error.URLError, TimeoutError, ValueError, OSError) as error:
                self.last_call = time.time()
                return 'upstream', {'detail': f'No se pudo consultar el servicio: {error}', 'code': None}
            self.last_call = time.time()
            now = datetime.now(BOGOTA)
            buses = [b for b in (normalise(e, origin, now) for e in raw) if b]
            cached = {'fetched': time.time(), 'queried_at': now.isoformat(timespec='seconds'), 'buses': buses,
                      'discarded': len(raw) - len(buses)}
            self.cache[code] = cached
            return 'ok', self.payload(code, cached)

    def stations(self):
        """Los identificadores de estación del catálogo, para no consultar por uno inventado."""
        if self._stations is None:
            data = json.loads(self.services.read_text())
            self._stations = {s['id']: s['name'] for s in data['stations'] if s['kind'] == 'station'}
        return self._stations

    def departures(self, station_id):
        """(status, payload) with the next departures published for one station.

        This is what the operator plans for the coming minutes, not a GPS reading: the board gives
        an hour and a boarding point, nothing that was measured on the street. The wait is worked
        out against Bogota's clock and everything else is passed through as it arrives.
        """
        names = self.stations()
        if station_id not in names:
            return 'unknown_station', None
        if not self.configured():
            return 'not_configured', None
        cached = self.boards.get(station_id)
        if cached and time.time() - cached['fetched'] < BOARD_TTL:
            return 'ok', self.board_payload(station_id, cached)
        with self.board_lock:
            cached = self.boards.get(station_id)
            if cached and time.time() - cached['fetched'] < BOARD_TTL:
                return 'ok', self.board_payload(station_id, cached)
            try:
                raw = self.board_request(station_id)
            except urllib.error.HTTPError as error:
                # 400 es la respuesta a un identificador que el tablero no reconoce, no un fallo.
                if error.code == 400:
                    return 'unknown_station', None
                return 'upstream', {'detail': f'El tablero respondió {error.code}.', 'code': error.code}
            except (urllib.error.URLError, TimeoutError, ValueError, OSError) as error:
                return 'upstream', {'detail': f'No se pudo leer el tablero: {error}.'}
            now = datetime.now(BOGOTA)
            cached = {'fetched': time.time(), 'queried_at': now.isoformat(),
                      'departures': [d for d in (self.departure(entry, now) for entry in raw) if d]}

            self.boards[station_id] = cached
        return 'ok', self.board_payload(station_id, cached)

    def departure(self, entry, now):
        """One board line, or None when it carries no usable hour."""
        stamp = f"{entry.get('date') or now.date().isoformat()} {(entry.get('time') or '')[:8]}"
        try:
            when = datetime.strptime(stamp, '%Y-%m-%d %H:%M:%S').replace(tzinfo=BOGOTA)
        except ValueError:
            return None
        return {'line': str(entry.get('line') or '').strip(),
                'destination': str(entry.get('destinationMainMastName') or '').strip(),
                'stop': str(entry.get('stop') or '').strip(),
                'at': when.isoformat(),
                'time': when.strftime('%H:%M'),
                'started': bool(entry.get('hasStarted'))}

    def board_request(self, station_id):
        settings = self.settings()
        url = settings.get('planner_board_url')
        if not url:
            raise ValueError('Falta la dirección del tablero en la configuración local.')
        now = datetime.now(BOGOTA)
        body = {'id': station_id, 'date': now.strftime('%Y-%m-%d'), 'time': now.strftime('%H:%M'),
                'maxJourneys': BOARD_JOURNEYS, 'duration': 60, 'rtMode': 'SERVER_DEFAULT',
                'type': 'DEP_STATION'}
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        if settings.get('planner_origin'):
            headers['Origin'] = settings['planner_origin']
        request = urllib.request.Request(url, data=json.dumps(body).encode(), method='POST', headers=headers)
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            payload = json.loads(response.read(4_000_000))
        return payload.get('data') or []

    def board_payload(self, station_id, cached):
        """La espera se calcula al servir y no al leer: el tablero se guarda unos segundos y su
        hora es de minuto entero, así que se compara minuto contra minuto —una salida del minuto
        en curso es «ahora», no «hace un minuto»— y no contra el segundo exacto.
        """
        minute = datetime.now(BOGOTA).replace(second=0, microsecond=0)
        departures = []
        for entry in cached['departures']:
            wait = round((datetime.fromisoformat(entry['at']) - minute).total_seconds() / 60)
            if wait < 0:
                continue
            departures.append({k: v for k, v in entry.items() if k != 'at'} | {'in_min': wait})
        return {'station_id': station_id, 'name': self.stations().get(station_id, ''),
                'queried_at': cached['queried_at'], 'age_s': round(time.time() - cached['fetched'], 1),
                'departures': departures, 'attribution': ATTRIBUTION}

    def request(self, code):
        settings = self.settings()
        body = json.dumps({'ruta': code}).encode()
        headers = {'Content-Type': 'application/json', 'Accept': '*/*', 'appid': settings.get('appid', '')}
        request = urllib.request.Request(settings['buses_url'], data=body, headers=headers, method='POST')
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            payload = json.loads(response.read(4_000_000))
        return payload if isinstance(payload, list) else []

    def payload(self, code, cached):
        return {'code': code, 'queried_at': cached['queried_at'], 'age_s': round(time.time() - cached['fetched'], 1),
                'buses': cached['buses'], 'discarded': cached['discarded'], 'attribution': ATTRIBUTION}
