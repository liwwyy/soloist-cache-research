exec(open('.soloist-investigation/page_probe.py').read())
class Decrypt(gdb.Breakpoint):
 def stop(self):
  try:
   inf=gdb.selected_inferior();v={k:int(gdb.parse_and_eval('$'+reg)) for k,reg in [('context','rdi'),('offset','rsi'),('input','rdx'),('output','rcx'),('length','r8')]}
   v['prefix']=bytes(inf.read_memory(v['input'],min(32,v['length']))).hex();(root/'decrypt-call.json').write_text(json.dumps(v));(root/'decrypt-context.bin').write_bytes(bytes(inf.read_memory(v['context'],0x310)));(root/'decrypt-stack.txt').write_text(gdb.execute('bt 15',to_string=True));return True
  except Exception as e:(root/'decrypt-probe-errors.txt').write_text(str(e));return False
Decrypt('*'+hex(base+0x10f9400))
