"""Live vehicle positions, read from services configured locally and projected to the frame.

Where the readings come from is not part of this repository: the addresses and the credential
live in tools/en_vivo.local.json, which is not versioned. Without that file nothing is requested
and the tab says so. Services answer only to requests that do not carry a browser Origin, or that
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
BOGOTA = ZoneInfo('America/Bogota')
CACHE_TTL = 15.0
MIN_INTERVAL = 2.0
# Instantánea de toda la red, de otro servicio: el planificador que la app incorpora en su sección
# de viajes. Responde por recuadro geográfico y devuelve exactamente el máximo que se le pida, así
# que un resultado del tamaño del tope significa que truncó y hay que repartirlo en cuadrantes.
BOGOTA_BBOX = {'llLat': 4.45, 'llLon': -74.25, 'urLat': 4.85, 'urLon': -73.99}
MAX_JOURNEYS = 1000
TRUNK_OPERATORS = ('Transmilenio-Troncal', 'Transmilenio-Dual')
NETWORK_TTL = 45.0
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

def quadrants(box):
    """The box split in four. Each vehicle is one point, so it falls in exactly one piece."""
    mid_lat = (box['llLat'] + box['urLat']) / 2
    mid_lon = (box['llLon'] + box['urLon']) / 2
    return [{'llLat': lower, 'llLon': left, 'urLat': upper, 'urLon': right}
            for lower, upper in ((box['llLat'], mid_lat), (mid_lat, box['urLat']))
            for left, right in ((box['llLon'], mid_lon), (mid_lon, box['urLon']))]

class LiveBuses:
    """Ask the configured service for one route at a time, cached and rate limited."""

    def __init__(self, services=SERVICES):
        self.services = services
        self.lock = threading.Lock()
        self.cache = {}
        self.last_call = 0.0
        self._catalogue = None
        self.network_lock = threading.Lock()
        self.network_cache = None

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

    def status(self):
        codes, _ = self.catalogue()
        return {'available': True, 'configured': self.configured(), 'codes': codes,
                'interval_s': 20, 'attribution': ATTRIBUTION}

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

    def network(self):
        """(status, payload) with every trunk and dual vehicle the planner places right now.

        One request covers Bogotá. If it comes back exactly at the cap it truncated, so the box is
        split into quadrants and the pieces are merged by journey reference. Zonal and feeder
        vehicles are dropped here: the simulator does not model them.
        """
        _, origin = self.catalogue()
        cached = self.network_cache
        if cached and time.time() - cached['fetched'] < NETWORK_TTL:
            return 'ok', self.network_payload(cached)
        with self.network_lock:
            cached = self.network_cache
            if cached and time.time() - cached['fetched'] < NETWORK_TTL:
                return 'ok', self.network_payload(cached)
            try:
                raw = self.journeys(BOGOTA_BBOX)
                truncated = len(raw) >= MAX_JOURNEYS
                boxes = 1
                if truncated:
                    # Un cuadrante que vuelva a venir en el tope sigue truncando, y se dice.
                    merged, truncated = {}, False
                    for box in quadrants(BOGOTA_BBOX):
                        piece = self.journeys(box)
                        truncated = truncated or len(piece) >= MAX_JOURNEYS
                        for journey in piece:
                            merged[journey.get('journeyDetailRef') or repr(journey)] = journey
                        boxes += 1
                    raw = list(merged.values())
            except urllib.error.HTTPError as error:
                return 'upstream', {'detail': f'El planificador respondió {error.code}.', 'code': error.code}
            except (urllib.error.URLError, TimeoutError, ValueError, OSError) as error:
                return 'upstream', {'detail': f'No se pudo consultar el planificador: {error}', 'code': None}
            now = datetime.now(BOGOTA)
            vehicles = [v for v in (self.vehicle(j, origin) for j in raw if j.get('operator') in TRUNK_OPERATORS) if v]
            cached = {'fetched': time.time(), 'queried_at': now.isoformat(timespec='seconds'),
                      'vehicles': vehicles, 'seen': len(raw), 'boxes': boxes, 'truncated': truncated}
            self.network_cache = cached
            return 'ok', self.network_payload(cached)

    def journeys(self, box):
        body = {**box, 'maxJny': str(MAX_JOURNEYS), 'positionMode': 'CALC_REPORT'}
        settings = self.settings()
        url = settings.get('planner_positions_url')
        if not url:
            raise ValueError('Falta la dirección del servicio en la configuración local.')
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        if settings.get('planner_origin'):
            headers['Origin'] = settings['planner_origin']
        request = urllib.request.Request(url, data=json.dumps(body).encode(), method='POST', headers=headers)
        with urllib.request.urlopen(request, timeout=40) as response:
            payload = json.loads(response.read(40_000_000))
        return payload.get('data') or []

    def vehicle(self, journey, origin):
        """One planner vehicle, without the timetable it carries: the page only draws the position."""
        try:
            lon, lat = float(journey['lon']), float(journey['lat'])
        except (KeyError, TypeError, ValueError):
            return None
        if not (-75.5 < lon < -73 and 3.5 < lat < 5.5):
            return None
        x, y = aeqd(lon, lat, origin)
        stops = journey.get('stops') or []
        return {'id': journey.get('journeyDetailRef') or '', 'line': str(journey.get('line') or '').strip(),
                'line_id': journey.get('lineId'), 'operator': journey.get('operator'),
                'destination': str((stops[-1] if stops else {}).get('name') or '').strip(),
                'xy': [round(x, 2), round(y, 2)], 'lonlat': [lon, lat]}

    def network_payload(self, cached):
        return {'queried_at': cached['queried_at'], 'age_s': round(time.time() - cached['fetched'], 1),
                'vehicles': cached['vehicles'], 'seen': cached['seen'], 'boxes': cached['boxes'],
                'truncated': cached['truncated'], 'cap': MAX_JOURNEYS,
                'attribution': ATTRIBUTION}

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
