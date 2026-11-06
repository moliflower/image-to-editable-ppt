import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { exportScene, validateScene } from '../scripts/export_pptx.mjs';
import { rotatedBounds } from '../scripts/scene_geometry.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const fixture = JSON.parse(await fs.readFile(path.join(root, 'tests/fixtures/diagram.scene.json'), 'utf8'));
const scientific = JSON.parse(await fs.readFile(path.join(root, 'tests/fixtures/scientific-text.scene.json'), 'utf8'));
function member(bytes, wanted) {
  let at = 0;
  while (bytes.readUInt32LE(at) === 0x04034b50) {
    const size = bytes.readUInt32LE(at + 18), names = bytes.readUInt16LE(at + 26), extra = bytes.readUInt16LE(at + 28);
    const name = bytes.subarray(at + 30, at + 30 + names).toString();
    const start = at + 30 + names + extra;
    if (name === wanted) return bytes.subarray(start, start + size).toString('utf8');
    at = start + size;
  }
  throw new Error('Missing ZIP member: ' + wanted);
}

test('scientific labels keep native runs, baselines and gradient opacity without splitting text boxes', async () => {
  await fs.mkdir(path.join(root, 'build'), {recursive:true});
  const dir = await fs.mkdtemp(path.join(root, 'build', 'text-test-'));
  try {
    const out = path.join(dir, 'figure.pptx');
    const result = await exportScene(scientific, out);
    const xml = member(await fs.readFile(out), 'ppt/slides/slide1.xml');
    assert.equal(result.objectCount, scientific.nodes.length);
    assert.equal(result.richTextBoxes, 3);
    assert.equal(result.gradientShapes, 1);
    assert.equal((xml.match(/<p:txBody>/g) || []).length, scientific.nodes.filter(n=>n.type==='text').length);
    assert.match(xml, /baseline="-25000"/);
    assert.match(xml, /baseline="30000"/);
    assert.match(xml, /u="sng"/);
    assert.match(xml, /<a:alpha val="5000"\/>/);
    assert.match(xml, /<a:spcPts val="1800"\/>/);
    assert.doesNotMatch(xml, /<p:pic>|normAutofit|spAutoFit/);
  } finally { await fs.rm(dir, {recursive:true, force:true}); }
});

test('rich runs preserve whitespace, explicit style overrides, Unicode and paragraph boundaries', async () => {
  const scene={canvas:{width:1000,height:600},nodes:[{id:'label',type:'text',x:20,y:20,w:900,h:260,
    text:'  A<&>\n\n中文 x2  ',fontSize:30,fontFamily:'Times New Roman',bold:true,italic:true,fill:'#123',
    runs:[{text:'  A<&>\r\n\r\n',bold:false},{text:'中文 ',fontFamily:'Microsoft YaHei',italic:false},
      {text:'x',underline:true},{text:'2',fontSize:20,baselineShift:'super'},{text:'  '}]}]};
  const dir=await fs.mkdtemp(path.join(root,'build','run-test-'));
  try {
    const result=await exportScene(scene,path.join(dir,'runs.pptx'));
    const xml=member(await fs.readFile(result.output),'ppt/slides/slide1.xml');
    assert.equal((xml.match(/<a:p>/g)||[]).length,3);
    assert.match(xml, /<a:t xml:space="preserve">  A&lt;&amp;&gt;<\/a:t>/);
    assert.match(xml, /sz="2160" b="0" i="1"/);
    assert.match(xml, /sz="2160" b="1" i="0"/);
    assert.match(xml, /<a:ea typeface="Microsoft YaHei"\/>/);
    const normalized=JSON.parse(await fs.readFile(path.join(dir,'runs.exported.scene.json')));
    assert.equal(normalized.nodes[0].runs.map(r=>r.text).join(''),normalized.nodes[0].text);
  } finally {await fs.rm(dir,{recursive:true,force:true});}
});

