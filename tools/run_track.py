import argparse,os,subprocess,signal,time,json,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--api-key-file',default='soloist-api-key.txt');p.add_argument('--binary',default='/tmp/soloist-investigation/soloist');p.add_argument('track');p.add_argument('--seconds',type=int,default=30);p.add_argument('--probe',default='page_probe.py');p.add_argument('--export',action='store_true');p.add_argument('--label',default='');a=p.parse_args();os.umask(0o077)
expected='3805746df067ebd586b9bdbd84e54fe49090df200ab430da2d7d29949ce2b540'
if hashlib.sha256(Path(a.binary).read_bytes()).hexdigest()!=expected:raise SystemExit('Unsupported Soloist build: hard-coded offsets require the exact researched binary.')
root=Path('.soloist-investigation');out=root/'tracks'/(a.track+a.label);out.mkdir(parents=True,exist_ok=True);k=Path(a.api_key_file).read_text().strip();env=os.environ.copy();env['SOLOIST_TEST_OUTPUT']=str(out);env['SOLOIST_BINARY_PATH']=str(Path(a.binary).resolve())

cmd=['gdb','-q','-batch','-ex','set debuginfod enabled off','-ex','set pagination off','-ex','set print thread-events off','-ex','starti','-ex','source '+str(root/a.probe),'-ex','continue','--args',a.binary,'-n','LiwMoosic Research','-k',k,'-D',str((root/'data').resolve()),'-C',str((out/'cache').resolve()),'-s','spotify:track:'+a.track]

if a.export:
 index=cmd.index('--args');cmd[index:index]=['-ex','source .soloist-investigation/native_export.py']
t=time.monotonic();proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,start_new_session=True,env=env)
try:log=proc.communicate(timeout=a.seconds)[0]
except subprocess.TimeoutExpired:
 os.killpg(proc.pid,signal.SIGTERM);log=proc.communicate()[0]
log=log.decode(errors='replace').replace(k,'[REDACTED]');(out/'debugger.log').write_text(log);print(log[-1400:]);print('Elapsed seconds',round(time.monotonic()-t,2))
