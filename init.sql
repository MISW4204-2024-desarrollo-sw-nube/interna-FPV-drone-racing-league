CREATE TABLE Video (
    id SERIAL PRIMARY KEY,
    status VARCHAR(255) NOT NULL,
    inprogress_file_url VARCHAR(255) NOT NULL,
    created_on TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NULL,
    complete_file_url VARCHAR(255) NULL
)