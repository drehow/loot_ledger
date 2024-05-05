/* wipe

DROP DATABASE IF EXISTS personal_finances;

*/
CREATE DATABASE IF NOT EXISTS personal_finances;

CREATE SCHEMA IF NOT EXISTS fin;

CREATE TABLE IF NOT EXISTS fin.account (
    id INT AUTOINCREMENT NOT NULL,
    name VARCHAR(255) NOT NULL,
    automated BOOLEAN NOT NULL,
    activated_date DATE NOT NULL,
    deactivated_date DATE,
    ra_score INT NOT NULL,
    asset BOOLEAN NOT NULL,
    PRIMARY KEY (id)
)

CREATE TABLE IF NOT EXISTS fin.category (
    id INT AUTOINCREMENT NOT NULL,
    name VARCHAR(255) NOT NULL,
    income_statement_group varchar(255) NOT NULL,
    PRIMARY KEY (id)
))
