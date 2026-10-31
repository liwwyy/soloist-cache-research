import sys,unittest,struct
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from offline_cache_decrypt import extract_ogg

def page(seq,flags,granule,payload=b'synthetic'):
 h=bytearray(b'OggS\x00'+bytes([flags])+struct.pack('<qIII',granule,0,seq,0)+bytes([1,len(payload)])+payload)
 crc=0
 for c in h:
  crc^=c<<24
  for _ in range(8):crc=((crc<<1)^0x04c11db7 if crc&0x80000000 else crc<<1)&0xffffffff
 struct.pack_into('<I',h,22,crc)
 return bytes(h)

class ContainerValidation(unittest.TestCase):
 def test_complete_stream(self):
  data=page(0,2,0)+page(1,4,44100)
  audio,result=extract_ogg(data,0)
  self.assertEqual(audio,data);self.assertEqual(result['pages'],2);self.assertEqual(result['duration_seconds'],1);self.assertTrue(result['end_of_stream'])
 def test_bad_crc_rejected(self):
  data=bytearray(page(0,6,44100));data[-1]^=1
  with self.assertRaisesRegex(ValueError,'CRC'):extract_ogg(data,0)
 def test_sequence_gap_rejected(self):
  with self.assertRaisesRegex(ValueError,'sequence'):extract_ogg(page(0,2,0)+page(2,4,44100),0)
 def test_missing_eos_rejected(self):
  with self.assertRaises(ValueError):extract_ogg(page(0,2,0),0)
 def test_truncated_page_rejected(self):
  with self.assertRaises(ValueError):extract_ogg(page(0,6,44100)[:-2],0)
 def test_prefix_and_trailing_bytes(self):
  audio=page(0,6,44100);actual,result=extract_ogg(b'prefix'+audio+b'tail',6)
  self.assertEqual(actual,audio);self.assertEqual(result['trailing_bytes'],4)

if __name__=='__main__':unittest.main()
