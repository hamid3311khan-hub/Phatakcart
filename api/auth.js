const { Pool } = require('pg');
const bcrypt = require('bcryptjs');
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false }
});

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();

  const { action } = req.query;

  try {
    if (action === 'register' && req.method === 'POST') {
      const { name, email, password, phone, address } = req.body;
      const hashed = await bcrypt.hash(password, 10);
      
      const result = await pool.query(`
        INSERT INTO users (name, email, password, phone, address)
        VALUES ($1, $2, $3, $4, $5) RETURNING id, name, email, role
      `, [name, email, hashed, phone, address]);
      
      return res.status(200).json({ user: result.rows[0] });
    }

    if (action === 'login' && req.method === 'POST') {
      const { email, password } = req.body;
      const result = await pool.query(`SELECT * FROM users WHERE email = $1`, [email]);
      
      if (result.rows.length === 0) return res.status(401).json({ error: 'User not found' });
      
      const user = result.rows[0];
      const match = await bcrypt.compare(password, user.password);
      if (!match) return res.status(401).json({ error: 'Wrong password' });
      
      delete user.password;
      return res.status(200).json({ user });
    }

    return res.status(404).json({ error: 'Invalid action' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};
