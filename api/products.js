const express = require('express')
const router = express.Router()
const { Pool } = require('pg')

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false }
})

router.get('/', async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT p.*, v.shop_name
      FROM products p
      LEFT JOIN vendors v ON p.vendor_id = v.id
      WHERE p.active = true
      ORDER BY p.id DESC
    `)
    res.json(result.rows)
  } catch (err) {
    res.status(500).json({ error: err.message })
  }
})

module.exports = router