test('unsupported or lossy text and gradient declarations fail before export', async () => {
  for(const patch of [
    {runs:[]},{runs:[{text:'wrong'}]},{runs:[{text:'x',fontSize:'18'}]},
    {runs:[{text:'x',bold:'false'}]},{runs:[{text:'x',fill:'none'}]},
    {runs:[{text:'x',baselineShift:'sup'}]},{runs:[{text:'x',fontstyle:'italic'}]},
    {runs:[{text:'x'}],textPath:{d:'M0 0 L100 0'}},
    {lineSpacing:0},{underline:'yes'},{fontSize:0.1},{verticalAlign:'bottom'}]) {
    const scene={canvas:{width:1000,height:600},nodes:[{id:'x',type:'text',x:0,y:0,w:200,h:60,text:'x',fontSize:20,...patch}]};
    assert.throws(()=>validateScene(scene));
    await assert.rejects(exportScene(scene,path.join(root,'build','must-not-exist.pptx')));
  }
  for(const gradient of [
    {angle:0,stops:[null,null]},
    {angle:0,stops:[{offset:1,color:'#fff'},{offset:0,color:'#000'}]},
    {angle:0,stops:[{offset:0,color:'#fff',opacity:-0.1},{offset:1,color:'#000'}]},
    {type:'radial',angle:0,stops:[{offset:0,color:'#fff'},{offset:1,color:'#000'}]}]) {
    assert.throws(()=>validateScene({canvas:{width:1000,height:600},nodes:[{id:'g',type:'rect',x:0,y:0,w:200,h:60,gradient}]}));
  }
  const scene=structuredClone(fixture);
  scene.nodes[0].gradient={angle:0,stops:[{offset:0,color:'#fff'},{offset:1,color:'#000'}]};
  assert.throws(()=>validateScene(scene),/fillable/);
});

test('exports native bilingual text, separate paths, arrowheads and valid geometry', async () => {
  await fs.mkdir(path.join(root, 'build'), { recursive: true });
  const dir = await fs.mkdtemp(path.join(root, 'build', 'editable-ppt-test-'));
  try {
    const out = path.join(dir, 'figure.pptx');
    const result = await exportScene(fixture, out);
    const bytes = await fs.readFile(out), text = member(bytes, 'ppt/slides/slide1.xml');
    assert.equal(bytes.readUInt32LE(0), 0x04034b50);
    assert.equal(result.objectCount, 17);
    assert.equal(result.counts.text, 6);
    assert.equal(result.arrows, 3);
    assert.equal((text.match(/<p:sp>/g) || []).length, 17);
    assert.equal((text.match(/<p:pic>/g) || []).length, 0);
    assert.equal((text.match(/<a:tailEnd type="triangle"\/>/g) || []).length, 3);
    assert.match(text, /<a:t>输入图片<\/a:t>/);
    assert.match(text, /<a:ea typeface="Microsoft YaHei"\/>/);
    assert.match(text, /<a:cubicBezTo>/);
    assert.match(text, /name="refinement-loop"/);
    assert.doesNotMatch(bytes.toString('utf8'), /Steve Canny|generated using python-pptx|thumbnail\.jpeg/);
    const normalized = JSON.parse(await fs.readFile(path.join(dir, 'figure.exported.scene.json')));
    assert.deepEqual(normalized.nodes.map(x => x.id), fixture.nodes.map(x => x.id));
  } finally { await fs.rm(dir, { recursive: true, force: true }); }
});

test('rejects duplicate IDs, unsupported primitives and a flattened background', () => {
  const duplicate = structuredClone(fixture); duplicate.nodes[1].id = duplicate.nodes[0].id;
  assert.throws(() => validateScene(duplicate), /duplicate/);
  const invalid = structuredClone(fixture); invalid.nodes[0].type = 'svg';
  assert.throws(() => validateScene(invalid), /unsupported node/);
  const flat = structuredClone(fixture);
  flat.nodes.push({ id: 'flat', type: 'image', x: 0, y: 0, w: 1200, h: 650, assetPurpose: 'photo', href: 'data:image/png;base64,YQ==' });
  assert.throws(() => validateScene(flat), /dominant bitmap/);
});

test('rejects remote image URLs, invisible text and nonnumeric geometry', () => {
  const remote = structuredClone(fixture);
  remote.nodes.push({ id: 'remote', type: 'image', x: 10, y: 10, w: 10, h: 10, assetPurpose: 'photo', href: 'https://example.com/image.png' });
  assert.throws(() => validateScene(remote), /embedded PNG/);
  const hidden = structuredClone(fixture); hidden.nodes[0].fill = 'none';
  assert.throws(() => validateScene(hidden), /invisible text/);
  const bad = structuredClone(fixture); bad.nodes[2].w = '280';
  assert.throws(() => validateScene(bad), /numeric/);
});

