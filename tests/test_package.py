import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]
module_spec=importlib.util.spec_from_file_location('package',ROOT/'tools/package.py')
package=importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(package)

class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        (self.root/'collections').mkdir()
        entries=[]
        for name in ['first','second']:
            folder=self.root/'Shaders'/name
            folder.mkdir(parents=True)
            (folder/f'{name}.frag').write_text('void main() { gl_FragColor=vec4(1.0); }\n')
            (self.root/'collections'/f'{name}.md').write_text(f'# {name}\n')
            entries.append(dict(id=name,version='0.1.0',shaders=[dict(file=f'{name}.frag')]))
        self.spec=dict(version=package.VERSION,host='stock',mode='PATTERN',collections=entries)
        self.save()

    def save(self):
        (self.root/'manifest.json').write_text(json.dumps(self.spec))

    def test_common_zip_has_only_separate_flat_shader_folders(self):
        assets=package.build(self.root)
        with zipfile.ZipFile(assets[-1]) as archive:
            self.assertEqual(set(archive.namelist()), {'first/first.frag','second/second.frag'})
        for name,path in zip(['first','second'],assets):
            with zipfile.ZipFile(path) as archive:
                self.assertEqual(set(archive.namelist()),{'README.md',f'Shaders/{name}/{name}.frag'})

    def test_unlisted_shader_is_rejected(self):
        (self.root/'Shaders/first/unlisted.frag').write_text('extra')
        with self.assertRaises(ValueError): package.build(self.root)

    def test_extra_nested_fx_or_docs_in_common_zip_are_rejected(self):
        for name in ['first/Fx/first.frag','first/README.md','first/Shaders/first.frag']:
            path=self.root/'tampered.zip'
            with zipfile.ZipFile(path,'w') as archive:
                archive.writestr('first/first.frag',b'shader')
                archive.writestr(name,b'unwanted')
            with self.assertRaises(ValueError):
                package.verify_zip(path,{'first/first.frag':b'shader'})

    def test_changed_shader_bytes_are_rejected(self):
        path=self.root/'tampered.zip'
        with zipfile.ZipFile(path,'w') as archive: archive.writestr('first/a.frag',b'wrong')
        with self.assertRaises(ValueError): package.verify_zip(path,{'first/a.frag':b'correct'})

    def test_empty_release_is_rejected(self):
        self.spec['collections']=[]
        self.save()
        with self.assertRaises(ValueError): package.build(self.root)

if __name__=='__main__': unittest.main()
