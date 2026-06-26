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
    if (action === 'signup' && req.method === 'POST') {
      const { name, email, password } = req.body;
      
      if (!name ||!email ||!password) {
        return res.status(400).json({ error: 'All fields required' });
      }

      const hashedPassword = await bcrypt.hash(password, 10);
      
      const result = await pool.query(`
        INSERT INTO users (name, email, password, role) 
        VALUES ($1, $2, $3, 'customer') 
        RETURNING id, name, email, role
      `, [name, email, hashedPassword]);

      return res.status(200).json({ 
        message: 'User created successfully',
        user: result.rows[0] 
      });
    }

    if (action === 'login' && req.method === 'POST') {
      const { email, password } = req.body;
      
      const result = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
      
      if (result.rows.length === 0) {
        return res.status(401).json({ error: 'Invalid email or password' });
      }

      const user = result.rows[0];
      const isValid = await bcrypt.compare(password, user.password);
      
      if (!isValid) {
        return res.status(401).json({ error: 'Invalid email or password' });
      }

      return res.status(200).json({ 
        message: 'Login successful',
        user: { id: user.id, name: user.name, email: user.email, role: user.role }
      });
    }

    return res.status(400).json({ error: 'Invalid action' });
    
  } catch (error) {
    if (error.code === '23505') {
      return res.status(400).json({ error: 'Email already exists' });
    }
    res.status(500).json({ error: error.message });
  }
};
