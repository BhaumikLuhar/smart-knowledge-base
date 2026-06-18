CREATE TABLE IF NOT EXISTS permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role TEXT NOT NULL,
    department_id UUID REFERENCES departments(id),
    can_access_department_id UUID REFERENCES departments(id),
    created_at TIMESTAMP DEFAULT now(),
    UNIQUE(role, department_id, can_access_department_id)
);