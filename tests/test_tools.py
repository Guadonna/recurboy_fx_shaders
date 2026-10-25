import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import signal
import sys
import unittest
from unittest.mock import patch
import zipfile

ROOT=Path(__file__).resolve().parents[1]

def module(name):
    spec=importlib.util.spec_from_file_location(name, ROOT/'tools'/(name+'.py'))
    value=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value

class PackageTests(unittest.TestCase):
    def test_release_reproducible_and_complete(self):
        package=module('package')
        first=package.build().read_bytes()
        second=package.build().read_bytes()
        self.assertEqual(first, second)
        with zipfile.ZipFile(io.BytesIO(first)) as archive:
            manifest=json.loads(archive.read('manifest.json'))
            shaders=[x for x in archive.namelist() if x.endswith('.frag')]
            self.assertEqual(sorted(shaders), sorted(x['file'] for x in manifest['effects']))
            self.assertEqual(len(shaders),11)
            for line in archive.read('SHA256SUMS').decode().splitlines():
                digest,name=line.split('  ',1)
                self.assertEqual(hashlib.sha256(archive.read(name)).hexdigest(),digest)
            self.assertTrue(all(not x.startswith('/') and '..' not in Path(x).parts for x in archive.namelist()))

    def test_texture_budgets_and_single_pass_contract(self):
        manifest=json.loads((ROOT/'manifest.json').read_text())
        for effect in manifest['effects']:
            source=(ROOT/effect['file']).read_text()
            main=source.split('void main()',1)[1]
            calls=len(re.findall(r'\b(?:texture2D|past)\s*\(',main))
            self.assertEqual(calls,effect['texture_reads'],effect['file'])
            self.assertLessEqual(calls,7)
            self.assertNotRegex(source,r'\b(?:for|while)\s*\(')
            self.assertNotIn('#include',source)

class HealthTests(unittest.TestCase):
    def setUp(self):
        self.health=module('pi_health')

    def run_monitor(self,temp,flags,pid=False):
        argv=['pi_health.py','--duration','1']
        if pid: argv+=['--pid','1234']
        def read(path):
            if path.name=='comm':return 'recurBOY\n'
            return '1234 (recurBOY) ' + ' '.join(['0']*19+['123456'])
        with patch.object(sys,'argv',argv), patch.object(sys,'stdout',io.StringIO()), \
             patch.object(sys,'stderr',io.StringIO()), \
             patch.object(self.health,'temperature',return_value=temp), \
             patch.object(self.health,'throttled',return_value=flags), \
             patch.object(self.health.time,'monotonic',side_effect=[0,2,2]), \
             patch.object(self.health.Path,'read_text',read), \
             patch.object(self.health.os,'kill') as kill:
            code=self.health.main()
            return code, kill.call_args_list

    def test_overheat_pauses_only_selected_process(self):
        code,calls=self.run_monitor(70,0,pid=True)
        self.assertEqual(code,2)
        self.assertEqual(calls[-1].args,(1234,signal.SIGSTOP))

    def test_monitor_only_never_signals(self):
        code,calls=self.run_monitor(71,0)
        self.assertEqual(code,2)
        self.assertEqual(calls,[])

    def test_active_throttling_pauses(self):
        code,calls=self.run_monitor(50,4,pid=True)
        self.assertEqual(code,2)
        self.assertEqual(calls[-1].args,(1234,signal.SIGSTOP))

    def test_historical_flags_do_not_pause(self):
        code,calls=self.run_monitor(50,0x50000,pid=True)
        self.assertEqual(code,0)
        self.assertEqual(len(calls),1) # initial permission check only

    def test_missing_sensor_pauses_guarded_process(self):
        with patch.object(self.health.Path,'read_text',side_effect=OSError('sensor missing')):
            with self.assertRaises(OSError): self.health.temperature()
        with patch.object(sys,'argv',['pi_health.py','--pid','1234']), \
             patch.object(sys,'stdout',io.StringIO()), patch.object(sys,'stderr',io.StringIO()), \
             patch.object(self.health.Path,'read_text',side_effect=['recurBOY','0 (recurBOY) '+' '.join(['0']*20),'0 (recurBOY) '+' '.join(['0']*20)]), \
             patch.object(self.health,'temperature',side_effect=OSError('missing')), \
             patch.object(self.health.os,'kill') as kill:
            self.assertEqual(self.health.main(),2)
            self.assertEqual(kill.call_args.args,(1234,signal.SIGSTOP))

if __name__=='__main__': unittest.main()
