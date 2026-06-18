CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,
    hashed_password TEXT NOT NULL,
    full_name TEXT NOT NULL,
    department_id UUID REFERENCES departments(id),
    role TEXT NOT NULL DEFAULT 'employee',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT now(),
    last_login TIMESTAMP
);