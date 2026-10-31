import gdb,json,time
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher,algorithms,modes
root=Path(__import__('os').environ['SOLOIST_TEST_OUTPUT']);t=time.monotonic()
try:
 d=json.loads((root/'decrypt-call.json').read_text());hits=json.loads((root/'outer-results.json').read_text());h=max(hits,key=lambda x:Path(x['file']).stat().st_size);raw=Path(h['file']).read_bytes()[h['offset']:];enc=Cipher(algorithms.AES(bytes.fromhex(h['key'])),modes.CTR(bytes.fromhex(h['iv']))).decryptor().update(raw)
 assert enc.startswith(bytes.fromhex(d['prefix'])), 'Unwrapped cache differs from current decryptor input'
 for bp in gdb.breakpoints():bp.enabled=False
 ptr=int(gdb.parse_and_eval('(void*)malloc('+str(len(enc))+')'));gdb.selected_inferior().write_memory(ptr,enc)
 function=base+0x10f9400
 gdb.execute('call ((void (*)(void*, unsigned long, void*, void*, unsigned long))'+hex(function)+')('+hex(d['context'])+',0,'+hex(ptr)+','+hex(ptr)+','+str(len(enc))+')',to_string=True)
 plain=bytes(gdb.selected_inferior().read_memory(ptr,len(enc)));(root/'native-decrypted.bin').write_bytes(plain);(root/'native-export-result.json').write_text(json.dumps({'seconds':time.monotonic()-t,'bytes':len(plain),'ogg':plain.find(b'OggS'),'flac':plain.find(b'fLaC')},indent=2))
except Exception as e:(root/'native-export-error.txt').write_text(str(e))
