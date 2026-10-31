"""Decrypt a prepared Soloist cache using track-specific saved material; no player or login."""
import argparse,hashlib,json,time,sys
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher,algorithms,modes

def extract_ogg(data,start):
 table=[]
 for i in range(256):
  v=i<<24
  for _ in range(8):v=((v<<1)^0x04c11db7 if v&0x80000000 else v<<1)&0xffffffff
  table.append(v)
 pos=start;expected=0;granule=0
 while True:
  if len(data)-pos<27:raise ValueError('Truncated Ogg page header')
  if data[pos:pos+5]!=b'OggS\0':raise ValueError('Missing Ogg page at '+str(pos))
  n=data[pos+26];length=27+n+sum(data[pos+27:pos+27+n]);page=data[pos:pos+length]
  if len(page)!=length:raise ValueError('Truncated page')
  seq=int.from_bytes(page[18:22],'little')
  if seq!=expected:raise ValueError('Page sequence gap')
  saved=int.from_bytes(page[22:26],'little');x=bytearray(page);x[22:26]=bytes(4);crc=0
  for c in x:crc=((crc<<8)^table[((crc>>24)^c)&255])&0xffffffff
  if saved!=crc:raise ValueError('Bad Ogg CRC at page '+str(seq))
  granule=int.from_bytes(page[6:14],'little',signed=True);expected+=1;pos+=length
  if page[5]&4:return data[start:pos],{'pages':expected,'end_of_stream':True,'final_granule':granule,'duration_seconds':granule/44100,'trailing_bytes':len(data)-pos}

def main():
 p=argparse.ArgumentParser();p.add_argument('bundle');p.add_argument('output');args=p.parse_args();t=time.monotonic();bp=Path(args.bundle).resolve();root=bp.parent;b=json.loads(bp.read_text());cache=Path(b['cache_file']).read_bytes()
 if hashlib.sha256(cache).hexdigest()!=b['cache_sha256']:raise ValueError('Cache differs from prepared input')
 enc=Cipher(algorithms.AES(bytes.fromhex(b['storage_key'])),modes.CTR(bytes.fromhex(b['storage_iv']))).decryptor().update(cache[b['storage_offset']:]);keystream=(root/b['keystream_file']).read_bytes()
 if len(enc)!=len(keystream):raise ValueError('Material length mismatch')
 plain=bytes(a^c for a,c in zip(enc,keystream));audio,validation=extract_ogg(plain,b['audio_offset']);Path(args.output).write_bytes(audio);validation.update({'bytes':len(audio),'sha256':hashlib.sha256(audio).hexdigest(),'elapsed_seconds':time.monotonic()-t});print(json.dumps(validation,indent=2))
if __name__=='__main__':main()
