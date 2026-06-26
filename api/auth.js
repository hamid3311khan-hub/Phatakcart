const express = require('express');
const { Pool } = require('pg');
const bcrypt = require('bcryptjs');
const router = express.Router();

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false }
});

router.post('/', async (req, res) => {
  const { action } = req.query;
  const { name, email, password } = req.body;

  try {
    if (action === 'signup') {
      if (!name ||!email ||!password) {
        return res.status(400).json({ error: 'All fields required' });
      }
      const hashed = await bcrypt.hash(password, 10);
      const result = await pool.query(
        'INSERT INTO users (name, email, password) VALUES ($1, $2, $3) RETURNING id, name, email',
        [name, email, hashed]
      );
      return res.status(201).json({ user: result.rows[0] });
    }

    if (action === 'login') {
      if (!email ||!password) {
        return res.status(400).json({ error: 'Email and password required' });
      }
      const result = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
      if (result.rows.length === 0) {
        return res.status(400).json({ error: 'User not found' });
      }

      const user = result.rows[0];
      const valid = await bcrypt.compare(password, user.password);
      if (!valid) {
        return res.status(400).json({ error: 'Invalid password' });
      }

      return res.status(200).json({
        user: { id: user.id, name: user.name, email: user.email }
      });
    }

    res.status(400).json({ error: 'Invalid action' });
  } catch (error) {
    if (error.code === '23505') {
      return res.status(400).json({ error: 'Email already exists' });
    }
    console.error(error);
    res.status(500).json({ error: 'Server error' });
  }
});

module.exports = router;
