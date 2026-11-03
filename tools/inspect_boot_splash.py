"""Inspect the version-specific FSSP boot image offline, without emitting pixels.

No hardware access or firmware modification. Image dimensions and byte order are
corroborated by this version's primary display renderer, not encoded in FSSP.
"""
import argparse
import hashlib
import json
import struct
import zlib
from pathlib import Path
from inspect_boot_prefix import crc16, FLASH_SIZE, LAYOUT
from deflate_transcode import transcode

SPLASH_START=0x781000
SPLASH_LIMIT=0x7a1000
WIDTH,HEIGHT=320,240
PIXEL_BYTES=WIDTH*HEIGHT*2


def inspect_splash(dump):
    if len(dump)!=FLASH_SIZE:raise ValueError('Expected an 8 MiB dump')
    if dump[0x20:0x24]!=b'FSSP' or struct.unpack_from('<I',dump,0x24)[0]!=SPLASH_START:
        raise ValueError('Unexpected version-specific FSSP header pointer')
    if dump[SPLASH_START:SPLASH_START+4]!=b'FSSP':raise ValueError('Missing FSSP record')
    length=struct.unpack_from('<I',dump,SPLASH_START+4)[0]
    start=SPLASH_START+8;end=start+length
    if length<2 or end+2>SPLASH_LIMIT:raise ValueError('FSSP compressed length outside configured window')
    encoded=dump[start:end]
    expected=int.from_bytes(dump[end:end+2],'big')
    if crc16(encoded)!=expected:raise ValueError('FSSP compressed-data CRC mismatch')
    decompressor=zlib.decompressobj(-15)
    pixels=decompressor.decompress(transcode(encoded,'msb','lsb').data,PIXEL_BYTES+1)
    if len(pixels)!=PIXEL_BYTES or not decompressor.eof or decompressor.unused_data or decompressor.unconsumed_tail:
        raise ValueError('FSSP does not decode to the expected complete 320x240x2 image')
    return {'layout':LAYOUT,'record_offset':hex(SPLASH_START),'compressed_offset':hex(start),
            'compressed_length':length,'crc_offset':hex(end),'crc16_big_endian':hex(expected),
            'crc_valid':True,'record_end_exclusive':hex(end+2),'decoded_size':len(pixels),
            'width':WIDTH,'height':HEIGHT,'pixel_format':'RGB565, big-endian words',
            'decoded_sha256':hashlib.sha256(pixels).hexdigest(),
            'limitations':['Dimensions and format are specific to the traced primary renderer.',
                           'No target execution or confirmation of physical panel colors.',
                           'Following record bytes are not classified or modified.',
                           'No pixels or manufacturer bitmap are emitted.']}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('dump',type=Path)
    p.add_argument('--layout',choices=[LAYOUT],required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.output.resolve()==a.dump.resolve():p.error('Output must differ from input')
    if a.dump.stat().st_size!=FLASH_SIZE:p.error('Expected an 8 MiB dump')
    report=inspect_splash(a.dump.read_bytes())
    with a.output.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
    print('FSSP CRC and complete 320x240 image verified. No hardware access or pixels emitted.')

if __name__=='__main__':main()
