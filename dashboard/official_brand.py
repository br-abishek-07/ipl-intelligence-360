"""Online IPL-hosted logo display with correctly attributed offline fallback.

No official logos are redistributed in this project. Remote availability is not
validated here; prefer user-supplied, permission-cleared local logos for offline demo.
"""
from pathlib import Path
import csv

BASE = 'https://documents.iplt20.com/ipl'
CODES = ('CSK','MI','RCB','KKR','SRH','RR','DC','PBKS','GT','LSG')

def official_logo_url(code: str) -> str:
    if code not in CODES:
        raise ValueError(f'Unsupported team code: {code}')
    folder = 'logos' if code == 'CSK' else 'Logos'
    return f'{BASE}/{code}/{folder}/Roundbig/{code}roundbig.png'

def local_logo_file(root: Path, code: str):
    if code not in CODES: raise ValueError(code)
    folder = root / 'assets' / 'logos' / 'official'
    for suffix in ('.png', '.webp', '.jpg', '.jpeg', '.svg'):
        p=folder / f'{code}{suffix}'
        if p.is_file(): return p
    return None

# Document not just the provider, but the exact unverified pattern.
def export_manifest(path:Path):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8') as f:
        out=csv.writer(f)
        out.writerow(['team_code','official_cdn_url','source_site','online_reachability','local_rights_status','offline_fallback'])
        for code in CODES:
            out.writerow([code,official_logo_url(code),'https://www.iplt20.com/teams','not verified in build environment','verify permission before redistribution','original decorative monogram'])
