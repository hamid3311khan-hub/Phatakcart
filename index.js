const express = require('express')
const path = require('path')
const app = express()
const port = process.env.PORT || 10000

// Middleware
app.use(express.json())
app.use(express.static('public'))

// PAGES KE ROUTES
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'))
})

app.get('/food', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'food.html'))
})

app.get('/cart', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'cart.html'))
})

// API ROUTES - AB ALAG FILES SE AAYENGE
app.use('/api/cart', require('./api/cart'))
app.use('/api/products', require('./api/products'))
app.use('/api/setup', require('./api/setup'))

// SERVER START
app.listen(port, () => {
  console.log(`Server running on port ${port}`)
})
