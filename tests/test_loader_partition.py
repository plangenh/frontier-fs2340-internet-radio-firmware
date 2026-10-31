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
