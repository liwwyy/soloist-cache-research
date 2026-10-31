"""Match captured storage cipher parameters to a cached content-stream prefix."""
import argparse,json
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher,algorithms,modes
p=argparse.ArgumentParser();p.add_argument('experiment');a=p.parse_args();root=Path(a.experiment)
prefix=bytes.fromhex(json.loads((root/'decrypt-call.json').read_text())['prefix'])
rows=[json.loads(s) for s in (root/'storage.jsonl').read_text().splitlines()];ivs={bytes.fromhex(r['iv']) for r in rows};keys=set()
for f in root.glob('storage-schedule-*.bin'):
 schedule=f.read_bytes()
 for start in range(0,len(schedule)-15,16):
  k=schedule[start:start+16];keys.update((k,k[::-1],b''.join(k[i:i+4][::-1] for i in range(0,16,4))))
hits=[]
for f in (root/'cache').rglob('*.file'):
 with f.open('rb') as source:raw=source.read(65536)
 for key in keys:
  for iv in ivs:
   for offset in (0,400):
    plain=Cipher(algorithms.AES(key),modes.CTR(iv)).decryptor().update(raw[offset:])
    if plain.startswith(prefix):hits.append({'file':str(f.resolve()),'position':0,'key':key.hex(),'iv':iv.hex(),'offset':offset})
(root/'outer-results.json').write_text(json.dumps(hits,indent=2));(root/'outer-results.json').chmod(0o600)
print('Matching cache/parameter combinations:',len(hits))
if not hits:raise SystemExit(1)
