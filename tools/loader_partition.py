"""Partition known loader commands without splitting a command across blocks.

Offline research primitive, not a firmware acceptance or bootability validator.
"""
import struct
from analyze_firmware import validate_commands


def command_records(stream):
    validate_commands(stream)
    offset = 0
    while offset < len(stream):
        kind, arg, length = struct.unpack_from('<3I', stream, offset)
        if kind in (3, 5, 16):
            end = offset + 12 + length
        elif kind == 0 and arg == 4:
            end = offset + 16 + struct.unpack_from('<I', stream, offset + 12)[0]
        else:
            end = offset + 20
        yield stream[offset:end]
        offset = end


def partition_commands(stream, block_count, limit=20480):
    if block_count < 1 or limit < 1:
        raise ValueError('Positive block count and size limit required')
    records = list(command_records(stream))
    if len(records) < block_count:
        raise ValueError('Insufficient commands for nonempty existing blocks')
    groups = []
    current = []
    size = 0
    for record in records:
        if len(record) > limit:
            raise ValueError('Single loader command exceeds block limit')
        if current and size + len(record) > limit:
            groups.append(current)
            current = []
            size = 0
        current.append(record)
        size += len(record)
    if current:
        groups.append(current)
    if len(groups) > block_count:
        raise ValueError('Complete commands do not fit existing block count')
    # Splitting an existing group at a command boundary cannot increase its size.
    while len(groups) < block_count:
        index = max(range(len(groups)), key=lambda i: len(groups[i]))
        group = groups[index]
        middle = len(group) // 2
        groups[index:index + 1] = [group[:middle], group[middle:]]
    parts = [b''.join(group) for group in groups]
    if b''.join(parts) != stream:
        raise ValueError('Partition changed loader bytes')
    for part in parts:
        if not 0 < len(part) <= limit:
            raise ValueError('Invalid partition size')
        validate_commands(part)
    return parts
