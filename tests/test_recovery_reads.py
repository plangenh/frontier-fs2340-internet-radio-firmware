import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from check_recovery_reads import inspect_reads
from compare_update_to_dump import FLASH_SIZE


class RecoveryReadTests(unittest.TestCase):
    def test_matching_nonconstant_and_unchanged(self):
        read = bytearray(b'\xff') * FLASH_SIZE
        read[42] = 3
        before = bytes(read)
        result = inspect_reads([read, before])
        self.assertTrue(result['reads_identical'])
        self.assertTrue(result['candidate_comparison_performed'])
        self.assertEqual(read, before)

    def test_mismatch_and_constant_skip_candidates(self):
        read = b'\xff' * FLASH_SIZE
        other = bytearray(read)
        other[-1] = 0
        for reads in ([read, other], [read, read]):
            result = inspect_reads(reads, [b'invalid candidate must not be compared'])
            self.assertFalse(result['candidate_comparison_performed'])
            self.assertEqual(result['candidate_comparisons'], [])

    def test_input_bounds(self):
        for reads in ([], [b'a'], [b'a', b'a']):
            with self.assertRaises(ValueError):
                inspect_reads(reads)
