const express = require('express');
const path = require('path');
const app = express();

app.use(express.json());
app.use(express.static('public'));

// API Routes - Har file ko connect karo
const registerRoute = require('./api/register');
const vendorRoute = require('./api/vendor');
const cartRoute = require('./api/cart');
const orderRoute = require('./api/order');
const productsRoute = require('./api/products');
const addProductRoute = require('./api/add-product');
const setupRoute = require('./api/setup');

app.use('/api/register', registerRoute);
app.use('/api/vendor', vendorRoute);
app.use('/api/cart', cartRoute);
app.use('/api/order', orderRoute);
app.use('/api/products', productsRoute);
app.use('/api/add-product', addProductRoute);
app.use('/api/setup', setupRoute);

// HTML Pages
app.get('/vendor', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'vendor.html'));
});

app.get('/register', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'register.html'));
});

app.get('/cart', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'cart.html'));
});

app.get('/order', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'order.html'));
});

app.get('/products', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'products.html'));
});

app.get('/food', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'food.html'));
});

app.get('/grocery', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'grocery.html'));
});

app.get('/dress', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'dress.html'));
});

app.get('/payment', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'payment.html'));
});

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
