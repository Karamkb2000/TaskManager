CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    done BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO tasks (title, description) VALUES
    ('Learn Docker', 'Understand containers, images, and volumes'),
    ('Learn Docker Compose', 'Multi-container apps made easy'),
    ('Deploy something', 'Put a real app on a server');
