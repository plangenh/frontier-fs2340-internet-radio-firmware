"""Compare offline load/fill results through the second structural parser.

No target execution; equality of reconstructed bytes does not prove bootability.
"""
import argparse
import json
import struct
from pathlib import Path
from independent_loader_check import check_image

PAGE = 4096
MAX_PAGES = 16384


def replay(records):
    pages = {}
    for record in records:
        size = record['length']
        position = 0
        while position < size:
            address = record['address'] + position
            key = (record['module'], address // PAGE)
            offset = address % PAGE
            length = min(size-position, PAGE-offset)
            if key not in pages:
                if len(pages) >= MAX_PAGES:
                    raise ValueError('Memory replay resource bound exceeded')
                pages[key] = (bytearray(PAGE), bytearray(PAGE))
            data, mask = pages[key]
            if record['kind'] == 'load':
                chunk = record['data'][position:position+length]
            else:
                pattern = struct.pack('<I', record['value'])
                phase = position % 4
                chunk = (pattern * ((length+phase+3)//4))[phase:phase+length]
            data[offset:offset+length] = chunk
            mask[offset:offset+length] = b'\1' * length
            position += length
    return pages


def compare_records(before, after, allowed=()):
    old, new = replay(before), replay(after)
    coverage = 0
    different = 0
    outside = 0
    modules = {}
    first = []
    for key in sorted(old.keys() | new.keys()):
        a, am = old.get(key, (bytes(PAGE), bytes(PAGE)))
        b, bm = new.get(key, (bytes(PAGE), bytes(PAGE)))
        module, page = key
        for offset in range(PAGE):
            if am[offset] != bm[offset]:
                coverage += 1
            elif am[offset] and a[offset] != b[offset]:
                different += 1
                address = page * PAGE + offset
                modules[module] = modules.get(module, 0) + 1
                if len(first) < 32:
                    first.append({'module': module, 'address': hex(address)})
                if not any(name == module and start <= address < end for name, start, end in allowed):
                    outside += 1
    return {'coverage_difference_bytes': coverage, 'changed_mapped_bytes': different,
            'changed_bytes_by_module': modules, 'changed_bytes_outside_allowed_ranges': outside,
            'first_changed_addresses': first,
            'scope_check_passed': coverage == 0 and outside == 0}


def compare_images(before, after, allowed=()):
    a, b = check_image(before, True), check_image(after, True)
    result = compare_records(a['_writes'], b['_writes'], allowed)
    result.update(before_sha256=a['sha256'], after_sha256=b['sha256'],
                  metadata_command_sequence_equal=a['_metadata'] == b['_metadata'],
                  allowed_ranges=[{'module': name, 'start': hex(start), 'end_exclusive': hex(end)}
                                  for name, start, end in allowed],
                  limitations=['Reconstructed load/fill bytes only; no execution, acceptance or boot test.',
                               'The second parser still shares the DEFLATE transcoder.',
                               'Allowed ranges are caller-supplied, not discovered or authorized by this tool.',
                               'Coverage changes are reported separately from changed jointly mapped bytes.'])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('before', type=Path)
    parser.add_argument('after', type=Path)
    parser.add_argument('--allow', action='append', default=[], metavar='MODULE:START:END')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    allowed = []
    for value in args.allow:
        name, start, end = value.rsplit(':', 2)
        start, end = int(start, 0), int(end, 0)
        if not 0 <= start < end <= 0x100000000:
            parser.error('Invalid allowed range')
        allowed.append((name, start, end))
    if args.output.resolve() in {args.before.resolve(), args.after.resolve()}:
        parser.error('Output must differ from inputs')
    if any(p.stat().st_size > 8*1024*1024 for p in (args.before, args.after)):
        parser.error('Input exceeds supported size')
    result = compare_images(args.before.read_bytes(), args.after.read_bytes(), allowed)
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print('Offline memory comparison complete; no device access or bootability claim.')


if __name__ == '__main__':
    main()