test('native start/end arrows, source-pixel dashes and all primitive rotations survive export without font fitting', async () => {
  const scene={canvas:{width:1000,height:600},nodes:[
    {id:'both',type:'line',x:50,y:100,x2:250,y2:100,arrow:true,arrowStart:true,dash:[12,6],stroke:'#000000',strokeWidth:2,rotation:10},
    {id:'curve',type:'path',d:'M 50 200 C 100 150 200 250 250 200',arrowStart:true,strokeDasharray:'3, 2, 1',stroke:'#000000',strokeWidth:2,rotation:-25},
    {id:'polygon',type:'polyline',points:'300,100 400,100 350,180',closed:true,fill:'#123456',rotation:45},
    {id:'box',type:'rect',x:450,y:100,w:100,h:50,fill:'#345678',rotation:30},
    {id:'oval',type:'ellipse',x:600,y:100,w:100,h:50,fill:'#345678',rotation:-15},
    {id:'photo',type:'image',x:50,y:300,w:100,h:100,assetPurpose:'photo',file:'pixels.png',rotation:12},
    {id:'label',type:'text',x:300,y:300,w:20,h:50,text:'Explicit font size stays unchanged',fontSize:33,fontFamily:'Times New Roman',rotation:90}
  ]};
  const dir=await fs.mkdtemp(path.join(root,'build','native-caps-'));
  try {
    const result=await exportScene(scene,path.join(dir,'native.pptx'),path.join(root,'tests','fixtures'));
    const xml=member(await fs.readFile(path.join(dir,'native.pptx')),'ppt/slides/slide1.xml');
    for(const angle of [10,-25,45,30,-15,12,90]) assert.ok(xml.includes(`rot="${angle*60000}"`));
    assert.equal(result.arrows,2); assert.equal(result.arrowheads,3);
    assert.equal((xml.match(/<a:headEnd type="triangle"\/>/g)||[]).length,2);
    assert.equal((xml.match(/<a:tailEnd type="triangle"\/>/g)||[]).length,1);
    assert.match(xml,/<a:custDash><a:ds d="600000" sp="300000"\/><\/a:custDash>/);
    assert.match(xml,/<a:ds d="150000" sp="100000"\/><a:ds d="50000" sp="150000"\/><a:ds d="100000" sp="50000"\/>/);
    assert.match(xml,/sz="2376"/);
    const normalized=JSON.parse(await fs.readFile(path.join(dir,'native.exported.scene.json'),'utf8'));
    assert.deepEqual(normalized.nodes[1].dash,[3,2,1,3,2,1]);
    assert.equal(normalized.nodes[6].fontSize,33);
    assert.equal(normalized.nodes[6].text,scene.nodes[6].text);
  } finally { await fs.rm(dir,{recursive:true,force:true}); }
});

test('invalid dash/arrow declarations fail and rotated bounds warn about real clipping', () => {
  for(const dash of [[],[0,0],[-1,2],[1,'2'],[Infinity,2],'','bad']) {
    const scene=structuredClone(fixture); scene.nodes[2].dash=dash;
    assert.throws(()=>validateScene(scene),/dash/);
  }
  const wrong=structuredClone(fixture);wrong.nodes[2].arrowStart=true;
  assert.throws(()=>validateScene(wrong),/arrowheads require/);
  const invisible=structuredClone(fixture);invisible.nodes[5].stroke='none';
  assert.throws(()=>validateScene(invisible),/visible stroke/);
  const rotated={id:'turned',type:'rect',x:10,y:20,w:100,h:20,rotation:90,fill:'#123456'};
  const bounds=rotatedBounds(rotated);
  [50,-20,70,80].forEach((v,i)=>assert.ok(Math.abs(bounds[i]-v)<1e-8));
  assert.ok(validateScene({canvas:{width:1200,height:650},nodes:[rotated]}).some(s=>/outside the canvas/.test(s)));
  const zeroDash=structuredClone(fixture);zeroDash.nodes[5].dash=[0,4];
  assert.doesNotThrow(()=>validateScene(zeroDash));
});
