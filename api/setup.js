const { sql } = require('@vercel/postgres');

module.exports = async (req, res) => {
  try {
    // 1. VENDORS TABLE - Shop wale
    await sql`
      CREATE TABLE IF NOT EXISTS vendors (
        id SERIAL PRIMARY KEY,
        shop_name VARCHAR(255) NOT NULL,
        owner_name VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        phone VARCHAR(20) NOT NULL,
        password VARCHAR(255) NOT NULL,
        address TEXT,
        kyc_doc VARCHAR(255),
        is_approved BOOLEAN DEFAULT false,
        created_at TIMESTAMP DEFAULT NOW()
      );
    `;

    // 2. USERS TABLE - Public customers
    await sql`
      CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        phone VARCHAR(20),
        password VARCHAR(255) NOT NULL,
        address TEXT,
        created_at TIMESTAMP DEFAULT NOW()
      );
    `;

    // 3. ADMIN TABLE - Tera account
    await sql`
      CREATE TABLE IF NOT EXISTS admin (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        name VARCHAR(255) DEFAULT 'Admin'
      );
    `;

    // 4. PRODUCTS TABLE - Tere + Vendor ke products
    await sql`
      CREATE TABLE IF NOT EXISTS products (
        id SERIAL PRIMARY KEY,
        vendor_id INTEGER REFERENCES vendors(id),
        admin_id INTEGER REFERENCES admin(id),
        name VARCHAR(255) NOT NULL,
        description TEXT,
        price DECIMAL(10,2) NOT NULL,
        offer_price DECIMAL(10,2),
        category VARCHAR(100),
        image_url VARCHAR(255),
        stock INTEGER DEFAULT 0,
        is_active BOOLEAN DEFAULT true,
        created_at TIMESTAMP DEFAULT NOW()
      );
    `;

    // 5. CART TABLE - Public ka cart
    await sql`
      CREATE TABLE IF NOT EXISTS cart (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        product_id INTEGER REFERENCES products(id),
        quantity INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT NOW()
      );
    `;

    // 6. ORDERS TABLE
    await sql`
      CREATE TABLE IF NOT EXISTS orders (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        total_amount DECIMAL(10,2) NOT NULL,
        status VARCHAR(50) DEFAULT 'pending',
        payment_status VARCHAR(50) DEFAULT 'pending',
        payment_id VARCHAR(255),
        shipping_address TEXT,
        created_at TIMESTAMP DEFAULT NOW()
      );
    `;

    // 7. ORDER_ITEMS TABLE
    await sql`
      CREATE TABLE IF NOT EXISTS order_items (
        id SERIAL PRIMARY KEY,
        order_id INTEGER REFERENCES orders(id),
        product_id INTEGER REFERENCES products(id),
        vendor_id INTEGER REFERENCES vendors(id),
        quantity INTEGER NOT NULL,
        price DECIMAL(10,2) NOT NULL
      );
    `;

    // Default admin create kar de
    await sql`
      INSERT INTO admin (email, password) 
      VALUES ('admin@yourshop.com', '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi')
      ON CONFLICT (email) DO NOTHING;
    `;

    res.status(200).json({ 
      message: 'Database setup complete ✅',
      admin_login: 'admin@yourshop.com',
      admin_password: 'password'
    });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};
