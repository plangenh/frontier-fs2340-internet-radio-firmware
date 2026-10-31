import json,struct,pathlib
import argparse
parser=argparse.ArgumentParser(description='Extract static menu candidates from a private original memory manifest.')
parser.add_argument('manifest',type=pathlib.Path)
parser.add_argument('locales',type=pathlib.Path)
parser.add_argument('--output',type=pathlib.Path,required=True)
args=parser.parse_args()
p=args.manifest.resolve().parent
out=args.output.resolve()
manifest=json.loads(args.manifest.read_text())
if manifest['sha256']!='48a9da85d2580ee7fffde0f204ee2046ae0e300a2f23f1e4a6a5e3b299bd0dc3': raise ValueError('Unsupported original')
out.mkdir(parents=True,exist_ok=False)
mod=next(x for x in manifest['modules'] if x['name']=='meta_t1.elf')
ims=[(x['address'],(p/x['file']).read_bytes()) for x in mod['images']]
loc=json.loads(args.locales.read_text());en=loc[0]['entries'];de=loc[6]['entries']

def read(addr,n):
 addr&=0x7fffffff
 out=bytearray()
 while len(out)<n:
  pos=addr+len(out)
  for a,b in ims:
   if a<=pos<a+len(b):
    take=min(n-len(out),a+len(b)-pos);out.extend(b[pos-a:pos-a+take]);break
  else:raise ValueError(hex(pos))
 return bytes(out)
def label(w):
 i=w>>16
 return {'id':i,'en':en[i]['text'],'de':de[i]['text']} if w&65535==15 and i<1056 else None
forms={}
for base,b in ims:
 for off in range(0,len(b)-64,4):
  w=struct.unpack_from('<16I',b,off)
  if not (w[0]<=4 and w[1]<=4) or not label(w[2]) or w[3]!=0 or not 0<=w[6]<=80 or w[4]!=0x280000 or w[5]!=0xc80140:continue
  try:
   rows=[]
   for i in range(w[6]):
    addr=(w[7]&0x7fffffff)+i*20
    try:r=struct.unpack('<5I',read(addr,20))
    except ValueError:
     rows.append({'address':f'0x{addr:08x}','label':{'id':None,'en':'[runtime-populated / unavailable initial bytes]','de':'[runtime-populated]'},'flags':None,'value':None,'callback':None,'argument':None,'submenu_candidate':None});continue
    lab=label(r[1]);
    if not lab:
     if r[1]==0xffff000f:lab={'id':65535,'en':'[dynamic label]','de':'[dynamic label]'}
     else:raise ValueError('not label')
    rows.append(dict(address=f'0x{addr:08x}',flags=f'0x{r[0]:x}',label=lab,value=f'0x{r[2]:x}',callback=f'0x{r[3]:08x}',argument=f'0x{r[4]:08x}',submenu_candidate=f'0x{r[4]&0x7fffffff:08x}' if r[3]==0xb20cbbd4 else None))
   addr=base+off;forms[f'0x{addr:08x}']=dict(address=f'0x{addr:08x}',title=label(w[2]),items_address=f'0x{w[7]&0x7fffffff:08x}',item_count=w[6],callback=f'0x{w[12]:08x}',geometry_words=[f'0x{x:08x}' for x in w[4:6]],items=rows)
  except ValueError:pass
for form in forms.values():
 for item in form['items']:
  item['submenu_descriptor_found']=item['submenu_candidate'] in forms
result=dict(method='64-byte list-form family, header flags 0..4, subtype 0..4, tagged title and exact 0,40,320,200 geometry; 20-byte records with tagged locale IDs; edges via shared b20cbbd4 callback and pointer argument are static submenu candidates, not observed execution.',source_sha256=manifest['sha256'],forms=list(forms.values()),root_candidates=['0x32aefa00','0x32aef9c0'])
(out/'list_forms.json').write_text(json.dumps(result,indent=2,ensure_ascii=False))
lines=['# Static list-form inventory','','Recovered %d list descriptors using a strict structural pattern. These are compiled resources; model feature filtering can hide entries. Runtime-populated list entries are marked explicitly. Links through b20cbbd4 are strong submenu candidates, but function dispatch has not been revalidated in this pass.','']
lines[2]=lines[2]%len(forms)
for f in forms.values():
 lines+=['## '+f['title']['en']+' — '+f['address'],'', '| ID | English | German | Callback | Argument / submenu candidate |','|---:|---|---|---|---|']
 for it in f['items']:
  l=it['label'];lines.append(f"| {l['id']} | {l['en']} | {l['de']} | {it['callback']} | {it['argument']} |")
 lines.append('')
(out/'LIST-FORMS.md').write_text('\n'.join(lines))
print('forms',len(forms),'rows',sum(f['item_count'] for f in forms.values()))
for f in forms.values():print(f['address'],f['title']['en'],f['item_count'])
