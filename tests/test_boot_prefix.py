"""Synthetic boot-record fixtures; no manufacturer code or device data."""
import struct
import sys
import unittest
import zlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from inspect_boot_prefix import inspect_prefix, crc16, FLASH_SIZE, MAX_SECONDARY
from deflate_transcode import transcode


def fixture(secondary=b'synthetic secondary', following=0):
    dump=bytearray(b'\xff')*FLASH_SIZE
    struct.pack_into('<III',dump,0,0x01aa5500,0x100,0x12080)
    dump[12:14]=b'\0\0'
    dump[14:16]=crc16(dump[:14]).to_bytes(2,'big')
    for offset,tag,value in [(0x10,b'APPN',0x12000),(0x18,b'LNVS',0x7a1000),(0x20,b'FSSP',0x781000),(0x28,b'PEND',0x403c6b)]:
        dump[offset:offset+4]=tag; struct.pack_into('<I',dump,offset+4,value)
    compressor=zlib.compressobj(wbits=-15)
    encoded=transcode(compressor.compress(secondary)+compressor.flush(),'lsb','msb').data
    carrier=encoded+crc16(encoded).to_bytes(2,'big')
    record=bytearray(128);record[:8]=b'SECLCONF';struct.pack_into('<II',record,8,0x200,len(carrier))
    struct.pack_into('<IH',record,120,following,128);record[126:]=crc16(record[:126]).to_bytes(2,'big')
    dump[0x100:0x180]=record;dump[0x200:0x200+len(carrier)]=carrier
    return dump


class BootPrefixTests(unittest.TestCase):
    def test_valid_and_input_unchanged(self):
        dump=fixture();before=bytes(dump);report=inspect_prefix(dump)
        self.assertEqual(report['record_count'],1)
        self.assertEqual(report['secondary_decoded_size'],len(b'synthetic secondary'))
        self.assertEqual(dump,before)

    def test_crc_failures(self):
        for at in [0,0x110,0x200]:
            with self.subTest(at=at):
                dump=fixture();dump[at]^=1
                with self.assertRaises(ValueError):inspect_prefix(dump)

    def test_bad_links_rejected_with_valid_record_crc(self):
        for following in [0x100,0x101,0x12000]:
            with self.subTest(link=following):
                with self.assertRaises(ValueError):inspect_prefix(fixture(following=following))

    def test_decompression_limit(self):
        with self.assertRaises(ValueError):inspect_prefix(fixture(b'A'*(MAX_SECONDARY+1)))


if __name__=='__main__':unittest.main()
