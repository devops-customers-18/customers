CREATE USER tester WITH PASSWORD 'test101';
CREATE DATABASE customers ;
\c customers;

CREATE TABLE IF NOT EXISTS Users (
    First_Name VARCHAR(20) NOT NULL,
    Last_Name VARCHAR(20) NOT NULL,
    Username VARCHAR(255) NOT NULL,
    Password VARCHAR(255) NOT NULL,
    Email VARCHAR(255),
    Address TEXT,
    Phone_Number VARCHAR(20),
    Title VARCHAR(20),
    Active BOOLEAN NOT NULL
);


GRANT ALL PRIVILEGES ON users TO tester;

