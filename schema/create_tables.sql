CREATE DATABASE library_db;
USE library_db;
USE library_db;

CREATE TABLE books (
    book_id         INT             AUTO_INCREMENT PRIMARY KEY,
    isbn            VARCHAR(13)     NOT NULL UNIQUE,
    title           VARCHAR(255)    NOT NULL,
    author          VARCHAR(255)    NOT NULL,
    genre           VARCHAR(50)     NOT NULL,
    year_published  SMALLINT        CHECK (year_published > 0),
    total_copies    INTEGER         NOT NULL DEFAULT 1,
    available_copies INTEGER        NOT NULL DEFAULT 1,
    added_at        DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE members (
    member_id       INT             AUTO_INCREMENT PRIMARY KEY,
    full_name       VARCHAR(100)    NOT NULL,
    email           VARCHAR(150)    NOT NULL UNIQUE,
    phone           VARCHAR(20),
    join_date       DATE            NOT NULL DEFAULT (CURRENT_DATE),
    expiry_date     DATE            NOT NULL,
    membership_type VARCHAR(20)     NOT NULL DEFAULT 'standard',
    status          VARCHAR(10)     NOT NULL DEFAULT 'active',
    CONSTRAINT chk_membership CHECK (membership_type IN ('standard','premium','student')),
    CONSTRAINT chk_status CHECK (status IN ('active','suspended','expired'))
);

CREATE TABLE loans (
    loan_id         INT             AUTO_INCREMENT PRIMARY KEY,
    book_id         INTEGER         NOT NULL,
    member_id       INTEGER         NOT NULL,
    loan_date       DATE            NOT NULL DEFAULT (CURRENT_DATE),
    due_date        DATE            NOT NULL,
    return_date     DATE,
    renewed_count   SMALLINT        NOT NULL DEFAULT 0,
    FOREIGN KEY (book_id)   REFERENCES books(book_id),
    FOREIGN KEY (member_id) REFERENCES members(member_id)
);

CREATE TABLE fines (
    fine_id         INT             AUTO_INCREMENT PRIMARY KEY,
    loan_id         INTEGER         NOT NULL,
    member_id       INTEGER         NOT NULL,
    amount          DECIMAL(8,2)    NOT NULL CHECK (amount > 0),
    issued_date     DATE            NOT NULL DEFAULT (CURRENT_DATE),
    paid            TINYINT(1)      NOT NULL DEFAULT 0,
    paid_date       DATE,
    FOREIGN KEY (loan_id)   REFERENCES loans(loan_id),
    FOREIGN KEY (member_id) REFERENCES members(member_id)
);

CREATE TABLE reservations (
    reservation_id  INT             AUTO_INCREMENT PRIMARY KEY,
    book_id         INTEGER         NOT NULL,
    member_id       INTEGER         NOT NULL,
    reserved_date   DATE            NOT NULL DEFAULT (CURRENT_DATE),
    queue_position  INTEGER         NOT NULL,
    notified        TINYINT(1)      NOT NULL DEFAULT 0,
    FOREIGN KEY (book_id)   REFERENCES books(book_id),
    FOREIGN KEY (member_id) REFERENCES members(member_id),
    UNIQUE (book_id, queue_position)
);
