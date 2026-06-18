CREATE TABLE IF NOT EXISTS document_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id),
    version INT NOT NULL,
    file_path TEXT NOT NULL,
    uploaded_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT now()
);