const { Client } = require('pg');

module.exports = async (req, res) => {
  const client = new Client({
    connectionString: process.env.DATABASE_URL,
    ssl: { rejectUnauthorized: false }
  });
  const cat = req.query.cat || 1;
  await client.connect();
  const result = await client.query('SELECT * FROM products WHERE category_id = $1', [cat]);
  await client.end();
  res.status(200).json(result.rows);
};
