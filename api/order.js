const { sql } = require('@vercel/postgres');
const Razorpay = require('razorpay');

module.exports = async (req, res) => {
  const { action } = req.query;

  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  try {
    // 1. CHECKOUT - Order create karo + Razorpay order banao
    if (action === 'checkout' && req.method === 'POST') {
      const { user_id, shipping_address } = req.body;

      if (!user_id ||!shipping_address) {
        return res.status(400).json({ error: 'user_id, shipping_address required' });
      }

      // Cart se items nikalo
      const cartResult = await sql`
        SELECT
          c.product_id,
          c.quantity,
          p.price,
          p.offer_price,
          p.vendor_id,
          p.stock
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ${user_id} AND p.is_active = true
      `;

      if (cartResult.rows.length === 0) {
        return res.status(400).json({ error: 'Cart empty hai' });
      }

      // Total calculate karo
      let total = 0;
      for (let item of cartResult.rows) {
        const price = item.offer_price || item.price;
        total += price * item.quantity;

        // Stock check
        if (item.stock < item.quantity) {
          return res.status(400).json({ error: `Stock kam hai product ID ${item.product_id} ke liye` });
        }
      }

      // Order create karo
      const orderResult = await sql`
        INSERT INTO orders (user_id, total_amount, shipping_address, status, payment_status)
        VALUES (${user_id}, ${total}, ${shipping_address}, 'pending', 'pending')
        RETURNING *
      `;

      const order = orderResult.rows[0];

      // Order items insert karo
      for (let item of cartResult.rows) {
        const price = item.offer_price || item.price;
        await sql`
          INSERT INTO order_items (order_id, product_id, vendor_id, quantity, price)
          VALUES (${order.id}, ${item.product_id}, ${item.vendor_id}, ${item.quantity}, ${price})
        `;

        // Stock kam karo
        await sql`
          UPDATE products SET stock = stock - ${item.quantity}
          WHERE id = ${item.product_id}
        `;
      }

      // Razorpay order banao - API keys Render env mein dalna
      const razorpay = new Razorpay({
        key_id: process.env.RAZORPAY_KEY_ID,
        key_secret: process.env.RAZORPAY_KEY_SECRET,
      });

      const razorpayOrder = await razorpay.orders.create({
        amount: Math.round(total * 100), // paise mein
        currency: 'INR',
        receipt: `order_${order.id}`,
      });

      // Order mein razorpay order id update karo
      await sql`
        UPDATE orders SET payment_id = ${razorpayOrder.id}
        WHERE id = ${order.id}
      `;

      return res.status(201).json({
        message: 'Order created',
        order_id: order.id,
        razorpay_order_id: razorpayOrder.id,
        amount: total,
        key_id: process.env.RAZORPAY_KEY_ID
      });
    }

    // 2. PAYMENT SUCCESS - Order confirm karo
    if (action === 'verify' && req.method === 'POST') {
      const { razorpay_order_id, razorpay_payment_id, razorpay_signature } = req.body;

      // Signature verify karo - production mein zaroori
      const crypto = require('crypto');
      const hmac = crypto.createHmac('sha256', process.env.RAZORPAY_KEY_SECRET);
      hmac.update(razorpay_order_id + '|' + razorpay_payment_id);
      const generated_signature = hmac.digest('hex');

      if (generated_signature!== razorpay_signature) {
        return res.status(400).json({ error: 'Payment verification failed' });
      }

      // Order update karo
      const result = await sql`
        UPDATE orders
        SET payment_status = 'paid', status = 'confirmed'
        WHERE payment_id = ${razorpay_order_id}
        RETURNING *
      `;

      if (result.rows.length === 0) {
        return res.status(404).json({ error: 'Order nahi mila' });
      }

      const order = result.rows[0];

      // Cart clear karo
      await sql`DELETE FROM cart WHERE user_id = ${order.user_id}`;

      return res.status(200).json({
        message: 'Payment success',
        order_id: order.id
      });
    }

    // 3. USER KE ORDERS DEKHO
    if (action === 'my-orders' && req.method === 'GET') {
      const { user_id } = req.query;

      const result = await sql`
        SELECT * FROM orders
        WHERE user_id = ${user_id}
        ORDER BY created_at DESC
      `;

      return res.status(200).json({ orders: result.rows });
    }

    // 4. ORDER DETAIL + ITEMS
    if (action === 'detail' && req.method === 'GET') {
      const { order_id } = req.query;

      const orderResult = await sql`SELECT * FROM orders WHERE id = ${order_id}`;

      if (orderResult.rows.length === 0) {
        return res.status(404).json({ error: 'Order nahi mila' });
      }

      const itemsResult = await sql`
        SELECT
          oi.*,
          p.name,
          p.image_url,
          v.shop_name
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        LEFT JOIN vendors v ON oi.vendor_id = v.id
        WHERE oi.order_id = ${order_id}
      `;

      return res.status(200).json({
        order: orderResult.rows[0],
        items: itemsResult.rows
      });
    }

    return res.status(404).json({ error: 'Invalid action' });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};
