const { Pool } = require('pg');
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false }
});

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,DELETE,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();

  try {
    if (req.method === 'GET') {
      const { category } = req.query;
      let query = `SELECT * FROM products WHERE is_active = true`;
      let params = [];
      
      if (category) {
        query += ` AND category = $1`;
        params.push(category);
      }
      query += ` ORDER BY created_at DESC`;
      
      const result = await pool.query(query, params);
      return res.status(200).json({ products: result.rows });
    }

    if (req.method === 'POST') {
      const { name, description, price, category, image, admin_id } = req.body;
      const result = await pool.query(`
        INSERT INTO products (name, description, price, category, image, admin_id)
        VALUES ($1, $2, $3, $4, $5, $6) RETURNING *
      `, [name, description, price, category, image, admin_id]);
      return res.status(200).json({ product: result.rows[0] });
    }

    return res.status(404).json({ error: 'Invalid method' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};
