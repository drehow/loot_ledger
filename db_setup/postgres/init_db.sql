/* 

WIPE AND RESET

In terminal:

psql -U postgres -h localhost -d postgres
password is mac password

run the following command:
\i db_setup/postgres/init_db.sql


*/
DROP DATABASE IF EXISTS personal_finances;

CREATE DATABASE personal_finances;

\c personal_finances

CREATE DATABASE personal_finances;
CREATE SCHEMA IF NOT EXISTS fin;

CREATE TABLE IF NOT EXISTS fin.account (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    automated BOOLEAN NOT NULL,
    activated_date DATE NOT NULL,
    deactivated_date DATE,
    ra_score INT NOT NULL,
    asset BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS fin.category (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    income_statement_group VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS fin.account_balance (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    date DATE NOT NULL,
    account_id INT NOT NULL,
    balance DECIMAL(10, 2) NOT NULL,
    manual BOOLEAN NOT NULL,

    FOREIGN KEY (account_id) REFERENCES fin.account(id)
);

CREATE TABLE IF NOT EXISTS fin.transaction (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    account_id INT NOT NULL,
    date DATE NOT NULL,
    xfer_account_id INT,
    category_id INT NOT NULL,
    description VARCHAR(255) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    note VARCHAR(255),
    manual BOOLEAN NOT NULL,

    FOREIGN KEY (account_id) REFERENCES fin.account(id),
    FOREIGN KEY (xfer_account_id) REFERENCES fin.account(id),
    FOREIGN KEY (category_id) REFERENCES fin.category(id)
);

-- Insert personal data
\i db_setup/postgres/init_account.sql
\i db_setup/postgres/init_category.sql
\i db_setup/postgres/init_account_balance.sql
\i db_setup/postgres/init_transaction.sql