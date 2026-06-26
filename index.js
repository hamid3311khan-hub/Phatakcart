const express = require('express');
const path = require('path');
const app = express();

app.use(express.json());
app.use(express.static('public'));

// API Routes
app.use('/api/auth', require('./api/auth'));
app.use('/api/setup', require('./api/setup'));
app.use('/api/products', require('./api/products'));
app.use('/api/cart', require('./api/cart'));
app.use('/api/order', require('./api/order'));
app.use('/api/admin', require('./api/admin'));

// Serve frontend
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`PhatakCart running on port ${PORT}`);
});
