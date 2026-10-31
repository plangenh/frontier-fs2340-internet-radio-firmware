"""Conservative checks for the curated public files, not a general secret scanner."""
from pathlib import Path
import re, subprocess
ROOT=Path(__file__).resolve().parents[1]
SUFFIXES={'.bin','.isu','.sap','.har','.pcap','.pcapng','.heic','.tar','.zip','.elf','.sqlite','.db','.png','.jpg','.jpeg','.pdf'}
PATTERNS={
 'local user path': re.compile(r'/(?:Users|home)/[A-Za-z0-9_.-]+/'),
 'private IPv4': re.compile(r'\b(?:192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b'),
 'MAC address': re.compile(r'\b(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\b'),
 'GitHub token': re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b'),
 'private key': re.compile(r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----'),
}
def files():
    paths={p for p in ROOT.rglob('*') if p.is_file() and not any(x in {'.git','__pycache__','.venv','private','output','artifacts'} for x in p.relative_to(ROOT).parts)}
    # Scan tracked ignored files too: ignore rules are not a publication boundary.
    result=subprocess.run(['git','-C',str(ROOT),'ls-files','-z'],capture_output=True)
    if result.returncode==0:
        paths.update(ROOT/p for p in result.stdout.decode().split('\0') if p and (ROOT/p).is_file())
    return sorted(paths)
def main():
    errors=[];scanned=files()
    for p in scanned:
        rel=p.relative_to(ROOT)
        if p.suffix.lower() in SUFFIXES or rel.parts[0] in {'private','output','artifacts'}:errors.append(f'{rel}: prohibited artifact')
        try:text=p.read_text(encoding='utf-8')
        except UnicodeError:errors.append(f'{rel}: non-text file requires review');continue
        if p.stat().st_size>1_000_000:errors.append(f'{rel}: unexpected large file')
        for label,pattern in PATTERNS.items():
            if pattern.search(text):errors.append(f'{rel}: {label} candidate')
    if errors:
        print('\n'.join(errors));raise SystemExit(1)
    print(f'Publication checks passed for {len(scanned)} files. Human review still required for new content.')
if __name__=='__main__':main()
