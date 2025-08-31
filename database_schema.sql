-- Database Schema for 11 Labs Multi-Agent System

-- Main conversations table
CREATE TABLE IF NOT EXISTS conversations (
    conversation_id TEXT PRIMARY KEY,
    transcript TEXT,
    user_id TEXT,
    user_name TEXT,
    call_duration INTEGER,
    success BOOLEAN,
    extracted_data JSONB,
    analysis_summary TEXT,
    evaluation_results JSONB,
    created_at TIMESTAMP WITH TIME ZONE,
    full_data JSONB,
    -- NEW: Multi-agent fields
    agent_id TEXT,
    track_type TEXT
);

-- User progress tracking table
CREATE TABLE IF NOT EXISTS user_progress (
    user_id TEXT PRIMARY KEY,
    track_type TEXT,
    current_agent TEXT,
    last_active TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User data points table (for cleaned extracted data)
CREATE TABLE IF NOT EXISTS user_data_points (
    id SERIAL PRIMARY KEY,
    user_id TEXT,
    field_name TEXT,
    value TEXT,
    rationale TEXT,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at);
CREATE INDEX IF NOT EXISTS idx_user_data_points_user_id ON user_data_points(user_id);
CREATE INDEX IF NOT EXISTS idx_user_progress_user_id ON user_progress(user_id);
