"""Inspect the observed FS2340 boot prefix offline; emit metadata, never firmware.

One explicit version-specific layout. No hardware access or target execution.
Code addresses and recovery behavior require separate disassembly evidence.
"""
import argparse
import binascii
import hashlib
import json
import struct
import zlib
from pathlib import Path
from deflate_transcode import transcode

LAYOUT = 'fs2340-touro-v4.10.18'
FLASH_SIZE = 0x800000
PREFIX_END = 0x12000
MAX_SECONDARY = 0x100000


def crc16(data):
    return binascii.crc_hqx(data, 0xffff) ^ 0xffff


def inspect_prefix(dump):
    if len(dump) != FLASH_SIZE:
        raise ValueError('Expected an 8 MiB dump')
    prefix = dump[:PREFIX_END]
    if struct.unpack_from('<I', prefix)[0] != 0x01aa5500:
        raise ValueError('Unsupported prefix magic')
    if crc16(prefix[:14]) != int.from_bytes(prefix[14:16], 'big'):
        raise ValueError('Header CRC mismatch')
    first, marker = struct.unpack_from('<II', prefix, 4)
    if (first, marker) != (0x100, 0x12080):
        raise ValueError('Unexpected version-specific header pointers')
    tags = {}
    for offset, expected in [(0x10,b'APPN'),(0x18,b'LNVS'),(0x20,b'FSSP'),(0x28,b'PEND')]:
        if prefix[offset:offset+4] != expected:
            raise ValueError('Unexpected header tag')
        value = struct.unpack_from('<I',prefix,offset+4)[0]
        if value >= FLASH_SIZE:
            raise ValueError('Header pointer outside flash')
        tags[expected.decode()] = hex(value)
    records = []
    primary = bytearray()
    seen = set()
    at = first
    while at:
        if at in seen or at < 0x100 or at % 128 or at+128 > PREFIX_END:
            raise ValueError('Cyclic, unaligned or out-of-range record link')
        seen.add(at)
        record = prefix[at:at+128]
        following, length = struct.unpack_from('<IH',record,120)
        if length != 128 or crc16(record[:126]) != int.from_bytes(record[126:128],'big'):
            raise ValueError('Record length or CRC mismatch')
        records.append({'offset':hex(at),'next':hex(following)})
        primary.extend(record[:120])
        at = following
    positions = [i for i in range(len(primary)) if primary.startswith(b'SECLCONF',i)]
    if len(positions) != 1 or positions[0]+16 > len(primary):
        raise ValueError('Expected one complete secondary configuration marker')
    source, size = struct.unpack_from('<II',primary,positions[0]+8)
    if source < max(seen)+128 or size < 3 or source+size > PREFIX_END:
        raise ValueError('Secondary carrier overlaps records or exceeds prefix')
    carrier = prefix[source:source+size]
    if crc16(carrier[:-2]) != int.from_bytes(carrier[-2:],'big'):
        raise ValueError('Secondary carrier CRC mismatch')
    decoder = zlib.decompressobj(-15)
    secondary = decoder.decompress(transcode(carrier[:-2],'msb','lsb').data,MAX_SECONDARY+1)
    if len(secondary)>MAX_SECONDARY or not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
        raise ValueError('Oversized, incomplete or trailing secondary DEFLATE data')
    return {'layout':LAYOUT,'prefix_size':PREFIX_END,'prefix_sha256':hashlib.sha256(prefix).hexdigest(),
            'header_crc_valid':True,'header_tags':tags,'main_marker':hex(marker),
            'record_count':len(records),'record_crcs_valid':True,'records':records,
            'primary_stripped_size':len(primary),'primary_sha256':hashlib.sha256(primary).hexdigest(),
            'secondary_carrier':{'offset':hex(source),'size':size,'crc_valid':True},
            'secondary_decoded_size':len(secondary),'secondary_sha256':hashlib.sha256(secondary).hexdigest(),
            'limitations':['Version-specific structural interpretation, not boot emulation.',
                           'DEFLATE transcoder shared with other project analysis tools.',
                           'No claim about complete ROM code, signatures, recovery entry conditions or bootability.',
                           'No original code, device configuration or executable bytes emitted.']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dump',type=Path)
    parser.add_argument('--layout',choices=[LAYOUT],required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.dump.resolve()==args.output.resolve():parser.error('Output must differ from input')
    if args.dump.stat().st_size!=FLASH_SIZE:parser.error('Expected an 8 MiB dump')
    report=inspect_prefix(args.dump.read_bytes())
    with args.output.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
    print(f'Prefix CRCs valid: {report["record_count"]} records; secondary decoded size {report["secondary_decoded_size"]}. No hardware access.')

if __name__=='__main__':main()
