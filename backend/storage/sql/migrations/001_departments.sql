CREATE TABLE IF NOT EXISTS departments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT now()
);

INSERT INTO departments (
    name,
    display_name
)
VALUES
('engineering', 'Engineering'),
('hr', 'Human Resources'),
('finance', 'Finance'),
('operations', 'Operations'),
('public', 'Public')
ON CONFLICT (name) DO NOTHING;