CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_type TEXT NOT NULL,
    department_id UUID REFERENCES departments(id),
    visibility TEXT NOT NULL DEFAULT 'department',
    version INT DEFAULT 1,
    status TEXT DEFAULT 'pending',
    page_count INT,
    uploaded_by UUID REFERENCES users(id),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);