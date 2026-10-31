"""Offline display resource extraction; input is existing parent manifest/memory.

The resource structure is derived from consecutive valid bytes and visual checks.
No firmware execution or device access. Writes only within this script directory.
"""
from pathlib import Path
import json, struct
import argparse
parser=argparse.ArgumentParser(description='Extract private language tables from a locally extracted original firmware.')
parser.add_argument('manifest',type=Path)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
PARENT=args.manifest.resolve().parent
ROOT=args.output.resolve()
ROOT.mkdir(parents=True,exist_ok=False)
manifest=json.loads(args.manifest.read_text())
if manifest['sha256']!='48a9da85d2580ee7fffde0f204ee2046ae0e300a2f23f1e4a6a5e3b299bd0dc3': raise ValueError('Unsupported original')
module=next(m for m in manifest['modules'] if m['name']=='meta_t1.elf')
images=[(i['address'],(PARENT/i['file']).read_bytes()) for i in module['images']]
fills=module['fills']
def read(address,size):
    address &= 0x7fffffff
    out=bytearray()
    while len(out)<size:
        a=address+len(out)
        for p,b in images:
            if p<=a<p+len(b):
                count=min(size-len(out),p+len(b)-a)
                out.extend(b[a-p:a-p+count]);break
        else:
            for f in fills:
                if f['address']<=a<f['address']+f['size'] and f['value']==0:
                    count=min(size-len(out),f['address']+f['size']-a)
                    out.extend(bytes(count));break
            else:raise ValueError(f'Unmapped byte {a:08x}')
    return bytes(out)
def string(address):
    address &= 0x7fffffff
    for p,b in images:
        if p<=address<p+len(b):
            begin=address-p;end=b.find(b'\0',begin)
            if end<0:raise ValueError('Unterminated string')
            return b[begin:end].decode('utf-8')
    if read(address,1)==b'\0':return ''
    raise ValueError(f'Non-string pointer {address:x}')
locale_names=['English','Czech','Danish','Dutch','Finnish','French','German','Italian','Norwegian','Polish','Portuguese','Slovak','Spanish','Swedish','Turkish']
roots=struct.unpack('<15I',read(0x32b12b58,60))
locales=[]
for language,root in zip(locale_names,roots):
    entries=[]
    for n in range(1056):
        pointer=struct.unpack('<I',read(root+n*4,4))[0]
        entries.append(dict(id=n,text=string(pointer),string_address=pointer&0x7fffffff,pointer_address=(root&0x7fffffff)+4*n))
    # Exactly 1056 string pointers, followed by a non-string pointer/value.
    next_word=struct.unpack('<I',read(root+1056*4,4))[0]
    locales.append(dict(language_inferred_from_text=language,table_address=root&0x7fffffff,entry_count=1056,next_word=next_word,entries=entries))
(ROOT/'locales_complete.json').write_text(json.dumps(locales,indent=2,ensure_ascii=False)+'\n')

print('Extracted 15 private language tables; 15,840 entries. Never publish this output without review.')
