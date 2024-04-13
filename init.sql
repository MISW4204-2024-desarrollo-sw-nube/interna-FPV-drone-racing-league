CREATE TABLE Video (
    id SERIAL PRIMARY KEY,
    status VARCHAR(10) NOT NULL,
    uploaded_file_url VARCHAR(255) NOT NULL,
    created_on TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NULL,
    processed_file_url VARCHAR(255) NULL
)