"""Fetch a pinned official npm tarball; only copy the three required public files."""
import base64
import hashlib
import io
import json
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = '0.186.0'
URL = f'https://registry.npmjs.org/three/-/three-{VERSION}.tgz'
INTEGRITY = 'cr/fIM2ddMSVbYVgkfD4jLJv7Fh/8ZTjvo+7gQeSVGUZHxpx9FDwoL5iC7hUz/LiRA8wMbqfnb90xKfm1/HHkQ=='


def main():
    archive = urllib.request.urlopen(URL, timeout=90).read()
    if base64.b64encode(hashlib.sha512(archive).digest()).decode() != INTEGRITY:
        raise ValueError('npm tarball integrity mismatch')
    folder = ROOT / 'app/dist/vendor'
    folder.mkdir(parents=True, exist_ok=True)
    hashes = {}
    with tarfile.open(fileobj=io.BytesIO(archive), mode='r:gz') as tar:
        for source, name in [('package/build/three.module.js', 'three.module.js'),
                             ('package/build/three.core.js', 'three.core.js'),
                             ('package/LICENSE', 'THREE-LICENSE.txt')]:
            payload = tar.extractfile(source).read()
            (folder / name).write_bytes(payload)
            hashes[name] = hashlib.sha256(payload).hexdigest()
    (folder / 'manifest.json').write_text(json.dumps({'package': 'three', 'version': VERSION,
        'source': URL, 'license': 'MIT', 'archive_integrity': 'sha512-'+INTEGRITY,
        'sha256': hashes}, indent=2)+'\n')
    print('THREE_VENDORED', VERSION)

if __name__ == '__main__':
    main()
