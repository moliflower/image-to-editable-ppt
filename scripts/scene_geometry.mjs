import { editableShapeFrame } from '../vendor/figureforge/editable-native.mjs';

// Canonical source-pixel dash lengths. Odd patterns repeat as specified by SVG.
export function dashPattern(node) {
  const fields = ['dash', 'dashed', 'strokeDasharray'].filter(k => node[k] !== undefined);
  if (fields.length > 1) throw new Error('use only one of dash, dashed, strokeDasharray');
  if (!fields.length) return false;
  const raw = node[fields[0]];
  if (typeof raw === 'boolean') return raw;
  const values = typeof raw === 'string' && raw.trim() ? raw.trim().split(/[\s,]+/).map(Number) : raw;
  if (!Array.isArray(values) || !values.length || values.some(v => typeof v !== 'number' || !Number.isFinite(v) || v < 0) || !values.some(v => v > 0))
    throw new Error('dash must be a boolean or nonempty nonnegative pixel lengths with a positive length');
  return values.length % 2 ? [...values, ...values] : [...values];
}

// Rotate the same frame PowerPoint uses, including Bezier control-point bounds.
export function rotatedBounds(node) {
  const f = editableShapeFrame(node);
  if (!f) return null;
  const cx=f.x+f.w/2, cy=f.y+f.h/2, a=(node.rotation||0)*Math.PI/180;
  const points=[[f.x,f.y],[f.x+f.w,f.y],[f.x+f.w,f.y+f.h],[f.x,f.y+f.h]]
    .map(([x,y]) => [cx+(x-cx)*Math.cos(a)-(y-cy)*Math.sin(a),cy+(x-cx)*Math.sin(a)+(y-cy)*Math.cos(a)]);
  return [Math.min(...points.map(p=>p[0])),Math.min(...points.map(p=>p[1])),Math.max(...points.map(p=>p[0])),Math.max(...points.map(p=>p[1]))];
}

export function validateSourceAssets(scene) {
  const errors=[], assets=scene.sourceAssets;
  if (assets !== undefined && !Array.isArray(assets)) return ['sourceAssets must be an array'];
  const ids=new Set();
  for (const a of assets||[]) {
    if (!a || typeof a.id !== 'string' || !a.id.trim() || ids.has(a.id)) {errors.push('sourceAssets has a missing or duplicate ID');continue;}
    ids.add(a.id);
    const c=a.canvas, b=a.crop;
    if (!c || !['width','height'].every(k=>Number.isInteger(c[k])&&c[k]>0) || !b || !['x','y','w','h'].every(k=>Number.isInteger(b[k])) || b.x<0 || b.y<0 || b.w<=0 || b.h<=0 || b.x+b.w>c.width || b.y+b.h>c.height)
      errors.push(a.id+': invalid source asset crop or canvas');
    if (!/^[a-f0-9]{64}$/.test(a.pixelSha256||'')) errors.push(a.id+': source asset needs pixelSha256; run image_assets.py prepare');
    const matches=(scene.nodes||[]).filter(n=>n.sourceAssetId===a.id);
    if (matches.length!==1 || matches[0].type!=='image') errors.push(a.id+': expected exactly one bound image');
    else if (!['x','y','w','h'].every(k=>matches[0].sourceCrop?.[k]===b?.[k]) || !['width','height'].every(k=>matches[0].sourceCanvas?.[k]===c?.[k])) errors.push(a.id+': source provenance differs from manifest');
  }
  for (const n of scene.nodes||[]) {
    if (n.sourceAssetId!==undefined && !ids.has(n.sourceAssetId)) errors.push(n.id+': unknown sourceAssetId');
    if ((n.sourceCrop!==undefined || n.sourceCanvas!==undefined) && n.sourceAssetId===undefined) errors.push(n.id+': source provenance needs sourceAssetId');
  }
  return errors;
}
