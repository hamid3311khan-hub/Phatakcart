const { Pool } = require('pg');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false }
});

module.exports = async (req, res) => {
  try {
    // Table banao
    await pool.query(`
      CREATE TABLE IF NOT EXISTS products (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        price INTEGER NOT NULL,
        category INTEGER NOT NULL
      )
    `);

    // Data daalo
    await pool.query(`
      INSERT INTO products (name, price, category) VALUES
      ('Chicken Biryani', 250, 1),
      ('Paneer Tikka', 180, 1),
      ('Veg Burger', 80, 1),
      ('Chicken Roll', 120, 1),
      ('Cotton Kurta', 599, 2),
      ('Jeans', 899, 2),
      ('T-Shirt', 399, 2),
      ('Aashirvaad Atta 5kg', 280, 3),
      ('Tata Salt 1kg', 25, 3)
      ON CONFLICT DO NOTHING
    `);

    res.json({ message: 'Database setup complete. Products added.' });
  } catch (err) {
    console.error('Setup Error:', err);
    res.status(500).json({ error: err.message });
  }
};
