-- Drop the database if it exists
DROP DATABASE IF EXISTS aorbo_contacts;

-- Create the database
CREATE DATABASE aorbo_contacts;

-- Use the database
USE aorbo_contacts;

-- Create contacts table
CREATE TABLE contacts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    mobile VARCHAR(20) NOT NULL,
    user_type VARCHAR(50),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
