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


def partition_preserving_blocks(stream, original_parts, limit=20480):
    """Keep matching prefix/suffix blocks where whole-command packing permits.

    This is a bounded preservation heuristic, not a minimum-change optimizer.
    Existing block count and order are retained; IDs are assigned by the caller.
    """
    if not original_parts:
        raise ValueError('At least one original block required')
    for part in original_parts:
        if not 0 < len(part) <= limit:
            raise ValueError('Invalid original block size')
        validate_commands(part)
    validate_commands(stream)
    left = 0
    start = 0
    while left < len(original_parts) and stream[start:start+len(original_parts[left])] == original_parts[left]:
        start += len(original_parts[left])
        left += 1
    if left == len(original_parts) and start == len(stream):
        return list(original_parts)
    # A growing stream may append commands after all original blocks; release
    # the last prefix block to retain the fixed count of nonempty blocks.
    if left == len(original_parts):
        left -= 1
        start -= len(original_parts[left])
    right = len(original_parts)
    end = len(stream)
    while right > left and end-len(original_parts[right-1]) >= start:
        part = original_parts[right-1]
        if stream[end-len(part):end] != part:
            break
        end -= len(part)
        right -= 1
    while True:
        try:
            middle = partition_commands(stream[start:end], right-left, limit)
            parts = list(original_parts[:left]) + middle + list(original_parts[right:])
            if b''.join(parts) != stream or len(parts) != len(original_parts):
                raise ValueError('Preserved partition mismatch')
            return parts
        except ValueError:
            if right < len(original_parts):
                end += len(original_parts[right])
                right += 1
            elif left > 0:
                left -= 1
                start -= len(original_parts[left])
            else:
                raise
