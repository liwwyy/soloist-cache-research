# Experimental probe for the pinned Linux x86_64 build only.
import gdb,os,struct,json
from pathlib import Path
root=Path(os.environ.get('SOLOIST_TEST_OUTPUT','.soloist-investigation'));out=root/'parser-pages';out.mkdir(exist_ok=True)
inf=gdb.selected_inferior();base=None
for line in open('/proc/'+str(inf.pid)+'/maps'):
 fields=line.split()
 if fields[-1]==os.environ.get('SOLOIST_BINARY_PATH','/tmp/soloist-investigation/soloist') and fields[2]=='00000000':base=int(fields[0].split('-')[0],16);break
if base is None:raise RuntimeError('Executable mapping not found')
class Page(gdb.Breakpoint):
 def stop(self):
  try:
   inf=gdb.selected_inferior();p=int(gdb.parse_and_eval('$rax'));h=bytes(inf.read_memory(p,27))
   if h[:5]!=b'OggS\0':return False
   n=h[26];laces=bytes(inf.read_memory(p+27,n));length=27+n+sum(laces);raw=bytes(inf.read_memory(p,length));serial,seq=struct.unpack_from('<II',h,14)
   (out/f'{serial}-{seq:05}.oggpage').write_bytes(raw)
   with (root/'parser-events.jsonl').open('a') as f:f.write(json.dumps({'sequence':seq,'serial':serial,'bytes':length,'flags':h[5],'granule':struct.unpack_from('<q',h,6)[0]})+'\n')
  except Exception as e:
   with (root/'parser-errors.txt').open('a') as f:f.write(str(e)+'\n')
  return False
Page('*'+hex(base+0x119a487))
