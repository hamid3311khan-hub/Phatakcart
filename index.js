import express from 'express';
import pg from 'pg';
import formidable from 'formidable';
import fs from 'fs';

const { Pool } = pg;
const app = express();
const port = process.env.PORT || 10000;

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false }
});

app.use(express.static('public'));
app.use(express.json());

app.get('/api/test', (req, res) => {
  res.json({ success: true, message: 'API Chal Rahi Hai Baba' });
});

app.post('/api/register', (req, res) => {
  const form = formidable({
    maxFileSize: 1.5 * 1024 * 1024, // ← BAS YE LINE FIX KI HAI. Pehle 1.5 * 1024 tha
    maxTotalFileSize: 3 * 1024 * 1024, // ← YE BHI FIX KI HAI
  });

  form.parse(req, async (err, fields, files) => {
    if (err) {
      console.log('Formidable Error:', err);
      return res.status(400).json({
        success: false,
        message: 'File bahut badi hai. 1.5MB se chhoti rakho'
      });
    }

    const shopName = fields.shopName?.[0];
    const phone = fields.phone?.[0];
    const password = fields.password?.[0];
    const address = fields.address?.[0];
    const aadhar = files.aadhar?.[0];
    const electricity = files.electricity?.[0];

    if (!shopName ||!phone ||!password ||!address ||!aadhar ||!electricity) {
      return res.status(400).json({
        success: false,
        message: 'Saare fields aur documents chahiye'
      });
    }

    try {
      const aadharBase64 = 'data:' + aadhar.mimetype + ';base64,' + fs.readFileSync(aadhar.filepath, 'base64');
      const electricityBase64 = 'data:' + electricity.mimetype + ';base64,' + fs.readFileSync(electricity.filepath, 'base64');

      await pool.query(
        `INSERT INTO vendors (shop_name, phone, password, address, aadhar_url, electricity_bill_url, kyc_status, active)
         VALUES ($1, $2, $3, $4, $5, $6, 'pending', false)`,
        [shopName, phone, password, address, aadharBase64, electricityBase64]
      );

      res.status(200).json({ success: true, message: 'Registration ho gaya!' });
    } catch (err) {
      console.log('DB Error:', err);
      if (err.code === '23505') {
        res.status(400).json({ success: false, message: 'Phone number already registered' });
      } else {
        res.status(500).json({ success: false, message: 'Database error' });
      }
    }
  });
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
