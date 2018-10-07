CREATE DATABASE IF NOT EXISTS customers;

USE customers;

CREATE TABLE IF NOT EXISTS Users (
    Id INT NOT NULL,
    First_Name VARCHAR(20) NOT NULL,
    Last_Name VARCHAR(20) NOT NULL,
    Username VARCHAR(255) NOT NULL,
    Password VARCHAR(255) NOT NULL,
    Email VARCHAR(255),
    Address TEXT,
    Phone_Number VARCHAR(20),
    Title VARCHAR(20),
    PRIMARY KEY (Id)
);