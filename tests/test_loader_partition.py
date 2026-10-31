import sys
import struct
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from loader_partition import partition_commands
from analyze_firmware import validate_commands


def load(size):
    return struct.pack('<4I', 0, 4, 0x32000000, size) + bytes(size)


class LoaderPartitionTests(unittest.TestCase):
    def test_expansion_moves_boundary_without_changing_stream(self):
        stream = load(14) + load(8) + load(8)
        with self.assertRaises(ValueError):
            validate_commands(stream[:48])
        parts = partition_commands(stream, 2, limit=54)
        self.assertEqual([len(p) for p in parts], [54, 24])
        self.assertEqual(b''.join(parts), stream)

    def test_exact_count_and_order(self):
        stream = b''.join(load(n) for n in range(20))
        for count in range(5, 21):
            parts = partition_commands(stream, count, 128)
            self.assertEqual(len(parts), count)
            self.assertEqual(b''.join(parts), stream)
            for part in parts:
                self.assertEqual(validate_commands(part), len(part))

    def test_refuses_invalid_or_impossible_inputs(self):
        for stream, count, limit in [(load(100), 1, 64), (load(1), 2, 64),
                                      (load(20)*3, 2, 60), (load(3)[:-1], 1, 64),
                                      (b'', 1, 64), (load(1), 0, 64)]:
            with self.assertRaises(ValueError):
                partition_commands(stream, count, limit)


class PreservationTests(unittest.TestCase):
    def test_identity_and_changed_prefix_preserve_suffix(self):
        from loader_partition import partition_preserving_blocks
        original = [load(32), load(24), load(16)]
        self.assertEqual(partition_preserving_blocks(b''.join(original), original, 64), original)
        changed = load(48) + b''.join(original[1:])
        parts = partition_preserving_blocks(changed, original, 64)
        self.assertEqual(parts[1:], original[1:])
        self.assertEqual(b''.join(parts), changed)
        middle_change = original[0] + load(40) + original[2]
        parts = partition_preserving_blocks(middle_change, original, 64)
        self.assertEqual(parts[0], original[0])
        self.assertEqual(parts[-1], original[-1])
        self.assertEqual(b''.join(parts), middle_change)

    def test_capacity_expands_middle_and_retains_order(self):
        from loader_partition import partition_preserving_blocks
        original = [load(4)*2]*3
        changed = bytearray(load(4)*7)
        changed[16] = 1
        changed = bytes(changed)
        parts = partition_preserving_blocks(changed, original, 64)
        self.assertEqual(len(parts), 3)
        self.assertEqual(b''.join(parts), changed)
        self.assertEqual(parts[-1], original[-1])

    def test_append_releases_prefix_and_impossible_input_fails(self):
        from loader_partition import partition_preserving_blocks
        original = [load(4), load(4)]
        parts = partition_preserving_blocks(b''.join(original)+load(4), original, 64)
        self.assertEqual(len(parts), 2)
        self.assertEqual(b''.join(parts), b''.join(original)+load(4))
        with self.assertRaises(ValueError):
            partition_preserving_blocks(load(100), original, 64)
