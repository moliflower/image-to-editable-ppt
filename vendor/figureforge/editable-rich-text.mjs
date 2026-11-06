// Original local DrawingML serializer. See UPSTREAM.md in this directory.
// Styles remain within one editable text box; font sizes never auto-shrink.
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const rgb = s => { const h = s.replace('#', ''); return (h.length === 3 ? [...h].map(c => c + c).join('') : h).toUpperCase(); };
const clean = s => s.replace(/\r\n?/g, '\n');

export function richTextParagraphs(node, unit) {
  const defaults = {fontSize: node.fontSize, fontFamily: node.fontFamily || 'Arial', fill: node.fill || '#000000',
    bold: !!node.bold, italic: !!node.italic, underline: !!node.underline, baselineShift: node.baselineShift || 'none'};
  const lines = [[]];
  for (const run of node.runs || [{text: node.text}]) {
    const style = {...defaults, ...run};
    clean(run.text).split('\n').forEach((text, index) => {
      if (index) lines.push([]);
      if (text) lines.at(-1).push({...style, text});
    });
  }
  const points = pixels => Math.max(100, Math.round(pixels * unit / 914400 * 7200));
  const properties = style => {
    const face = esc(style.fontFamily.split(',')[0].replace(/["']/g, ''));
    const baseline = {none: 0, super: 30000, sub: -25000}[style.baselineShift];
    return `lang="en-US" sz="${points(style.fontSize)}" b="${style.bold ? 1 : 0}" i="${style.italic ? 1 : 0}" u="${style.underline ? 'sng' : 'none'}" baseline="${baseline}"><a:solidFill><a:srgbClr val="${rgb(style.fill)}"/></a:solidFill><a:latin typeface="${face}"/>`;
  };
  return lines.map(runs => {
    const maxSize = Math.max(node.fontSize, ...runs.map(r => r.fontSize));
    const spacing = node.lineSpacing === undefined ? Math.round(points(maxSize) * 1.14) : Math.round(node.lineSpacing * unit / 914400 * 7200);
    const leading = lines.length > 1 || node.lineSpacing !== undefined
      ? `<a:lnSpc><a:spcPts val="${spacing}"/></a:lnSpc><a:spcBef><a:spcPts val="0"/></a:spcBef><a:spcAft><a:spcPts val="0"/></a:spcAft>` : '';
    const body = runs.map(r => `<a:r><a:rPr ${properties(r)}</a:rPr><a:t xml:space="preserve">${esc(r.text)}</a:t></a:r>`).join('');
    return `<a:p><a:pPr algn="${node.anchor === 'middle' ? 'ctr' : node.anchor === 'end' ? 'r' : 'l'}">${leading}</a:pPr>${body}<a:endParaRPr ${properties(defaults)}</a:endParaRPr></a:p>`;
  }).join('');
}
