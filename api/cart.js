const express = require('express')
const router = express.Router()

// SHURU MEIN CART KHALI RAHEGA
let cartItems = []

// Products ka data - id check kar isme Fortune Oil ka id 10 hai
const allProducts = [
  { id: 1, name: 'Chicken Biryani', price: 250 },
  { id: 2, name: 'Paneer Tikka', price: 180 },
  { id: 3, name: 'Veg Burger', price: 80 },
  { id: 4, name: 'Chicken Roll', price: 120 },
  { id: 5, name: 'Cotton Kurta', price: 599 },
  { id: 6, name: 'Jeans', price: 899 },
  { id: 7, name: 'T-Shirt', price: 399 },
  { id: 8, name: 'Aashirvaad Atta 5kg', price: 280 },
  { id: 9, name: 'Tata Salt 1kg', price: 25 },
  { id: 10, name: 'Fortune Oil 1L', price: 130 }  // ID 10 HAI ISKA
]

// GET /api/cart - Khali cart dikhega ab
router.get('/', (req, res) => {
  res.status(200).json(cartItems)
})

// POST /api/cart - Add karo
router.post('/', (req, res) => {
  const { productId, qty } = req.body
  
  const product = allProducts.find(p => p.id == productId)
  if (!product) {
    return res.status(404).json({ success: false, message: 'Product nahi mila' })
  }
  
  const existingItem = cartItems.find(item => item.id == productId)
  
  if (existingItem) {
    existingItem.qty += qty
  } else {
    cartItems.push({
      id: product.id,
      name: product.name,
      price: product.price,
      qty: qty
    })
  }
  
  res.status(200).json({ success: true, message: `${product.name} add ho gaya` })
})

// DELETE /api/cart/:id - REMOVE SYSTEM
router.delete('/:id', (req, res) => {
  const id = parseInt(req.params.id)
  cartItems = cartItems.filter(item => item.id !== id)
  res.json({ success: true, message: 'Item remove ho gaya' })
})
// PUT /api/cart/:id - Quantity Update karo
router.put('/:id', (req, res) => {
  const id = parseInt(req.params.id)
  const { qty } = req.body
  
  const item = cartItems.find(item => item.id === id)
  if (!item) {
    return res.status(404).json({ success: false })
  }
  
  item.qty = qty
  if (item.qty <= 0) {
    // 0 ho jaye to remove kar do
    cartItems = cartItems.filter(item => item.id !== id)
  }
  
  res.json({ success: true, message: 'Quantity updated' })
})
module.exports = router
