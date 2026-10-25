import hashlib,importlib.util,io,json,unittest,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class PackageTests(unittest.TestCase):
 def test_complete_reproducible_archive(self):
  spec=importlib.util.spec_from_file_location('pack',ROOT/'tools/package.py');pack=importlib.util.module_from_spec(spec);spec.loader.exec_module(pack)
  data=pack.build().read_bytes();self.assertEqual(data,pack.build().read_bytes())
  with zipfile.ZipFile(io.BytesIO(data)) as z:
   m=json.loads(z.read('manifest.json'));actual={n for n in z.namelist() if n.endswith('.frag')}
   self.assertEqual(len(actual),5);self.assertEqual(actual,{e['file'] for e in m['effects']})
   self.assertTrue(all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in z.namelist()))
   for line in z.read('SHA256SUMS').decode().splitlines():
    h,n=line.split('  ',1);self.assertEqual(hashlib.sha256(z.read(n)).hexdigest(),h)
if __name__=='__main__':unittest.main()
