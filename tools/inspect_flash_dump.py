"""Read-only inspection of a caller-supplied full dump using one static layout.

No flash access, patching, CRC verification, or active-record selection. A matching
object header is a candidate only; fragmented and encrypted objects are not decoded.
"""
import argparse,hashlib,json,struct
from pathlib import Path
LAYOUT='fs2340-touro-v4.10.18'
FLASH_SIZE=8*1024*1024
START=0x7a1000
END=0x7ff000
SECTOR_SIZE=4096
OBJECT_SIZE=292

def inspect_dump(data):
    if len(data)!=FLASH_SIZE:raise ValueError('Expected an 8 MiB full-chip dump; an ISU update is not a flash dump')
    region=data[START:END]
    sectors=[region[n:n+SECTOR_SIZE] for n in range(0,len(region),SECTOR_SIZE)]
    candidates=[]
    # First six schema bytes: tag3, header length12, version1. Keep unknown flags explicit.
    signature=struct.pack('<IBB',3,12,1)
    position=0
    while True:
        position=region.find(signature,position)
        if position<0:break
        at=position;position+=1
        if at+12>len(region):continue
        tag,header_length,version,flags,size=struct.unpack_from('<IBBHI',region,at)
        if size!=OBJECT_SIZE:continue
        complete=at+size<=len(region)
        crosses=(at%SECTOR_SIZE)+size>SECTOR_SIZE
        candidate=dict(offset=f'0x{START+at:06x}',tag=tag,header_length=header_length,version=version,flags=flags,total_object_size=size,within_region=complete,crosses_sector_boundary=crosses,recognition='Unverified contiguous schema-header candidate; record identity, checksum and generation not verified')
        # Read only the documented scalar fields, never strings or other personal payload.
        if flags==0 and complete and not crosses:
            time_source=struct.unpack_from('<i',region,at+20)[0]
            language=region[at+41]
            candidate['unverified_fields']={'time_update_source':time_source,'language_index':language,'plausible_values':time_source in (0,1,2,4) and language<15}
        candidates.append(candidate)
    return dict(layout=LAYOUT,dump_sha256=hashlib.sha256(data).hexdigest(),dump_size=len(data),configured_settings_window={'start':f'0x{START:06x}','end_exclusive':f'0x{END:06x}','length':END-START,'sector_size':SECTOR_SIZE,'sector_count':len(sectors)},fully_erased_0xff_sectors=sum(all(x==255 for x in s) for s in sectors),object_header_candidates=candidates,limitations=['Layout is from one documented firmware version; it is not automatically detected or hardware-validated.','Header matches do not establish record key0x2e, validity, current generation, or safe modification.','No storage checksum verification, journal reconstruction, decryption, or fragmented-object reconstruction.','Areas outside the configured settings window remain unclassified; the final4KiB must not be assumed disposable.'])

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dump',type=Path)
    parser.add_argument('--layout',required=True,choices=[LAYOUT],help='Explicitly select the version-specific layout assumption')
    parser.add_argument('--output',type=Path,required=True,help='New private JSON output file')
    args=parser.parse_args()
    if args.output.resolve()==args.dump.resolve():parser.error('Output must not be the input dump')
    if args.dump.stat().st_size!=FLASH_SIZE:parser.error('Expected an 8 MiB full-chip dump')
    result=inspect_dump(args.dump.read_bytes())
    with args.output.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
    print(f'Read-only inspection complete: {len(result["object_header_candidates"])} unverified header candidates. No checksums verified; input unchanged.')
if __name__=='__main__':main()
