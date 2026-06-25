const express = require('express')
const router = express.Router()
const { Pool } = require('pg')

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false }
})

// Get products - category filter ke saath
router.get('/', async (req, res) => {
  try {
    const { cat } = req.query
    let query = 'SELECT * FROM products WHERE active = true'
    let params = []
    
    if (cat) {
      query += ' AND category = $1'
      params.push(parseInt(cat))
    }
    
    query += ' ORDER BY id DESC'
    
    const result = await pool.query(query, params)
    res.json(result.rows)
  } catch (err) {
    console.error('Products API Error:', err)
    res.status(500).json({ error: err.message })
  }
})

// Add product - vendor ke liye
router.post('/', async (req, res) => {
  try {
    const { vendorId, name, price, offerPrice, category, imageUrl, description } = req.body
    
    await pool.query(`
      INSERT INTO products (vendor_id, name, price, offer_price, category, image_url, description, active) 
      VALUES ($1, $2, $3, $4, $5, $6, $7, true)
    `, [vendorId, name, price, offerPrice, parseInt(category), imageUrl, description])
    
    res.json({ success: true, message: 'Product add ho gaya' })
  } catch (err) {
    res.status(500).json({ success: false, error: err.message })
  }
})

// Get vendor products
router.get('/vendor/:vendorId', async (req, res) => {
  try {
    const result = await pool.query(
      'SELECT * FROM products WHERE vendor_id = $1 ORDER BY id DESC',
      [req.params.vendorId]
    )
    res.json(result.rows)
  } catch (err) {
    res.status(500).json({ error: err.message })
  }
})

module.exports = router
