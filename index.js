const express = require('express');
const path = require('path');
const app = express();
const port = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static('public'));

// API Routes
app.use('/api/products', require('./api/products'));
app.use('/api/setup', require('./api/setup'));

// HTML Routes
app.get('/food', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'food.html'));
});

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
