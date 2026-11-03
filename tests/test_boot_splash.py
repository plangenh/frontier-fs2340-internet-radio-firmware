"""Synthetic FSSP records, not manufacturer imagery."""
import struct
import sys
import unittest
import zlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from inspect_boot_splash import inspect_splash,SPLASH_START,PIXEL_BYTES,FLASH_SIZE,crc16
from deflate_transcode import transcode


def fixture(pixels=b'\0\0'*(320*240)):
    d=bytearray(b'\xff')*FLASH_SIZE;d[0x20:0x24]=b'FSSP';struct.pack_into('<I',d,0x24,SPLASH_START)
    compressor=zlib.compressobj(wbits=-15)
    encoded=transcode(compressor.compress(pixels)+compressor.flush(),'lsb','msb').data
    record=b'FSSP'+struct.pack('<I',len(encoded))+encoded+crc16(encoded).to_bytes(2,'big')
    d[SPLASH_START:SPLASH_START+len(record)]=record
    return d


class BootSplashTests(unittest.TestCase):
    def test_complete_image_and_unchanged_input(self):
        d=fixture();before=bytes(d);r=inspect_splash(d)
        self.assertTrue(r['crc_valid']);self.assertEqual(r['decoded_size'],PIXEL_BYTES);self.assertEqual(d,before)

    def test_checksum_rejected(self):
        d=fixture();d[SPLASH_START+9]^=1
        with self.assertRaises(ValueError):inspect_splash(d)

    def test_length_bounds_rejected(self):
        d=fixture();struct.pack_into('<I',d,SPLASH_START+4,0xffffffff)
        with self.assertRaises(ValueError):inspect_splash(d)

    def test_decoded_size_rejected(self):
        for pixels in [b'\0'*10,b'\0'*(PIXEL_BYTES+1)]:
            with self.subTest(size=len(pixels)):
                with self.assertRaises(ValueError):inspect_splash(fixture(pixels))

if __name__=='__main__':unittest.main()
