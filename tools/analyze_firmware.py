"""Reproduce the offline FS2340 analysis; never executes firmware code."""
from pathlib import Path
import binascii
import collections
import hashlib
import json
import re
import struct
import zlib

from deflate_transcode import transcode
import argparse
ROOT = None
FW = None
EXPECTED = '48a9da85d2580ee7fffde0f204ee2046ae0e300a2f23f1e4a6a5e3b299bd0dc3'

def validate_commands(data):
    """Require a complete known loader-command sequence in a single block."""
    off=0
    while off<len(data):
        if off+12>len(data): raise ValueError('Truncated loader header')
        kind,arg,length=struct.unpack_from('<3I',data,off)
        if kind in (3,5,16): end=off+12+length
        elif kind==0 and arg==4:
            if off+16>len(data): raise ValueError('Truncated load header')
            end=off+16+struct.unpack_from('<I',data,off+12)[0]
        elif kind==4 and arg==8: end=off+20
        else: raise ValueError('Unknown loader command')
        if not off<end<=len(data): raise ValueError('Loader command crosses block boundary')
        off=end
    return off

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    fw = FW.read_bytes()
    if sha(fw)!=EXPECTED: raise ValueError('Unsupported firmware hash; this extractor is version-specific')
    if len(fw)<124 or hashlib.md5(fw[124:]).digest()!=fw[108:124]: raise ValueError('Invalid ISU MD5')
    base = fw.index(b'enco') - 128
    pos = base + 144
    records = []
    blocks = {}
    while True:
        ident, offset, size, nxt, usize = struct.unpack_from('<5I', fw, pos)
        if ident == 0 or size >= 65536 or not 0 < usize <= 20480:
            break
        physical = base + offset - 0x12000
        stream = fw[physical + 1:physical + size]
        crc = binascii.crc_hqx(stream, 65535) ^ 65535
        assert fw[physical] == 0x63
        assert fw[physical + size:physical + size + 2] == crc.to_bytes(2, 'big')
        decoded = zlib.decompress(transcode(stream,'msb','lsb').data,-15)
        validate_commands(decoded)
        assert len(decoded) == usize
        blocks[ident] = decoded
        records.append(dict(id=ident, table_offset=pos, physical_offset=physical,
                            compressed_size=size, next_id=nxt, decoded_size=usize,
                            crc_verified=True, decoded_sha256=sha(decoded)))
        pos += 20
    assert records[0]['physical_offset'] == pos + 20
    assert records[-1]['physical_offset'] + records[-1]['compressed_size'] + 2 == len(fw)
    links = {r['next_id'] for r in records}
    by_id = {r['id']: r for r in records}
    chains = []
    visited = set()
    for head in (r['id'] for r in records if r['id'] not in links):
        data = bytearray()
        cur = head
        while cur in by_id:
            assert cur not in visited
            visited.add(cur)
            data += blocks[cur]
            cur = by_id[cur]['next_id']
        chains.append((head, bytes(data)))
    assert len(visited) == len(records)

    modules = []
    commands = []
    for ci, (head, data) in enumerate(chains):
        chain_name = f'chain{ci}_id{head:08x}'
        p = ROOT / 'decoded' / (chain_name + '.bin')
        p.parent.mkdir(exist_ok=True)
        p.write_bytes(data)
        off = 0
        module = None
        while off < len(data):
            kind, arg, length = struct.unpack_from('<3I', data, off)
            cmd = dict(chain=chain_name, offset=off, kind=kind)
            if kind in (3, 5, 16):
                end = off + 12 + length
                payload = data[off + 12:end]
                if kind == 16:
                    name = payload[4:].split(b'\0')[0].decode('ascii')
                    module = dict(name=name, chain=chain_name, records=[], fills=[])
                    modules.append(module)
                    cmd['module'] = name
                else:
                    cmd['payload_hex'] = payload.hex()
            elif kind == 0 and arg == 4:
                address = length
                size = struct.unpack_from('<I', data, off + 12)[0]
                end = off + 16 + size
                assert module is not None
                module['records'].append(dict(address=address, size=size,
                    chain_payload_offset=off + 16, data=data[off + 16:end]))
                cmd.update(address=address, size=size)
            elif kind == 4 and arg == 8:
                address = length
                size, value = struct.unpack_from('<2I', data, off + 12)
                end = off + 20
                assert module is not None
                module['fills'].append(dict(address=address, size=size, value=value))
                cmd.update(address=address, size=size, fill_value=value)
            else:
                raise ValueError(f'Unknown command {chain_name}:{off:x}: {kind,arg,length}')
            assert off < end <= len(data)
            commands.append(cmd)
            off = end
        assert off == len(data)

    out = ROOT / 'memory'
    out.mkdir(exist_ok=True)
    assets = ROOT / 'png'
    assets.mkdir(exist_ok=True)
    pngs = []
    module_manifest = []
    for mi, module in enumerate(modules):
        # Only initialized load records are merged. Fill records remain in the manifest.
        spans = []
        for r in sorted(module['records'], key=lambda r:r['address']):
            a, b = r['address'], r['data']
            if spans and spans[-1][0] + len(spans[-1][1]) == a:
                spans[-1][1].extend(b)
            else:
                if spans:
                    assert spans[-1][0] + len(spans[-1][1]) <= a
                spans.append((a, bytearray(b)))
        images = []
        for si, (address, buf) in enumerate(spans):
            b = bytes(buf)
            name = f'{mi:02d}_{module["name"]}_{address:08x}.bin'
            (out / name).write_bytes(b)
            images.append(dict(file='memory/'+name, address=address, size=len(b), sha256=sha(b)))
            strings = [(m.start(),m.group().decode()) for m in re.finditer(rb'[ -~]{5,}', b)]
            (out / (name+'.strings.txt')).write_text('\n'.join(f'{address+o:08x} {s}' for o,s in strings)+'\n')
            for match in re.finditer(re.escape(b'\x89PNG\r\n\x1a\n'), b):
                start = match.start()
                p = start + 8
                try:
                    while True:
                        n = struct.unpack_from('>I', b, p)[0]
                        assert n <= len(b)-p-12
                        typ = b[p+4:p+8]
                        chunk = b[p+4:p+8+n]
                        assert zlib.crc32(chunk) == struct.unpack_from('>I', b, p+8+n)[0]
                        p += 12+n
                        if typ == b'IEND': break
                    w,h = struct.unpack_from('>2I', b, start+16)
                    pngname = f'{mi:02d}_{address+start:08x}_{w}x{h}.png'
                    (assets/pngname).write_bytes(b[start:p])
                    pngs.append(dict(file='png/'+pngname, module=module['name'],
                        address=address+start, width=w, height=h, size=p-start, crc_verified=True))
                except (AssertionError, struct.error):
                    pass
        module_manifest.append(dict(name=module['name'], chain=module['chain'],
            load_record_count=len(module['records']), images=images, fills=module['fills'],
            records=[{k:v for k,v in r.items() if k!='data'} for r in module['records']]))
    result = dict(firmware=FW.name, sha256=sha(fw), compressed_blocks=records,
        chain_count=len(chains), decoded_bytes=sum(len(d) for _,d in chains),
        loader_command_count=len(commands), command_counts=dict(collections.Counter(c['kind'] for c in commands)),
        modules=module_manifest, pngs=pngs,
        limitations=['Loader command semantics are inferred from structure; no firmware was executed.',
            'Memory images contain initialized load bytes only; zero/fill regions remain in manifest.',
            'PNG extraction is signature-based; extracted images are not automatically display UI assets.',
            'No META machine code has been decompiled to C.'])
    (ROOT/'manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    (ROOT/'loader_commands.json').write_text(json.dumps(commands,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['compressed_blocks','modules','pngs']},indent=2))
    print('modules',[(m['name'],len(m['images']),m['load_record_count']) for m in module_manifest])
    print('PNGs',len(pngs),[(p['width'],p['height']) for p in pngs])

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='Offline extraction of the documented original; never contacts a radio.')
    parser.add_argument('firmware',type=Path)
    parser.add_argument('--output',type=Path,required=True,help='New private output directory')
    args=parser.parse_args()
    FW=args.firmware.resolve(); ROOT=args.output.resolve()
    if sha(FW.read_bytes())!=EXPECTED: parser.error('Unsupported firmware SHA-256')
    ROOT.mkdir(parents=True,exist_ok=False)
    main()
