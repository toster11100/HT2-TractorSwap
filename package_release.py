"""Package only the byte-verified 1.1.4 ASI and player instructions."""
import hashlib
import json
from pathlib import Path
import zipfile

import build

VERSION='1.1.4'
PUBLISHED_ASI_SHA256='aa33d60d8601ebb372f8c20c3d43945014ffc95b479ccdfb8f88fbf665fb0711'


def package():
    here=Path(__file__).resolve().parent
    image=build.build()
    digest=hashlib.sha256(image).hexdigest()
    if digest!=PUBLISHED_ASI_SHA256:
        raise RuntimeError(
            f'Reproducible build differs from the published ASI: {digest}')
    output=here/'build-output'
    package_dir=output/'package'
    files={
        'plugins/HT2_TractorSwap.asi':image,
        'README.txt':(here/'README.txt').read_bytes(),
    }
    for name,payload in files.items():
        target=package_dir/name
        target.parent.mkdir(parents=True,exist_ok=True)
        if not target.exists() or target.read_bytes()!=payload:
            target.write_bytes(payload)
    archive=output/f'HT2_TractorSwap_{VERSION}.zip'
    if archive.exists():
        with zipfile.ZipFile(archive) as existing:
            if set(existing.namelist())!=set(files) or any(
                    existing.read(name)!=payload for name,payload in files.items()):
                raise RuntimeError(f'Existing archive differs; preserve it: {archive}')
    else:
        with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as bundle:
            for name,payload in files.items():
                entry=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0))
                entry.compress_type=zipfile.ZIP_DEFLATED
                bundle.writestr(entry,payload)
    with zipfile.ZipFile(archive) as saved:
        if saved.testzip() is not None or set(saved.namelist())!=set(files):
            raise RuntimeError(f'Invalid player archive: {archive}')
        for name,payload in files.items():
            if saved.read(name)!=payload:
                raise RuntimeError(f'Archive payload mismatch: {name}')
    manifest={
        'version':VERSION,
        'archive':archive.name,
        'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
        'published_asi_sha256':digest,
        'files':{name:hashlib.sha256(payload).hexdigest()
                 for name,payload in files.items()},
        'published':False,
    }
    (output/'package_manifest.json').write_text(
        json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(manifest,indent=2))
    return manifest


if __name__=='__main__':
    package()
