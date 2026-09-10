"""Loopback-only local player. Serves only authored public assets, never the repo."""
import argparse
import functools
import http.server
import json
import threading
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT/'app/dist'
PORT = 8766
URL = f'http://127.0.0.1:{PORT}/'


def main():
    parser=argparse.ArgumentParser(description='Simulación local Transmi 2D')
    parser.add_argument('--open',action='store_true',help='Abrir el navegador predeterminado')
    args=parser.parse_args()
    try:
        server=http.server.ThreadingHTTPServer(('127.0.0.1',PORT),functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(DIRECTORY)))
    except OSError as error:
        # Reuse this same app only; do not scan ports or terminate another process.
        try:
            with urllib.request.urlopen(URL+'network.json',timeout=2) as response:
                current=json.loads(response.read(2_000_000))
            expected=json.loads((DIRECTORY/'network.json').read_text())
            if current.get('revision')!=expected['revision'] or current.get('source_sha256')!=expected['source_sha256']:
                raise ValueError('Different server')
        except Exception:
            raise SystemExit(f'El puerto {PORT} está ocupado por otra aplicación. Cierra esa aplicación y vuelve a abrir la prueba. {error}')
        print('Transmi 2D ya está abierto: '+URL)
        if args.open:
            webbrowser.open(URL)
        return
    print('Transmi 2D: '+URL,flush=True)
    print('Prueba local sin conexión externa. Mantén esta ventana abierta; Ctrl+C cierra el servidor.',flush=True)
    if args.open:
        threading.Timer(.3,lambda:webbrowser.open(URL)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__=='__main__':
    main()
