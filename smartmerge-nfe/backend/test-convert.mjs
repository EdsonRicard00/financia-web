const xmlContent = '<root><element>teste</element></root>';
const formData = new FormData();
formData.append('files', new Blob([xmlContent], { type: 'text/xml' }), 'test.xml');

const response = await fetch('http://localhost:5000/api/convert-xml', {
  method: 'POST',
  body: formData,
});

console.log('status', response.status);
console.log('content-type', response.headers.get('content-type'));
if (response.ok) {
  const buffer = await response.arrayBuffer();
  console.log('bytes', buffer.byteLength);
} else {
  console.log('body', await response.text());
}
