const express = require('express');
const mysql = require('mysql2');
const cors = require('cors');
const bodyParser = require('body-parser');

const app = express();

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(express.static('public'));

// Database connection
const db = mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: 'Vemalatha@0704', // Leave empty if you haven't set a password
    database: 'aorbo_contacts'
});

// Connect to database
db.connect((err) => {
    if (err) {
        console.error('Error connecting to MySQL database:', err);
        return;
    }
    console.log('Connected to MySQL database');
});

// API endpoint to handle form submissions
app.post('/api/contact', (req, res) => {
    const { name, email, mobile, userType, comment } = req.body;
    
    const query = 'INSERT INTO contacts (name, email, mobile, user_type, comment) VALUES (?, ?, ?, ?, ?)';
    const values = [name, email, mobile, userType, comment];

    db.query(query, values, (err, result) => {
        if (err) {
            console.error('Error saving contact form:', err);
            res.status(500).json({ error: 'Error saving your information' });
            return;
        }
        res.status(200).json({ message: 'Contact form submitted successfully' });
    });
});

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
