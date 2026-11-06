import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
BUILD=ROOT/'build';BUILD.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT/'scripts'))
from scientific_components import Figure
from build_figure import build
import figure_session as session
import open_artifact


class ComponentTests(unittest.TestCase):
    def test_gallery_exports_independent_shapes_and_native_math(self):
        spec=importlib.util.spec_from_file_location('components_demo',ROOT/'examples/components_demo.py')
        demo=importlib.util.module_from_spec(spec);spec.loader.exec_module(demo)
        f=demo.example()
        with tempfile.TemporaryDirectory(dir=BUILD) as folder:
            folder=Path(folder)
            source=f.save(folder/'input.json')
            result=build(source,folder/'figure.pptx',renderer='none')
            self.assertTrue(result['auditPassed'],result['errors'])
            self.assertEqual(result['images'],0)
            self.assertEqual(result['objectCount'],len(f.nodes))
            self.assertEqual(result['warnings'],[])
            with zipfile.ZipFile(result['output']) as pptx:
                xml=pptx.read('ppt/slides/slide1.xml').decode()
            self.assertIn('baseline="30000"',xml)
            self.assertIn('baseline="-25000"',xml)
            self.assertIn('<a:cubicBezTo>',xml)
            self.assertEqual(xml.count('<p:sp>'),len(f.nodes))
            connector=next(n for n in f.nodes if n['id']=='pipeline-arrow-1')
            self.assertEqual([connector[k] for k in ['x','y','x2','y2']],[190,118,238,118])
            self.assertEqual(next(n['d'] for n in f.nodes if n['id']=='routed'),'M 610 490 L 730 490 L 730 550 L 850 550')

    def test_crop_component_keeps_independent_placement_and_original_pixels(self):
        with tempfile.TemporaryDirectory(dir=BUILD) as folder:
            folder=Path(folder);Image.new('RGB',(400,200),(25,90,140)).save(folder/'source.png')
            f=Figure(400,200);f.text('title',10,10,300,'Source provenance',18)
            crop={'x':10,'y':20,'w':40,'h':30}
            f.image_crop('photo',200,100,80,60,crop,purpose='photo')
            crop['x']=99
            result=build(f.save(folder/'input.json'),folder/'figure.pptx',folder/'source.png',renderer='none')
            self.assertTrue(result['auditPassed'])
            audit=json.loads((folder/'figure.audit.json').read_text(encoding='utf-8'))
            self.assertEqual(audit['originalSourceVerifiedAssets'],1)
            self.assertEqual(f.assets[0]['crop']['x'],10)

    def test_rejects_ambiguous_components_without_silently_dropping_data(self):
        f=Figure(600,400)
        f.text('title',10,10,300,'Example',18)
        with self.assertRaisesRegex(ValueError,'duplicate'): f.rect('title',0,0,20,20)
        with self.assertRaisesRegex(ValueError,'match'): f.matrix('m',0,0,2,2,10,10,colors=['#fff'])
        with self.assertRaisesRegex(ValueError,'concatenated'): f.text('t',0,0,100,'wrong',runs=[{'text':'right'}])
        with self.assertRaisesRegex(ValueError,'Boxplot'): f.boxplot('b',20,10,15,30,20,40)
        with self.assertRaisesRegex(ValueError,'integer'): f.image_crop('p',0,0,20,20,{'x':0.5,'y':0,'w':10,'h':10})


class SessionTests(unittest.TestCase):
    def test_wall_clock_includes_all_stages_and_binds_to_reviewed_artifacts(self):
        with tempfile.TemporaryDirectory(dir=BUILD) as folder:
            folder=Path(folder);record=folder/'session.json'
            with patch.object(session,'now',side_effect=['2026-11-06T08:00:00+00:00','2026-11-06T08:01:00+00:00','2026-11-06T08:02:05+00:00']):
                session.start(record,'whole figure')
                with self.assertRaisesRegex(ValueError,'already exists'): session.start(record,'reset')
                session.mark(record,'source ready')
                ppt=folder/'figure.pptx';ppt.write_bytes(b'unit-test artifact')
                png=folder/'figure.png';Image.new('RGB',(20,20),'blue').save(png)
                report={'output':str(ppt),'auditPassed':True,'objectCount':2,'images':0,'timingsSeconds':{'total':0.1},
                        'render':{'status':'rendered','preview':str(png),
                                  'pptxSha256':hashlib.sha256(ppt.read_bytes()).hexdigest(),
                                  'pngSha256':hashlib.sha256(png.read_bytes()).hexdigest()}}
                build_report=folder/'build.json';build_report.write_text(json.dumps(report),encoding='utf-8')
                with self.assertRaisesRegex(ValueError,'explicit visual-review'): session.finish(record,build_report,'')
                ppt.write_bytes(b'changed')
                with self.assertRaisesRegex(ValueError,'changed'): session.finish(record,build_report,'reviewed')
                ppt.write_bytes(b'unit-test artifact')
                result=session.finish(record,build_report,'Wording, topology and layout reviewed')
                self.assertEqual(result['elapsedSeconds'],125)
                self.assertEqual(result['buildTimingsSeconds']['total'],0.1)
                self.assertEqual(len(result['events']),1)

    def test_file_open_uses_literal_paths_without_a_shell(self):
        with tempfile.TemporaryDirectory(dir=BUILD) as folder:
            ppt=Path(folder)/'a space 中文.pptx';ppt.write_bytes(b'test')
            with patch.object(open_artifact.platform,'system',return_value='Darwin'),patch.object(open_artifact.shutil,'which',return_value='/usr/bin/open'),patch.object(open_artifact.subprocess,'run') as run:
                result=open_artifact.open_pptx(ppt)
                self.assertEqual(result['status'],'open-requested')
                self.assertEqual(run.call_args.args[0],['/usr/bin/open',str(ppt.resolve())])
                self.assertNotIn('shell',run.call_args.kwargs)
            with self.assertRaises(ValueError):open_artifact.open_pptx(ppt.with_suffix('.exe'))


if __name__=='__main__':unittest.main()
