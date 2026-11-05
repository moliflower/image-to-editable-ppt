// Local scene contract; explicit styles only, with no font measurement or fitting.
const finite = value => typeof value === 'number' && Number.isFinite(value);
const ink = value => typeof value === 'string' && /^#(?:[\da-f]{3}|[\da-f]{6})$/i.test(value);
const keys = new Set(['text', 'fontFamily', 'fontSize', 'fill', 'bold', 'italic', 'underline', 'baselineShift']);
export const normalizedText = value => String(value ?? '').replace(/\r\n?/g, '\n');

export function validateText(node, canvasWidth) {
  const errors = [];
  const check = (style, label) => {
    for (const key of ['bold', 'italic', 'underline'])
      if (style[key] !== undefined && typeof style[key] !== 'boolean') errors.push(`${label}: ${key} must be boolean`);
    if (style.fontFamily !== undefined && (typeof style.fontFamily !== 'string' || !style.fontFamily.trim() || /[\x00-\x1f]/.test(style.fontFamily)))
      errors.push(`${label}: invalid fontFamily`);
    if (style.fontSize !== undefined && (!finite(style.fontSize) || style.fontSize <= 0 || style.fontSize * 720 / canvasWidth < 1 || style.fontSize * 720 / canvasWidth > 4000))
      errors.push(`${label}: fontSize must map to 1..4000 PowerPoint points`);
    if (style.fill !== undefined && !ink(style.fill)) errors.push(`${label}: text fill must be a visible hex color`);
    if (style.baselineShift !== undefined && !['none', 'super', 'sub'].includes(style.baselineShift))
      errors.push(`${label}: baselineShift must be none, super or sub`);
  };
  check(node, node.id);
  if (node.verticalAlign !== undefined && !['top', 'middle'].includes(node.verticalAlign)) errors.push(`${node.id}: invalid verticalAlign`);
  if (node.lineSpacing !== undefined && (!finite(node.lineSpacing) || node.lineSpacing <= 0 || node.lineSpacing * 72000 / canvasWidth > 20116800))
    errors.push(`${node.id}: lineSpacing must be a positive source-pixel distance within PowerPoint limits`);
  if (node.runs !== undefined) {
    if (!Array.isArray(node.runs) || !node.runs.length) return [...errors, `${node.id}: runs must be a nonempty array`];
    if (node.textPath) errors.push(`${node.id}: runs with textPath are unsupported; use ordinary text boxes`);
    for (const [i, run] of node.runs.entries()) {
      const label = `${node.id}.runs[${i}]`;
      if (!run || typeof run !== 'object' || Array.isArray(run)) { errors.push(`${label}: expected an object`); continue; }
      for (const key of Object.keys(run)) if (!keys.has(key)) errors.push(`${label}: unsupported run property ${key}`);
      if (typeof run.text !== 'string' || !run.text.length || /[\x00-\x08\x0b\x0c\x0e-\x1f]/.test(run.text)) errors.push(`${label}: invalid run text`);
      check(run, label);
    }
    if (node.runs.map(r => normalizedText(r?.text)).join('') !== normalizedText(node.text))
      errors.push(`${node.id}: concatenated runs must exactly match text`);
  }
  return errors;
}
