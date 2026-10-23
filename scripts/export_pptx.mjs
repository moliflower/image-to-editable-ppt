#!/usr/bin/env node
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { buildNativePptx, expandEditableTextPaths, geometrySegments } from '../vendor/figureforge/editable-native.mjs';

const base = path.dirname(fileURLToPath(import.meta.url));
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const color = v => typeof v === 'string' && /^(none|#[\da-f]{3}|#[\da-f]{6})$/i.test(v);
const finite = v => typeof v === 'number' && Number.isFinite(v);
const types = new Set(['text', 'rect', 'ellipse', 'line', 'polyline', 'path', 'image']);

export function validateScene(scene) {
  const errors = [], warnings = [], ids = new Set();
  const c = scene?.canvas;
  if (!c || !finite(c.width) || !finite(c.height) || c.width <= 0 || c.height <= 0)
    throw new Error('canvas.width and canvas.height must be positive finite numbers');
  if (c.height / c.width > 5.6 || c.height / c.width < 1 / 56)
    errors.push('Canvas aspect ratio exceeds supported PowerPoint slide dimensions');
  if (!Array.isArray(scene.nodes) || !scene.nodes.length) throw new Error('Scene needs a nonempty nodes array');
  if (scene.reviewNotes !== undefined && (!Array.isArray(scene.reviewNotes) || scene.reviewNotes.some(x => typeof x !== 'string')))
    errors.push('reviewNotes must be an array of strings');
  for (const n of scene.nodes) {
    if (!n || typeof n !== 'object') { errors.push('Each node must be an object'); continue; }
    const id = n.id;
    if (typeof id !== 'string' || !id.trim() || ids.has(id)) errors.push('Missing or duplicate node id: ' + id);
    ids.add(id);
    if (!types.has(n.type)) { errors.push(id + ': unsupported node type ' + n.type); continue; }
    if (n.export === false) errors.push(id + ': hidden/export-disabled nodes are not accepted');
    if (n.opacity !== undefined) errors.push(id + ': opacity is unsupported; use explicit colors');
    for (const key of ['fill', 'stroke']) if (n[key] !== undefined && !color(n[key])) errors.push(id + ': invalid ' + key);
    if (n.strokeWidth !== undefined && (!finite(n.strokeWidth) || n.strokeWidth <= 0)) errors.push(id + ': invalid strokeWidth');
    if (n.radius !== undefined && (!finite(n.radius) || n.radius < 0)) errors.push(id + ': invalid radius');
    if (n.rotation !== undefined && (!finite(n.rotation) || n.type !== 'text')) errors.push(id + ': rotation is supported on text only');
    if (n.gradient !== undefined) {
      if (!finite(n.gradient?.angle) || !Array.isArray(n.gradient?.stops) || n.gradient.stops.length < 2 ||
          n.gradient.stops.some(s => !finite(s.offset) || s.offset < 0 || s.offset > 1 || !color(s.color) || s.color === 'none'))
        errors.push(id + ': invalid gradient');
    }
    let bounds;
    if (['text', 'rect', 'ellipse', 'image'].includes(n.type)) {
      for (const k of ['x', 'y', 'w', 'h']) if (!finite(n[k])) errors.push(id + ': ' + k + ' must be numeric');
      if (!(n.w > 0 && n.h > 0)) errors.push(id + ': width and height must be positive');
      bounds = [n.x, n.y, n.x + n.w, n.y + n.h];
    } else {
      if (n.type === 'line') {
        for (const k of ['x', 'y', 'x2', 'y2']) if (!finite(n[k])) errors.push(id + ': missing numeric ' + k);
      }
      if (n.type === 'polyline' && (typeof n.points !== 'string' || !/^\s*-?[\d.]+(?:[eE][+-]?\d+)?(?:[\s,]+-?[\d.]+(?:[eE][+-]?\d+)?)+\s*$/.test(n.points)))
        errors.push(id + ': invalid polygon points');
      if (n.type === 'path' && (typeof n.d !== 'string' || !/^\s*[Mm]/.test(n.d) || /[BbRrUu]/.test(n.d)))
        errors.push(id + ': invalid or unsupported SVG path');
      const pts = geometrySegments(n).flatMap(p => p.points);
      if (pts.length < 2) errors.push(id + ': empty geometry');
      else bounds = [Math.min(...pts.map(p => p.x)), Math.min(...pts.map(p => p.y)), Math.max(...pts.map(p => p.x)), Math.max(...pts.map(p => p.y))];
    }
    if (bounds && (bounds[0] < -1 || bounds[1] < -1 || bounds[2] > c.width + 1 || bounds[3] > c.height + 1))
      warnings.push(id + ': geometry extends outside the canvas; review clipping');
    if (n.type === 'text') {
      if (typeof n.text !== 'string' || !n.text.trim()) errors.push(id + ': text is empty');
      if (typeof n.text === 'string' && /[\u0000-\u0008\u000B\u000C\u000E-\u001F]/.test(n.text)) errors.push(id + ': text contains invalid XML control characters');
      if (!finite(n.fontSize) || n.fontSize <= 0) errors.push(id + ': fontSize must be positive');
      if (!['start', 'middle', 'end', undefined].includes(n.anchor)) errors.push(id + ': invalid anchor');
      if (n.fill === 'none') errors.push(id + ': invisible text is not allowed');
      const lines = String(n.text || '').split(/\r?\n/).length;
      if (n.h < n.fontSize * 1.25 * lines) warnings.push(id + ': text box may be too short for the declared font and line count');
    }
    if (n.type === 'image') {
      if (!['photo', 'texture', 'logo', 'complex-artwork'].includes(n.assetPurpose)) errors.push(id + ': image needs assetPurpose');
      if (n.w * n.h > c.width * c.height * 0.55) errors.push(id + ': dominant bitmap rejected; reconstruct diagram objects');
      if (!/^data:image\/(png|jpeg);base64,[A-Za-z0-9+/=\s]+$/.test(n.href || '')) errors.push(id + ': image must be embedded PNG/JPEG; prepare crops or use a local file');
    }
  }
  if (!scene.nodes.some(n => n.type !== 'image')) errors.push('A diagram must contain native editable objects');
  if (errors.length) throw new Error(errors.join('\n'));
  return warnings;
}

const crcTable = Uint32Array.from({ length: 256 }, (_, n) => {
  let c = n; for (let k = 0; k < 8; k++) c = (c & 1) ? 0xedb88320 ^ (c >>> 1) : c >>> 1; return c >>> 0;
});
function crc32(bytes) {
  let c = 0xffffffff; for (const b of bytes) c = crcTable[(c ^ b) & 255] ^ (c >>> 8); return (c ^ 0xffffffff) >>> 0;
}
export function zipStore(files) {
  const locals = [], central = []; let offset = 0, centralSize = 0;
  for (const f of files) {
    const name = Buffer.from(f.name), data = Buffer.from(f.data), crc = crc32(data);
    const local = Buffer.alloc(30);
    local.writeUInt32LE(0x04034b50, 0); local.writeUInt16LE(20, 4); local.writeUInt16LE(0x800, 6);
    local.writeUInt16LE(33, 12); local.writeUInt32LE(crc, 14); local.writeUInt32LE(data.length, 18);
    local.writeUInt32LE(data.length, 22); local.writeUInt16LE(name.length, 26);
    locals.push(local, name, data);
    const entry = Buffer.alloc(46);
    entry.writeUInt32LE(0x02014b50, 0); entry.writeUInt16LE(20, 4); entry.writeUInt16LE(20, 6);
    entry.writeUInt16LE(0x800, 8); entry.writeUInt16LE(33, 14); entry.writeUInt32LE(crc, 16);
    entry.writeUInt32LE(data.length, 20); entry.writeUInt32LE(data.length, 24);
    entry.writeUInt16LE(name.length, 28); entry.writeUInt32LE(offset, 42);
    central.push(entry, name); centralSize += entry.length + name.length; offset += local.length + name.length + data.length;
  }
  const end = Buffer.alloc(22);
  end.writeUInt32LE(0x06054b50, 0); end.writeUInt16LE(files.length, 8); end.writeUInt16LE(files.length, 10);
  end.writeUInt32LE(centralSize, 12); end.writeUInt32LE(offset, 16);
  return new Blob([...locals, ...central, end]);
}

function adaptPackage(files, nodes) {
  const enc = new TextEncoder(), dec = new TextDecoder();
  const removed = new Set(files.filter(f => /^(docProps\/thumbnail\.|ppt\/notes|ppt\/printerSettings\/)/.test(f.name)).map(f => f.name));
  const kept = [];
  for (const f of files) {
    if (removed.has(f.name)) continue;
    if (!/\.(xml|rels)$/.test(f.name)) { kept.push(f); continue; }
    let xml = dec.decode(f.data);
    if (f.name.endsWith('.rels')) {
      const folder = path.posix.dirname(f.name).replace(/\/?_rels$/, '');
      xml = xml.replace(/<Relationship\b[^>]*\/>/g, tag => {
        const target = tag.match(/\bTarget="([^"]+)"/)?.[1];
        if (/TargetMode="External"/.test(tag)) throw new Error('External template relationship rejected');
        return target && removed.has(path.posix.normalize(path.posix.join(folder, target))) ? '' : tag;
      });
    }
    if (f.name === '[Content_Types].xml')
      xml = xml.replace(/<Override\b[^>]*\/>/g, tag => removed.has(tag.match(/PartName="\/([^"]+)"/)?.[1]) ? '' : tag);
    if (f.name === 'ppt/presentation.xml') xml = xml.replace(/<p:notesMasterIdLst>[\s\S]*?<\/p:notesMasterIdLst>/g, '');
    xml = xml.replace(/<p:printerSettings\b[^>]*\/>/g, '');
    if (f.name === 'docProps/core.xml') {
      xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>Editable figure</dc:title><dc:creator>image-to-editable-ppt</dc:creator></cp:coreProperties>';
    }
    if (f.name === 'docProps/app.xml') {
      xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Application>image-to-editable-ppt</Application><Slides>1</Slides></Properties>';
    }
    if (f.name === 'ppt/slides/slide1.xml') {
      xml = xml.replace('<p:cSld>', '<p:cSld><p:bg><p:bgPr><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill><a:effectLst/></p:bgPr></p:bg>');
      xml = xml.replace(/<p:cNvPr id="(\d+)" name="[^"]*"\/>/g, (tag, id) => {
        const n = nodes[Number(id) - 2];
        return n ? '<p:cNvPr id="' + id + '" name="' + esc(n.name || n.id) + '"/>' : tag;
      });
      xml = xml.replace(/<a:latin typeface="([^"]*)"\/>/g, '$&<a:ea typeface="$1"/><a:cs typeface="$1"/>');
    }
    kept.push({ name: f.name, data: enc.encode(xml) });
  }
  return kept;
}

