import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('package_all', ROOT/'tools/package_all.py')
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)


class DeviceBundleTests(unittest.TestCase):
    def source(self, folder, name):
        path = folder/(name+'.zip')
        files = {
            'Fx/example.frag': ('// '+name+'\nvoid main() {}\n').encode(),
            'manifest.json': json.dumps({'collection': name, 'effects': [{'file': 'Fx/example.frag'}]}).encode(),
            'README.md': b'Collection instructions',
            'docs/preview.png': b'Preview placeholder',
        }
        files['SHA256SUMS'] = ''.join(hashlib.sha256(data).hexdigest()+'  '+n+'\n' for n,data in files.items()).encode()
        with zipfile.ZipFile(path, 'w') as z:
            for n,data in files.items(): z.writestr(n,data)
        return path

    def test_only_flat_shader_folders_and_reproducible_contents(self):
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td);sources=[self.source(folder,'feedback'),self.source(folder,'datamosh')]
            a,b=folder/'a.zip',folder/'b.zip'
            package.build(sources,a,'1.1.1');package.build(sources[::-1],b,'1.1.1')
            self.assertEqual(a.read_bytes(),b.read_bytes())
            self.assertEqual(package.verify_bundle(a,sources),2)
            with zipfile.ZipFile(a) as z:
                self.assertEqual(set(z.namelist()),{'feedback/example.frag','datamosh/example.frag'})
                for source in sources:
                    with zipfile.ZipFile(source) as original:
                        self.assertEqual(z.read(source.stem+'/example.frag'),original.read('Fx/example.frag'))

    def test_rejects_extra_files_old_nesting_and_changed_shader(self):
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td);source=self.source(folder,'feedback')
            with zipfile.ZipFile(source) as z:shader=z.read('Fx/example.frag')
            for files in [
                {'feedback/example.frag':shader,'feedback/README.md':b'extra'},
                {'feedback/Fx/example.frag':shader},
                {'feedback/example.frag':b'changed'},
            ]:
                target=folder/'bad.zip'
                with zipfile.ZipFile(target,'w') as z:
                    for name,data in files.items():z.writestr(name,data)
                with self.assertRaises(AssertionError):package.verify_bundle(target,[source])

if __name__=='__main__':unittest.main()
