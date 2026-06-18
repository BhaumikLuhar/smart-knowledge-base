CREATE TABLE IF NOT EXISTS chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    chunk_index INT NOT NULL,
    page_number INT,
    embedding_ref TEXT,
    department_id UUID REFERENCES departments(id),
    visibility TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT now()
);