export async function exportScene(input, output, sceneDirectory = process.cwd()) {
  const scene = structuredClone(input);
  for (const n of scene.nodes || []) {
    if (n.type === 'image' && n.file) {
      const filename = path.resolve(sceneDirectory, n.file), bytes = await fs.readFile(filename);
      const mime = /\.png$/i.test(filename) ? 'png' : /\.jpe?g$/i.test(filename) ? 'jpeg' : null;
      if (!mime) throw new Error(n.id + ': local image must be PNG/JPEG');
      n.href = 'data:image/' + mime + ';base64,' + bytes.toString('base64'); delete n.file;
    }
    if (n.crop) throw new Error(n.id + ': run image_assets.py prepare before exporting crop nodes');
    if (n.type === 'text') {
      n.fontFamily ||= 'Times New Roman'; n.fill ??= '#000000';
    } else { n.fill ??= 'none'; n.stroke ??= 'none'; }
  }
  const normalized = expandEditableTextPaths(scene);
  const warnings = validateScene(normalized);
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async url => {
    if (url !== './pptx-template.json') throw new Error('Network access is not supported');
    return { ok: true, json: async () => JSON.parse(await fs.readFile(path.join(base, '../vendor/figureforge/pptx-template.json'), 'utf8')) };
  };
  let pptx;
  try { pptx = await buildNativePptx(normalized, files => zipStore(adaptPackage(files, normalized.nodes))); }
  finally { globalThis.fetch = originalFetch; }
  const counts = {};
  for (const n of normalized.nodes) counts[n.type] = (counts[n.type] || 0) + 1;
  const summary = {
    status: 'exported', visualVerification: 'required', canvas: normalized.canvas,
    objectCount: normalized.nodes.length, counts,
    arrows: normalized.nodes.filter(n => n.arrow).length,
    imageRegions: normalized.nodes.filter(n => n.type === 'image').map(n => ({ id: n.id, purpose: n.assetPurpose, description: n.assetDescription || '' })),
    warnings, reviewNotes: normalized.reviewNotes || [],
    upstreamRevision: 'dbf360a533ee46bc7d4a8f6037717c83f21a633a'
  };
  output = path.resolve(output);
  if (!/\.pptx$/i.test(output)) throw new Error('Output must end in .pptx');
  const stem = output.slice(0, -5);
  await fs.mkdir(path.dirname(output), { recursive: true });
  await fs.writeFile(output, Buffer.from(await pptx.arrayBuffer()));
  await fs.writeFile(stem + '.exported.scene.json', JSON.stringify(normalized, null, 2) + '\n');
  await fs.writeFile(stem + '.editability.json', JSON.stringify(summary, null, 2) + '\n');
  return { output, ...summary };
}

async function main() {
  const argv = process.argv.slice(2);
  if (argv.includes('--help') || !argv.length) { console.log('node export_pptx.mjs --scene scene.json --output figure.pptx'); return; }
  const args = {};
  for (let i = 0; i < argv.length; i += 2) {
    if (!['--scene', '--output'].includes(argv[i]) || !argv[i + 1]) throw new Error('Unknown or incomplete argument: ' + argv[i]);
    args[argv[i]] = argv[i + 1];
  }
  if (!args['--scene'] || !args['--output']) throw new Error('--scene and --output are required');
  const source = path.resolve(args['--scene']);
  console.log(JSON.stringify(await exportScene(JSON.parse((await fs.readFile(source, 'utf8')).replace(/^\uFEFF/, '')), args['--output'], path.dirname(source)), null, 2));
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url))
  main().catch(e => { console.error(e.message); process.exitCode = 1; });
