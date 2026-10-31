"""Independent structural FS2340 checker; no firmware execution or device access.

Container and command parsing do not import the packer or extraction parser.
Vendor DEFLATE bit conversion is shared and is not independently verified here.
"""
import argparse
import binascii
import hashlib
import json
import struct
import zlib
from pathlib import Path
from deflate_transcode import transcode


def scan_commands(block, module=None):
    cursor = 0
    writes = []
    count = 0
    while cursor < len(block):
        remaining = len(block) - cursor
        if remaining < 12:
            raise ValueError('Incomplete command header')
        tag = int.from_bytes(block[cursor:cursor+4], 'little')
        argument = int.from_bytes(block[cursor+4:cursor+8], 'little')
        third = int.from_bytes(block[cursor+8:cursor+12], 'little')
        header = 12
        if tag in (3, 5, 16):
            size = third
            if size > remaining - header:
                raise ValueError('Metadata crosses block boundary')
            if tag == 16:
                payload = block[cursor+12:cursor+12+size]
                if len(payload) < 5 or b'\0' not in payload[4:]:
                    raise ValueError('Missing terminated module name')
                module = payload[4:].split(b'\0', 1)[0].decode('ascii')
                if not module:
                    raise ValueError('Empty module name')
        elif (tag, argument) in ((0, 4), (4, 8)):
            header = 16 if tag == 0 else 20
            if remaining < header:
                raise ValueError('Incomplete memory command header')
            length = int.from_bytes(block[cursor+12:cursor+16], 'little')
            if module is None:
                raise ValueError('Memory command before module declaration')
            if length > 0x100000000 - third:
                raise ValueError('Memory address wraps 32-bit space')
            size = length if tag == 0 else 0
            if size > remaining - header:
                raise ValueError('Load crosses block boundary')
            record = {'module': module, 'address': third, 'length': length,
                      'kind': 'load' if tag == 0 else 'fill'}
            if tag == 0:
                record['data'] = block[cursor+16:cursor+16+length]
            else:
                record['value'] = int.from_bytes(block[cursor+16:cursor+20], 'little')
            writes.append(record)
        else:
            raise ValueError('Unsupported command tag/argument')
        cursor += header + size
        count += 1
    return module, writes, count


def check_image(image):
    if len(image) < 288 or len(image) > 8*1024*1024:
        raise ValueError('Unsupported image size')
    if struct.unpack_from('<3I', image) != (0x1176, 124, 1):
        raise ValueError('Unsupported outer header')
    if hashlib.md5(image[124:]).digest() != image[108:124]:
        raise ValueError('Outer MD5 mismatch')
    if image[252:256] != b'enco':
        raise ValueError('Missing enco marker')
    entries = []
    position = 268
    seen = set()
    while True:
        if position + 20 > len(image):
            raise ValueError('Truncated block table')
        ident, address, size, link, decoded_size = struct.unpack_from('<5I', image, position)
        position += 20
        if ident == 0:
            break
        if ident in seen:
            raise ValueError('Duplicate block ID')
        seen.add(ident)
        if not 1 < size < 65536 or not 0 < decoded_size <= 20480:
            raise ValueError('Invalid block size')
        if len(entries) >= 4096 or sum(e[4] for e in entries) + decoded_size > 64*1024*1024:
            raise ValueError('Analysis resource bound exceeded')
        entries.append((ident, address - 0x12000 + 124, size, link, decoded_size))
    if not entries:
        raise ValueError('Empty block table')
    blocks = {}
    for ident, offset, size, link, decoded_size in entries:
        if offset != position or offset + size + 2 > len(image):
            raise ValueError('Noncontiguous or out-of-range block')
        if image[offset] != 0x63:
            raise ValueError('Wrong block prefix')
        encoded = image[offset+1:offset+size]
        expected_crc = int.from_bytes(image[offset+size:offset+size+2], 'big')
        if binascii.crc_hqx(encoded, 0xffff) ^ 0xffff != expected_crc:
            raise ValueError('Block CRC mismatch')
        decoder = zlib.decompressobj(-15)
        decoded = decoder.decompress(transcode(encoded, 'msb', 'lsb').data, decoded_size+1)
        if len(decoded) != decoded_size or not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
            raise ValueError('Invalid or oversized DEFLATE stream')
        blocks[ident] = (link, decoded)
        position = offset + size + 2
    if position != len(image):
        raise ValueError('Unexpected trailing bytes')
    links = [entry[3] for entry in entries]
    heads = [entry[0] for entry in entries if entry[0] not in links]
    visited = set()
    writes = []
    command_count = 0
    for head in heads:
        current = head
        module = None
        while current in blocks:
            if current in visited:
                raise ValueError('Cyclic or merged block chains')
            visited.add(current)
            current, data = blocks[current]
            module, records, count = scan_commands(data, module)
            writes.extend(records)
            command_count += count
    if len(visited) != len(blocks):
        raise ValueError('Unreachable or cyclic blocks')
    overlaps = []
    # Report all overlapping writes; do not assume all overlaps are corruption.
    by_module = {}
    for index, record in enumerate(writes):
        by_module.setdefault(record['module'], []).append((index, record))
    for records in by_module.values():
        active = []
        for index, record in sorted(records, key=lambda item: item[1]['address']):
            start, end = record['address'], record['address'] + record['length']
            active = [(i, r) for i, r in active if r['address'] + r['length'] > start]
            for previous_index, previous in active:
                lo = max(start, previous['address'])
                hi = min(end, previous['address'] + previous['length'])
                if lo < hi:
                    if len(overlaps) >= 100000:
                        raise ValueError('Overlap analysis resource bound exceeded')
                    overlaps.append({'earlier_write': min(previous_index, index),
                                     'later_write': max(previous_index, index),
                                     'start': hex(lo), 'end_exclusive': hex(hi)})
            if end > start:
                active.append((index, record))
    return {'sha256': hashlib.sha256(image).hexdigest(), 'blocks': len(blocks),
            'chains': len(heads), 'commands': command_count, 'writes': len(writes),
            'module_names': sorted(by_module), 'overlapping_writes': overlaps,
            'limitations': ['Static structural checks only; no hardware boot test.',
                            'DEFLATE bit transcoder is shared with other analysis tools.',
                            'Unknown chain terminal IDs are retained as opaque; no terminal whitelist is established.',
                            'Address checks detect 32-bit wrap, not validity for physical RAM or MMIO.',
                            'Overlaps are reported, not automatically classified as invalid.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.image.stat().st_size > 8*1024*1024:
        parser.error('Image exceeds supported size')
    if args.image.resolve() == args.output.resolve():
        parser.error('Output must differ from input')
    result = check_image(args.image.read_bytes())
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print('Structural checks passed; no bootability claim or device access.')


if __name__ == '__main__':
    main()
