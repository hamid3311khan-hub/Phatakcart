const express = require('express');
const app = express();
const path = require('path');

app.use(express.json());
app.use(express.static('.'));

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

app.use('/api/products', require('./api/products.js'));
app.use('/api/setup', require('./api/setup.js'));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Phatakcart running on ${PORT}`));
