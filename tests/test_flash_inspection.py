import struct,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from inspect_flash_dump import inspect_dump,FLASH_SIZE,START,END
class FlashInspectionTests(unittest.TestCase):
    def make_dump(self):return bytearray(b'\xff')*FLASH_SIZE
    def place_object(self,data,offset,flags=0):
        data[offset:offset+292]=bytes(292)
        struct.pack_into('<IBBHI',data,offset,3,12,1,flags,292)
        struct.pack_into('<i',data,offset+20,4)
        data[offset+41]=6
    def test_size_and_erased_window(self):
        with self.assertRaises(ValueError):inspect_dump(bytes(124))
        result=inspect_dump(self.make_dump())
        self.assertEqual(result['fully_erased_0xff_sectors'],94)
        self.assertEqual(result['object_header_candidates'],[])
    def test_bounded_read_only_candidates(self):
        data=self.make_dump();self.place_object(data,START+64);self.place_object(data,64)
        before=bytes(data)
        result=inspect_dump(data)
        self.assertEqual(data,before)
        candidates=result['object_header_candidates']
        self.assertEqual(len(candidates),1)
        self.assertEqual(candidates[0]['unverified_fields']['language_index'],6)
        self.assertIn('not verified',candidates[0]['recognition'])
    def test_encrypted_crossing_and_truncated_not_decoded(self):
        data=self.make_dump()
        self.place_object(data,START+64,flags=1)
        self.place_object(data,START+4096-40)
        struct.pack_into('<IBBHI',data,END-12,3,12,1,0,292)
        candidates=inspect_dump(data)['object_header_candidates']
        self.assertEqual(len(candidates),3)
        self.assertTrue(all('unverified_fields' not in c for c in candidates))
        self.assertFalse(candidates[-1]['within_region'])
if __name__=='__main__':unittest.main()
