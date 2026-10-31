exec(open('.soloist-investigation/page_probe.py').read())
class Storage(gdb.Breakpoint):
 count=0
 def stop(self):
  if self.count>=4:return False
  try:
   inf=gdb.selected_inferior();ctx=int(gdb.parse_and_eval('$rdi'));ivp=int(gdb.parse_and_eval('$rsi'));vt=struct.unpack('<Q',bytes(inf.read_memory(ctx,8)))[0];entry={'context':ctx,'vtable':vt,'iv':bytes(inf.read_memory(ivp,16)).hex(),'offset':int(gdb.parse_and_eval('$r12')),'length':int(gdb.parse_and_eval('$r14')),'functions':[struct.unpack('<Q',bytes(inf.read_memory(vt+i,8)))[0]-base for i in (0x20,0x38,0x40)]}
   (root/f'storage-context-{self.count}.bin').write_bytes(bytes(inf.read_memory(ctx,1024)))
   inner=struct.unpack('<Q',bytes(inf.read_memory(ctx+8,8)))[0];(root/f'storage-inner-{self.count}.bin').write_bytes(bytes(inf.read_memory(inner,2048)));schedule=struct.unpack('<Q',bytes(inf.read_memory(inner+8,8)))[0];(root/f'storage-schedule-{self.count}.bin').write_bytes(bytes(inf.read_memory(schedule,240)));entry['inner_vtable']=[struct.unpack('<Q',bytes(inf.read_memory(struct.unpack('<Q',bytes(inf.read_memory(inner,8)))[0]+i,8)))[0]-base for i in (0x28,)]
   with (root/'storage.jsonl').open('a') as f:f.write(json.dumps(entry)+'\n')
   self.count+=1
  except Exception as e:(root/'storage-errors.txt').write_text(str(e))
  return False
Storage('*'+hex(base+0xe562e1))
