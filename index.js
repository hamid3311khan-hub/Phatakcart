const express = require('express');
const path = require('path');
const productsAPI = require('./api/products.js');
const setupAPI = require('./api/setup.js');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// API Routes
app.get('/api/products', productsAPI);
app.get('/api/setup', setupAPI);

app.listen(PORT, () => {
  console.log(`Phatakcart server running on port ${PORT}`);
});
const express = require('express')
const path = require('path')
const app = express()
const port = process.env.PORT || 10000

app.use(express.json())
app.use(express.static('public'))

// HOME PAGE
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'))
})

// FOOD PAGE - YE NAYA ADD KAR ⚠️
app.get('/food', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'food.html'))
})

// CART PAGE - YE BHI ADD KAR DE
app.get('/cart', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'cart.html'))
})

// APIs same rahenge
app.get('/api/products', (req, res) => {
  res.json([
    { id: 1, name: 'Chicken Biryani', price: 250 },
    { id: 2, name: 'Paneer Tikka', price: 180 }
  ])
})

app.get('/api/cart', (req, res) => {
  res.json([
    { id: 1, name: 'Chicken Biryani', price: 250, qty: 2 },
    { id: 3, name: 'Veg Burger', price: 80, qty: 1 }
  ])
})

app.listen(port, () => {
  console.log(`Server running on port ${port}`)
})
