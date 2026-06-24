const { Pool } = require('pg');
const pool = new Pool({ connectionString: process.env.DATABASE_URL });

module.exports = async (req, res) => {
  try {
    await pool.query(`
      CREATE TABLE IF NOT EXISTS products (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        price INTEGER,
        category VARCHAR(50),
        image VARCHAR(255)
      );
    `);
    
    await pool.query(`TRUNCATE TABLE products RESTART IDENTITY;`);
    
    await pool.query(`
      INSERT INTO products (name, price, category, image) VALUES
      ('Chicken Biryani', 180, 'food', 'https://i.imgur.com/8QZQZ8p.jpg'),
      ('Veg Biryani', 120, 'food', 'https://i.imgur.com/8QZQZ8p.jpg'),
      ('Mutton Biryani', 220, 'food', 'https://i.imgur.com/8QZQZ8p.jpg');
    `);
    
    res.json({ message: 'DB Setup Done ✅ Phatakcart Ready' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: err.message });
  }
};
