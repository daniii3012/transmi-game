"""Serve only public simulator assets: loopback by default, optional explicit LAN.

It also answers /api/en-vivo, the only dynamic part of the simulator: a published page cannot make
those readings itself. That extra exists only while this server runs and only when the local
configuration is present; what gets published is static, and the panel says so there.
"""
import argparse
import functools
import http.server
import json
import socket
import threading
import urllib.parse
import urllib.request
import webbrowser
from pathlib import Path

from live_buses import LiveBuses

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'app/dist'
LIVE = LiveBuses()

class LocalHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def list_directory(self, path):
        self.send_error(404, 'Not found')
        return None

    def do_GET(self):
        if urllib.parse.urlsplit(self.path).path.startswith('/api/'):
            return self.live()
        return super().do_GET()

    def live(self):
        url = urllib.parse.urlsplit(self.path)
        query = urllib.parse.parse_qs(url.query)
        try:
            if url.path == '/api/en-vivo/estado':
                return self.json(200, LIVE.status())
            if url.path == '/api/en-vivo/red':
                state, payload = LIVE.network()
            elif url.path == '/api/en-vivo/buses':
                code = (query.get('ruta') or [''])[0].strip().upper()[:8]
                state, payload = LIVE.buses(code)
            elif url.path == '/api/en-vivo/estacion':
                station = (query.get('id') or [''])[0].strip()[:32]
                state, payload = LIVE.departures(station)
            else:
                return self.json(404, {'error': 'unknown_endpoint'})
        except Exception as error:  # Un fallo aquí no puede tumbar el simulador entero.
            return self.json(500, {'error': 'server', 'detail': str(error)})
        if state == 'ok':
            return self.json(200, payload)
        if state == 'unknown_route':
            return self.json(404, {'error': state, 'detail': 'Esa ruta no está en el catálogo del simulador.'})
        if state == 'unknown_station':
            return self.json(404, {'error': state, 'detail': 'Esta estación no tiene tablero publicado.'})
        if state == 'not_configured':
            return self.json(503, {'error': state, 'detail': 'Falta la configuración local del servicio.'})
        return self.json(502, {'error': 'upstream', **payload})

    def json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

def lan_address():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as connection:
            # A connect without send discovers the selected interface; no packet payload.
            connection.connect(('192.0.2.1', 9))
            return connection.getsockname()[0]
    except OSError:
        return socket.gethostname() + '.local'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--open', action='store_true')
    parser.add_argument('--lan', action='store_true', help='Permitir acceso desde la red local por el puerto 8767')
    args = parser.parse_args()
    port = 8767 if args.lan else 8766
    host = '0.0.0.0' if args.lan else '127.0.0.1'
    local_url = f'http://127.0.0.1:{port}/'
    player_url = f'http://{lan_address()}:{port}/' if args.lan else local_url
    try:
        server = http.server.ThreadingHTTPServer((host, port), functools.partial(LocalHandler, directory=str(DIRECTORY)))
    except OSError as error:
        try:
            with urllib.request.urlopen(local_url + 'services.json', timeout=2) as response:
                current = json.loads(response.read(20_000_000))
            expected = json.loads((DIRECTORY / 'services.json').read_text())
            if current.get('revision') != expected['revision'] or current.get('source_hashes') != expected['source_hashes']:
                raise ValueError('Different server')
        except Exception:
            raise SystemExit(f'El puerto {port} está ocupado por otra aplicación. {error}')
        print('Transmi ya está abierto: ' + player_url)
        if args.open:
            webbrowser.open(local_url)
        return
    print('Transmi 2D: ' + player_url, flush=True)
    if args.lan:
        print('Abre esa dirección desde otro dispositivo de la misma red. Cada dispositivo tiene su propio escenario.', flush=True)
    print('Mantén esta Terminal abierta; Ctrl+C cierra este servidor.', flush=True)
    if args.open:
        threading.Timer(.3, lambda: webbrowser.open(local_url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == '__main__':
    main()
