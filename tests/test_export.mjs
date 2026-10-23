import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { exportScene, validateScene } from '../scripts/export_pptx.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const fixture = JSON.parse(await fs.readFile(path.join(root, 'examples/diagram.scene.json'), 'utf8'));
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
