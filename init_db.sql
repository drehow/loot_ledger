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
)

CREATE TABLE IF NOT EXISTS fin.account_balance (
    id INT AUTOINCREMENT NOT NULL,
    date DATE NOT NULL,
    account_id INT NOT NULL,
    balance DECIMAL(10, 2) NOT NULL,
    manual BOOLEAN NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (account_id) REFERENCES fin.account(id)
)

-- id	account_id	date	to_account_id	from_account_id	category_id	description	amount	note
CREATE TABLE IF NOT EXISTS fin.transaction (
    id INT AUTOINCREMENT NOT NULL,
    account_id INT NOT NULL,
    date DATE NOT NULL,
    to_account_id INT,
    from_account_id INT,
    category_id INT NOT NULL,
    description VARCHAR(255) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    note VARCHAR(255),
    PRIMARY KEY (id),
    FOREIGN KEY (account_id) REFERENCES fin.account(id),
    FOREIGN KEY (to_account_id) REFERENCES fin.account(id),
    FOREIGN KEY (from_account_id) REFERENCES fin.account(id),
    FOREIGN KEY (category_id) REFERENCES fin.category(id)
)

