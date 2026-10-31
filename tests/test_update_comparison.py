import hashlib,struct,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from compare_update_to_dump import compare_images,parse_update,FLASH_SIZE,PAYLOAD_BASE,VERSION
class UpdateComparisonTests(unittest.TestCase):
    def update(self):
        payload=bytearray(range(256))*2;payload[128:132]=b'enco'
        header=bytearray(124);struct.pack_into('<3I',header,0,0x1176,124,1)
        header[12:44]=VERSION.encode().ljust(32,b' ')
        header[44:108]=b'ir-cui-FS2340-0000-0444'.ljust(64,b' ')
        header[108:124]=hashlib.md5(payload).digest()
        return bytes(header+payload),bytes(payload)
    def test_exact_and_bounded_mismatch(self):
        update,payload=self.update();dump=bytearray(b'\xff')*FLASH_SIZE
        dump[PAYLOAD_BASE:PAYLOAD_BASE+len(payload)]=payload
        self.assertTrue(compare_images(dump,update)['exact_payload_match'])
        dump[0]=17;self.assertTrue(compare_images(dump,update)['exact_payload_match'])
        dump[PAYLOAD_BASE+7]^=1;before=bytes(dump)
        result=compare_images(dump,update)
        self.assertEqual(result['different_bytes'],1)
        self.assertEqual(result['first_difference_intervals'][0]['start'],hex(PAYLOAD_BASE+7))
        self.assertEqual(before,dump)
    def test_outer_validation(self):
        update,_=self.update()
        for offset in (0,4,8,12,44,108,124):
            corrupt=bytearray(update);corrupt[offset]^=1
            with self.assertRaises(ValueError):parse_update(corrupt)
        with self.assertRaises(ValueError):compare_images(bytes(10),update)
if __name__=='__main__':unittest.main()
