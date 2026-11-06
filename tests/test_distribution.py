"""Verify the committed install ZIP can work without developer/showcase files."""
from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]


class DistributionTests(unittest.TestCase):
    def test_committed_archive_is_small_and_exports_in_isolation(self):
        build=(ROOT/'build').resolve();build.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='skill-package-',dir=build) as folder:
            folder=Path(folder).resolve()
            self.assertTrue(folder.is_relative_to(build))
            archive=folder/'skill.zip'
            subprocess.run(['git','archive','--format=zip','--output',str(archive),'HEAD'],cwd=ROOT,check=True)
            installed=folder/'installed'
            with zipfile.ZipFile(archive) as package:
                files=[n for n in package.namelist() if not n.endswith('/')]
                for name in files:
                    p=Path(name)
                    self.assertFalse(p.is_absolute() or '..' in p.parts)
                    self.assertNotIn(p.parts[0],{'tests','.github','docs','examples'})
                    self.assertNotIn(p.suffix,{'.pptx','.png','.gif','.jpg'})
                self.assertEqual({n for n in files if n.startswith('references/')},{
                    'references/scene-schema.md','references/components.md','references/rendering.md'})
                self.assertIn('vendor/figureforge/LICENSE',files)
                self.assertIn('vendor/figureforge/UPSTREAM.md',files)
                package.extractall(installed)
            # Catch accidental inclusion of generated data or large examples.
            self.assertLess(sum(p.stat().st_size for p in installed.rglob('*') if p.is_file()),1_000_000)
            task=folder/'task';task.mkdir()
            author=task/'author.py'
            author.write_text('''from pathlib import Path
import sys
from PIL import Image
sys.path.insert(0,str(Path(sys.argv[1])/'scripts'))
from scientific_components import Figure
f=Figure(600,360)
f.chain('model',30,40,['Encoder','Decoder'],120,45,gap=30,fontSize=20)
f.text('loss',30,130,260,fontSize=24,runs=[{'text':'L'},{'text':'cls','fontSize':14,'baselineShift':'sub'}])
f.image_crop('sample',420,230,80,60,{'x':20,'y':20,'w':70,'h':50},purpose='texture')
Image.new('RGB',(600,360),(28,100,160)).save('source.png')
f.save('scene.json')
''',encoding='utf-8')
            env=dict(os.environ);env.pop('PYTHONPATH',None)
            subprocess.run([sys.executable,str(author),str(installed)],cwd=task,env=env,check=True,capture_output=True)
            result=subprocess.run([sys.executable,'-X','utf8',str(installed/'scripts/build_figure.py'),
                '--scene',str(task/'scene.json'),'--source',str(task/'source.png'),
                '--output',str(task/'figure.pptx'),'--renderer','none'],
                cwd=task,env=env,check=True,capture_output=True,text=True,encoding='utf-8')
            checked=json.loads(result.stdout)
            self.assertTrue(checked['auditPassed'],checked)
            self.assertEqual(checked['objects'],7)
            self.assertEqual(checked['images'],1)
            self.assertEqual(checked['warningCount'],0)
            self.assertTrue((task/'figure.pptx').is_file())


if __name__=='__main__':unittest.main()
