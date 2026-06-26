const express = require('express');
const path = require('path');
const app = express();

app.use(express.json());
app.use(express.static('public'));

// Sirf 2 routes rakhe hain abhi
app.use('/api/setup', require('./api/setup'));
app.use('/api/auth', require('./api/auth'));

// Baaki sab files hain par load nahi ho rahi, isliye crash nahi hoga
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'login.html'));
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on ${PORT}`));
