import importlib.util,json,struct,sys,unittest,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from deflate_transcode import transcode
from analyze_firmware import validate_commands
class AnalysisChecks(unittest.TestCase):
    def test_transcode_roundtrip(self):
        for level in (0,1,6,9):
            for payload in (b'',b'abc'*500,bytes(range(256))*20):
                encoder=zlib.compressobj(level=level,wbits=-15)
                standard=encoder.compress(payload)+encoder.flush()
                vendor=transcode(standard,'lsb','msb')
                restored=transcode(vendor.data,'msb','lsb',restore_padding=vendor.trailing_value)
                self.assertEqual(restored.data,standard)
                self.assertEqual(zlib.decompress(restored.data,-15),payload)
    def test_block_boundary_rejects_split_load(self):
        valid=struct.pack('<4I',0,4,0x1234,8)+b'12345678'
        self.assertEqual(validate_commands(valid),len(valid))
        with self.assertRaisesRegex(ValueError,'boundary'):validate_commands(valid[:-1])
        with self.assertRaises(ValueError):validate_commands(valid[:8])
    def test_public_inventory(self):
        d=json.loads((ROOT/'site/data/menus.json').read_text());forms=d['forms']
        self.assertEqual(len(forms),39)
        self.assertEqual(sum(f['item_count'] for f in forms),102)
        self.assertEqual(sum(i['label']['id'] is not None and i['label']['id']<1056 for f in forms for i in f['items']),95)
        by={f['address']:f for f in forms}
        self.assertEqual(by['0x32aefa00']['item_count'],12)
        self.assertEqual(by['0x32aef9c0']['item_count'],10)
        for f in forms:
            self.assertEqual(f['item_count'],len(f['items']))
            for i in f['items']:
                if i.get('submenu_descriptor_found'):self.assertIn(i['submenu_candidate'],by)
if __name__=='__main__':unittest.main()
