/* pdf-worker.js: pdfmake Web Worker */
let pdfMake;
self.addEventListener('message', (e) => {
  const { docDefinition, type } = e.data;
  if (!pdfMake) {
    importScripts(
      'https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.2.12/pdfmake.min.js',
      'https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.2.12/vfs_fonts.js'
    );
    pdfMake = self.pdfMake;
    pdfMake.vfs = self.pdfMake.vfs || {};
  }
  const op = { method: type === 'blob' ? 'createBlob' : type === 'dataUrl' ? 'createDataUrl' : 'download' };
  let result;
  if (type === 'blob') result = pdfMake.createPdf(docDefinition).getBlob();
  else if (type === 'dataUrl') result = pdfMake.createPdf(docDefinition).getDataUrl();
  else pdfMake.createPdf(docDefinition).download(docDefinition.info?.title || 'documento.pdf');
  self.postMessage({ result });
});
