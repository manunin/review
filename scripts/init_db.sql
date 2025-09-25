-- Initialize the database schema
-- This script is run when the PostgreSQL container starts for the first time

-- Create extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Note: The actual tables will be created by Alembic migrations
-- This script just sets up the basic database structure

-- Grant permissions to the application user
GRANT ALL PRIVILEGES ON DATABASE review_db TO postgres;

-- You can add any additional initialization here
-- For example, creating indexes, setting up initial data, etc.

-- Example: Create a function for updated timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';
