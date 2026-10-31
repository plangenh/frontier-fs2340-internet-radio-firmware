"""Check repeatability of full-chip reads and compare explicit ISU candidates.

Read-only; matching reads are not proof of electrical correctness or bootability.
"""
import argparse
import hashlib
import json
from pathlib import Path
from compare_update_to_dump import FLASH_SIZE, LAYOUT, compare_images


def inspect_reads(reads, updates=()):
    if len(reads) < 2:
        raise ValueError('At least two independently acquired reads are required')
    if any(len(data) != FLASH_SIZE for data in reads):
        raise ValueError('Every read must contain exactly 8 MiB')
    hashes = [hashlib.sha256(data).hexdigest() for data in reads]
    identical = all(data == reads[0] for data in reads[1:])
    constant = [data.count(data[:1]) == FLASH_SIZE for data in reads]
    result = {
        'layout': LAYOUT,
        'read_sha256': hashes,
        'reads_identical': identical,
        'constant_byte_reads': constant,
        'candidate_comparison_performed': identical and not any(constant),
        'candidate_comparisons': [],
        'limitations': [
            'Independent acquisition cannot be established from file contents.',
            'Identical nonconstant reads can still be consistently incorrect.',
            'No electrical diagnosis, boot validation, repair image, or write authorization is implied.',
            'Candidate comparisons cover only their mapped payload windows; other regions remain unclassified.'
        ]
    }
    if result['candidate_comparison_performed']:
        result['candidate_comparisons'] = [compare_images(reads[0], data) for data in updates]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('reads', nargs='+', type=Path)
    parser.add_argument('--update', action='append', type=Path, default=[])
    parser.add_argument('--layout', required=True, choices=[LAYOUT])
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    inputs = args.reads + args.update
    if len(args.reads) < 2:
        parser.error('Supply at least two independently acquired reads')
    if len({p.resolve() for p in args.reads}) != len(args.reads):
        parser.error('Read paths must be distinct')
    if args.output.resolve() in {p.resolve() for p in inputs}:
        parser.error('Output must differ from all inputs')
    if any(p.stat().st_size != FLASH_SIZE for p in args.reads):
        parser.error('Every read must contain exactly 8 MiB')
    if any(p.stat().st_size > FLASH_SIZE for p in args.update):
        parser.error('Candidate update exceeds supported chip size')
    result = inspect_reads([p.read_bytes() for p in args.reads], [p.read_bytes() for p in args.update])
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print('Read checks complete; identical=' + str(result['reads_identical']) + '. No Flash writes performed.')


if __name__ == '__main__':
    main()
