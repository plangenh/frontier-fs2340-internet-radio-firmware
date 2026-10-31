import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compare_loaded_memory import replay, compare_records, compare_images
from test_independent_loader import fixture, module, load


def record(address, data):
    return {'module': 'test', 'kind': 'load', 'address': address, 'length': len(data), 'data': data}


class LoadedMemoryTests(unittest.TestCase):
    def test_fill_phase_across_page_and_equivalent_materialization(self):
        fill = {'module': 'test', 'kind': 'fill', 'address': 4095, 'length': 9, 'value': 0x04030201}
        materialized = record(4095, b'\1\2\3\4\1\2\3\4\1')
        self.assertEqual(replay([fill]), replay([materialized]))
        self.assertTrue(compare_records([fill], [materialized])['scope_check_passed'])

    def test_zero_coverage_is_not_unmapped(self):
        result = compare_records([], [record(0, b'\0')])
        self.assertEqual(result['coverage_difference_bytes'], 1)
        self.assertFalse(result['scope_check_passed'])

    def test_scopes_and_last_write_order(self):
        before = [record(10, b'abc')]
        after = before + [record(11, b'Z')]
        result = compare_records(before, after, [('test', 11, 12)])
        self.assertEqual(result['changed_mapped_bytes'], 1)
        self.assertTrue(result['scope_check_passed'])
        self.assertFalse(compare_records(before, after, [('test', 10, 11)])['scope_check_passed'])
        self.assertEqual(replay(after), replay([record(10, b'aZc')]))

    def test_full_container_metadata_and_inputs(self):
        before = fixture(module()+load(data=b'abc'))
        after = fixture(module()+load(data=b'aZc'))
        saved = bytes(after)
        result = compare_images(before, after, [('test', 0x32000001, 0x32000002)])
        self.assertTrue(result['metadata_command_sequence_equal'])
        self.assertTrue(result['scope_check_passed'])
        self.assertEqual(saved, after)
