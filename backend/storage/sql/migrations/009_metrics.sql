CREATE TABLE IF NOT EXISTS metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    endpoint TEXT NOT NULL,
    user_id UUID REFERENCES users(id),
    latency FLOAT,
    tokens INT,
    status TEXT,
    error_message TEXT,
    agent_name TEXT,
    retrieval_count INT,
    created_at TIMESTAMP DEFAULT now()
);