// Exporta cada BPMNDiagram del modelo formal; no recrea un diagrama ilustrativo.
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { chromium } from 'playwright';

const root = fileURLToPath(new URL('../../', import.meta.url));
const output = path.join(root, 'quarto/diagrams');
await mkdir(output, { recursive: true });
const xml = await readFile(path.join(root, 'docs/procesos/creacion-enlace.bpmn'), 'utf8');
const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.setContent('<!doctype html><html><body><div id="canvas" style="width:1900px;height:1000px"></div></body></html>');
  await page.addScriptTag({ path: path.join(root, 'tools/documentation/node_modules/bpmn-js/dist/bpmn-viewer.development.js') });
  const diagrams = await page.evaluate(async (source) => {
    const viewer = new window.BpmnJS({ container: '#canvas' });
    const { warnings } = await viewer.importXML(source);
    if (warnings.length) throw new Error(warnings.map(w => w.message).join('\n'));
    const result = [];
    for (const diagram of viewer.getDefinitions().diagrams) {
      const opened = await viewer.open(diagram);
      if (opened.warnings.length) throw new Error(opened.warnings.map(w => w.message).join('\n'));
      const { svg } = await viewer.saveSVG({ format: true });
      result.push({ id: diagram.id, svg });
    }
    viewer.destroy();
    return result;
  }, xml);
  if (diagrams.length !== 4) throw new Error(`Se esperaban cuatro procesos, hay ${diagrams.length}`);
  for (const diagram of diagrams) {
    if (!/^[A-Za-z0-9_-]+$/.test(diagram.id)) throw new Error('Identificador de diagrama inválido');
    await writeFile(path.join(output, `bpmn-${diagram.id}.svg`), diagram.svg, 'utf8');
    console.log(`BPMN ${diagram.id}: SVG exportado del XML`);
  }
} finally {
  await browser.close();
}
