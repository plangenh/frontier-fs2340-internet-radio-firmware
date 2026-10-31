import importlib.util,json,struct,sys,unittest,zlib,subprocess,tempfile
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
    def test_menu_row_crossing_zero_fill_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp)
            descriptor_base=0x32ae0000;row_base=0x32af0000
            words=[0,4,(162<<16)|15,0,0x280000,0xc80140,1,row_base|0x80000000,0,0,0,0,0,0,0,0,0]
            header=struct.pack('<17I',*words)
            tail=struct.pack('<4I',(317<<16)|15,0,0xb20b41b0,0)
            (d/'header.dat').write_bytes(header);(d/'tail.dat').write_bytes(tail)
            manifest={'sha256':'48a9da85d2580ee7fffde0f204ee2046ae0e300a2f23f1e4a6a5e3b299bd0dc3','modules':[{'name':'meta_t1.elf','images':[{'address':descriptor_base,'file':'header.dat'},{'address':row_base+4,'file':'tail.dat'}],'fills':[{'address':row_base,'size':4,'value':0}]}]}
            (d/'manifest.json').write_text(json.dumps(manifest))
            entries=[{'text':''} for _ in range(1056)]
            entries[162]={'text':'Network'};entries[317]={'text':'Network wizard'}
            (d/'locales.json').write_text(json.dumps([{'entries':entries} for _ in range(7)]))
            subprocess.run([sys.executable,str(ROOT/'tools/extract_menus.py'),str(d/'manifest.json'),str(d/'locales.json'),'--output',str(d/'out')],check=True,capture_output=True,text=True)
            forms=json.loads((d/'out/list_forms.json').read_text())['forms']
            self.assertEqual(len(forms),1)
            self.assertEqual(forms[0]['items'][0]['label']['en'],'Network wizard')
            self.assertEqual(forms[0]['items'][0]['flags'],'0x0')
    def test_public_inventory(self):
        d=json.loads((ROOT/'site/data/menus.json').read_text());forms=d['forms']
        self.assertEqual(len(forms),39)
        self.assertEqual(sum(f['item_count'] for f in forms),102)
        self.assertEqual(sum(i['label']['id'] is not None and i['label']['id']<1056 for f in forms for i in f['items']),96)
        by={f['address']:f for f in forms}
        self.assertEqual(by['0x32aefa00']['item_count'],12)
        network=by['0x32afbe08']['items']
        self.assertEqual(network[0]['label']['id'],317)
        self.assertEqual(network[0]['label']['en'],'Network wizard')
        self.assertEqual(network[0]['flags'],'0x0')
        self.assertEqual(by['0x32aef9c0']['item_count'],10)
        for f in forms:
            self.assertEqual(f['item_count'],len(f['items']))
            for i in f['items']:
                if i.get('submenu_descriptor_found'):self.assertIn(i['submenu_candidate'],by)
if __name__=='__main__':unittest.main()
