const express = require('express')
const router = express.Router()

// Abhi ke liye dummy cart data
let cartItems = [
  { id: 1, name: 'Chicken Biryani', price: 250, qty: 2 },
  { id: 3, name: 'Veg Burger', price: 80, qty: 1 }
]

// GET /api/cart - Cart ke items bhejo
router.get('/', (req, res) => {
  res.status(200).json(cartItems)
})

// POST /api/cart - Cart mein item add karo
router.post('/', (req, res) => {
  const { productId, qty } = req.body
  res.status(200).json({ 
    success: true, 
    message: `Product ${productId} added with qty ${qty}` 
  })
})

module.exports = router
