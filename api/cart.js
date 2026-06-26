const { sql } = require('@vercel/postgres');

module.exports = async (req, res) => {
  const { action } = req.query;

  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,DELETE,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  try {
    // 1. CART MEIN PRODUCT ADD KARO
    if (action === 'add' && req.method === 'POST') {
      const { user_id, product_id, quantity = 1 } = req.body;

      if (!user_id ||!product_id) {
        return res.status(400).json({ error: 'user_id, product_id required' });
      }

      // Check product stock
      const product = await sql`SELECT stock FROM products WHERE id = ${product_id}`;
      if (product.rows.length === 0 || product.rows[0].stock < quantity) {
        return res.status(400).json({ error: 'Stock nahi hai' });
      }

      // Check cart mein pehle se hai kya
      const existing = await sql`
        SELECT * FROM cart WHERE user_id = ${user_id} AND product_id = ${product_id}
      `;

      if (existing.rows.length > 0) {
        // Quantity update kar do
        const newQty = existing.rows[0].quantity + parseInt(quantity);
        await sql`
          UPDATE cart SET quantity = ${newQty}
          WHERE user_id = ${user_id} AND product_id = ${product_id}
        `;
      } else {
        // Naya add kar do
        await sql`
          INSERT INTO cart (user_id, product_id, quantity)
          VALUES (${user_id}, ${product_id}, ${quantity})
        `;
      }

      return res.status(200).json({ message: 'Cart mein add ho gaya' });
    }

    // 2. CART DIKHAO
    if (action === 'view' && req.method === 'GET') {
      const { user_id } = req.query;
      
      if (!user_id) {
        return res.status(400).json({ error: 'user_id required' });
      }

      const result = await sql`
        SELECT
          c.id as cart_id,
          c.quantity,
          p.id as product_id,
          p.name,
          p.price,
          p.offer_price,
          p.image_url,
          p.stock,
          v.shop_name,
          CASE
            WHEN p.vendor_id IS NOT NULL THEN 'vendor'
            WHEN p.admin_id IS NOT NULL THEN 'admin'
          END as seller_type
        FROM cart c
        JOIN products p ON c.product_id = p.id
        LEFT JOIN vendors v ON p.vendor_id = v.id
        WHERE c.user_id = ${user_id} AND p.is_active = true
      `;

      let total = 0;
      const cartItems = result.rows.map(item => {
        const price = item.offer_price || item.price;
        total += price * item.quantity;
        return { ...item, item_total: price * item.quantity };
      });

      return res.status(200).json({
        cart: cartItems,
        total_amount: total
      });
    }

    // 3. QUANTITY UPDATE KARO
    if (action === 'update' && req.method === 'POST') {
      const { user_id, product_id, quantity } = req.body;

      if (quantity <= 0) {
        // Delete kar do agar 0 hai
        await sql`DELETE FROM cart WHERE user_id = ${user_id} AND product_id = ${product_id}`;
        return res.status(200).json({ message: 'Item remove ho gaya' });
      }

      await sql`
        UPDATE cart SET quantity = ${quantity}
        WHERE user_id = ${user_id} AND product_id = ${product_id}
      `;

      return res.status(200).json({ message: 'Quantity update ho gayi' });
    }

    // 4. CART SE ITEM DELETE KARO
    if (action === 'remove' && req.method === 'DELETE') {
      const { user_id, product_id } = req.body;

      await sql`DELETE FROM cart WHERE user_id = ${user_id} AND product_id = ${product_id}`;
      return res.status(200).json({ message: 'Item delete ho gaya' });
    }

    // 5. PURA CART CLEAR KARO - Order ke baad
    if (action === 'clear' && req.method === 'POST') {
      const { user_id } = req.body;

      await sql`DELETE FROM cart WHERE user_id = ${user_id}`;
      return res.status(200).json({ message: 'Cart clear ho gaya' });
    }

    return res.status(404).json({ error: 'Invalid action' });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};
