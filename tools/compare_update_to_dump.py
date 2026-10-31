"""Compare a version-specific ISU payload to a full dump without modifying either.

Uses the statically traced ordinary local-upload address mapping. It does not
validate every container block, emulate boot, build a repair image, or access SPI.
"""
import argparse,hashlib,json,struct
from pathlib import Path
FLASH_SIZE=8*1024*1024
PAYLOAD_BASE=0x12000
SETTINGS_START=0x7a1000
CUSTOMISATION='ir-cui-FS2340-0000-0444'
VERSION='V4.10.18.281972.EX11_10-1A8'
LAYOUT='fs2340-touro-v4.10.18'

def parse_update(data):
    if len(data)<124:raise ValueError('Truncated ISU header')
    magic,offset,format_version=struct.unpack_from('<3I',data)
    if (magic,offset,format_version)!=(0x1176,124,1):raise ValueError('Unsupported ISU outer header')
    version=data[12:44].decode('ascii').rstrip(' \0')
    if version!=VERSION:raise ValueError('Unsupported firmware version')
    customisation=data[44:108].decode('ascii').rstrip(' \0')
    if customisation!=CUSTOMISATION:raise ValueError('Unsupported customization; mapping is not portable across devices')
    payload=data[offset:]
    if len(payload)<144 or payload[128:132]!=b'enco':raise ValueError('Expected ordinary enco payload at the documented position')
    if hashlib.md5(payload).digest()!=data[108:124]:raise ValueError('ISU payload MD5 mismatch')
    if PAYLOAD_BASE+len(payload)>SETTINGS_START:raise ValueError('Payload overlaps configured settings window; this tool refuses the layout')
    return payload

def compare_images(dump,update):
    if len(dump)!=FLASH_SIZE:raise ValueError('Expected an 8 MiB full-chip dump')
    payload=parse_update(update)
    end=PAYLOAD_BASE+len(payload)
    stored=dump[PAYLOAD_BASE:end]
    different=sum(a!=b for a,b in zip(stored,payload))
    intervals=[];begin=None;total_intervals=0
    for i,(a,b) in enumerate(zip(stored,payload)):
        if a!=b and begin is None:begin=i
        if a==b and begin is not None:
            total_intervals+=1
            if len(intervals)<32:intervals.append({'start':hex(PAYLOAD_BASE+begin),'end_exclusive':hex(PAYLOAD_BASE+i)})
            begin=None
    if begin is not None:
        total_intervals+=1
        if len(intervals)<32:intervals.append({'start':hex(PAYLOAD_BASE+begin),'end_exclusive':hex(end)})
    return dict(layout=LAYOUT,dump_sha256=hashlib.sha256(dump).hexdigest(),update_sha256=hashlib.sha256(update).hexdigest(),comparison_window={'start':hex(PAYLOAD_BASE),'end_exclusive':hex(end),'length':len(payload)},exact_payload_match=different==0,different_bytes=different,difference_interval_count=total_intervals,first_difference_intervals=intervals,intervals_truncated=total_intervals>32,limitations=['Mapping is from the documented ordinary local-upload path; no hardware dump validation has yet been performed.','Outer MD5 and byte comparison do not establish block validity, firmware acceptance, bootability, or current active-image selection.','The pre-write helper and boot/commit metadata outside this window are not reconstructed.','No bytes outside the compared window were classified; no modification or repair image was produced.'])

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('dump',type=Path);p.add_argument('update',type=Path)
    p.add_argument('--layout',required=True,choices=[LAYOUT]);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.output.resolve() in {a.dump.resolve(),a.update.resolve()}:p.error('Output must differ from both inputs')
    if a.dump.stat().st_size!=FLASH_SIZE:p.error('Expected an 8 MiB full-chip dump')
    if a.update.stat().st_size>SETTINGS_START-PAYLOAD_BASE+124:p.error('Update too large for the documented comparison window')
    result=compare_images(a.dump.read_bytes(),a.update.read_bytes())
    with a.output.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
    print(f'Read-only comparison complete: exact payload match={result["exact_payload_match"]}; different bytes={result["different_bytes"]}. No repair image produced.')
if __name__=='__main__':main()
