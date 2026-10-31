import binascii
import hashlib
import struct
import sys
import unittest
import zlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from independent_loader_check import scan_commands, check_image
from deflate_transcode import transcode


def module():
    payload = bytes(4) + b'test\0'
    return struct.pack('<3I', 16, 0, len(payload)) + payload


def load(address=0x32000000, data=b'abc'):
    return struct.pack('<4I', 0, 4, address, len(data)) + data


def fixture(commands):
    encoder = zlib.compressobj(wbits=-15)
    compressed = encoder.compress(commands) + encoder.flush()
    encoded = transcode(compressed, 'lsb', 'msb').data
    raw = b'\x63' + encoded + (binascii.crc_hqx(encoded, 65535)^65535).to_bytes(2, 'big')
    image = bytearray(308)
    struct.pack_into('<3I', image, 0, 0x1176, 124, 1)
    image[252:256] = b'enco'
    struct.pack_into('<5I', image, 268, 1, 308-124+0x12000, len(raw)-2, 0, len(commands))
    image.extend(raw)
    image[108:124] = hashlib.md5(image[124:]).digest()
    return image


class IndependentLoaderTests(unittest.TestCase):
    def test_valid_and_overlap_reporting(self):
        image = fixture(module()+load()+load(data=b'xyz'))
        before = bytes(image)
        result = check_image(image)
        self.assertEqual(result['blocks'], 1)
        self.assertEqual(len(result['overlapping_writes']), 1)
        self.assertEqual(bytes(image), before)

    def test_command_faults(self):
        for command in (module()[:-1], load(), module()+load(0xffffffff),
                        module()+load()[:-1], struct.pack('<3I', 99, 0, 0),
                        struct.pack('<3I', 16, 0, 4)+bytes(4)):
            with self.assertRaises(ValueError):
                scan_commands(command)

    def test_container_faults_beyond_outer_checksum(self):
        valid = fixture(module()+load())
        for offset in (268+4, 268+8, 268+12, 268+16, 308, len(valid)-1):
            corrupt = bytearray(valid)
            corrupt[offset] ^= 1
            corrupt[108:124] = hashlib.md5(corrupt[124:]).digest()
            with self.assertRaises((ValueError, zlib.error)):
                check_image(corrupt)
        with self.assertRaises(ValueError):
            check_image(valid[:-1])

    def test_module_context_survives_block_boundary(self):
        name, _, _ = scan_commands(module())
        name, records, count = scan_commands(load(), name)
        self.assertEqual(name, 'test')
        self.assertEqual(count, 1)
        self.assertEqual(records[0]['length'], 3)
