import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'collections/datamosh'

class DatamoshPackageTests(unittest.TestCase):
    def test_standalone_archive_and_integrity(self):
        spec=importlib.util.spec_from_file_location('package_collection',ROOT/'tools/package_collection.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        data=module.build('datamosh').read_bytes()
        self.assertEqual(data,module.build('datamosh').read_bytes())
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            manifest=json.loads(archive.read('manifest.json'))
            self.assertEqual(manifest['collection'],'datamosh')
            shaders={n for n in archive.namelist() if n.endswith('.frag')}
            self.assertEqual(len(shaders),5)
            self.assertEqual(shaders,{e['file'] for e in manifest['effects']})
            self.assertTrue(all(n.startswith('Fx/dm') for n in shaders))
            self.assertNotIn('docs/fx-fourth-knob.patch',archive.namelist())
            for line in archive.read('SHA256SUMS').decode().splitlines():
                digest,name=line.split('  ',1)
                self.assertEqual(hashlib.sha256(archive.read(name)).hexdigest(),digest)
            self.assertFalse(any(Path(n).is_absolute() or '..' in Path(n).parts for n in archive.namelist()))
        for invalid in ['../datamosh','/tmp/datamosh','datamosh/sub']:
            with self.assertRaises(ValueError):module.build(invalid)

    def test_native_interface_and_budgets(self):
        manifest=json.loads((BASE/'manifest.json').read_text())
        for effect in manifest['effects']:
            source=(BASE/effect['file']).read_text()
            main=source.split('void main()',1)[1]
            self.assertEqual(len(re.findall(r'\b(?:texture2D|past)\s*\(',main)),effect['texture_reads'])
            self.assertLessEqual(effect['texture_reads'],6)
            self.assertEqual(effect['passes'],1)
            self.assertNotRegex(source,r'\b(?:for|while)\s*\(')
            self.assertNotIn('#include',source)
            self.assertNotRegex(source,r'\bu_fx_|\bu_x3\b')

if __name__=='__main__':unittest.main()
