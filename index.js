const express = require('express')
const path = require('path')
const app = express()
const port = process.env.PORT || 10000

// YE 2 LINES SABSE ZARURI HAIN ⚠️
app.use(express.json()) // API ke liye POST data padhne ke liye
app.use(express.static('public')) // HTML files serve karne ke liye

// Home page
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'))
})

// Server start
app.listen(port, () => {
  console.log(`Server running on port ${port}`)
})
