# Database Schema Updates for 3-Agent System

## Current Schema Analysis
Based on your app.py, you have:
- `conversations` table (stores full webhook data)
- `user_data_points` table (stores clean extracted data)

## Required Schema Updates

### 1. Add Agent Tracking Columns
```sql
-- Add agent identification to conversations table
ALTER TABLE conversations 
ADD COLUMN agent_id VARCHAR(50),
ADD COLUMN track_type VARCHAR(20); -- 'founder' or 'executive'

-- Add agent identification to user_data_points table
ALTER TABLE user_data_points 
ADD COLUMN agent_id VARCHAR(50),
ADD COLUMN track_type VARCHAR(20); -- 'founder' or 'executive'

-- Update existing records (set to your current agent)
UPDATE conversations SET agent_id = 'value_architect', track_type = 'founder' WHERE agent_id IS NULL;
UPDATE user_data_points SET agent_id = 'value_architect', track_type = 'founder' WHERE agent_id IS NULL;
```

### 2. Create User Progress Tracking Table
```sql
-- Track user's progress through agent sequence
CREATE TABLE user_agent_progress (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR(255) NOT NULL,
  track_type VARCHAR(20) NOT NULL, -- 'founder' or 'executive'
  agent_id VARCHAR(50) NOT NULL,   -- 'value_architect', 'positioning_strategist', 'growth_architect'
  status VARCHAR(20) NOT NULL,     -- 'not_started', 'in_progress', 'completed'
  started_at TIMESTAMP WITH TIME ZONE,
  completed_at TIMESTAMP WITH TIME ZONE,
  last_conversation_id VARCHAR(255),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  -- Ensure one record per user/track/agent combination
  UNIQUE(user_id, track_type, agent_id)
);

-- Create indexes for common queries
CREATE INDEX idx_user_agent_progress_user ON user_agent_progress(user_id);
CREATE INDEX idx_user_agent_progress_status ON user_agent_progress(status);
```

### 3. Add Completion Tracking Columns
```sql
-- Track data collection completion per section
ALTER TABLE user_data_points 
ADD COLUMN section_name VARCHAR(100), -- 'core_expertise', 'brand_personality', etc.
ADD COLUMN quality_score INTEGER DEFAULT 7, -- 1-10 quality rating
ADD COLUMN is_complete BOOLEAN DEFAULT true;

-- Update existing records with section mapping
UPDATE user_data_points SET 
  section_name = CASE data_point_key
    WHEN 'broad_domain_expertise' THEN 'core_expertise'
    WHEN 'specific_niche_focus' THEN 'core_expertise'  
    WHEN 'ideal_client_definition' THEN 'core_expertise'
    WHEN 'target_customer_problems' THEN 'core_expertise'
    WHEN 'signature_outcomes' THEN 'core_expertise'
    WHEN 'unique_method_approach' THEN 'positioning_method'
    WHEN 'industry_contrarian_belief' THEN 'positioning_method'
    WHEN 'value_misunderstanding' THEN 'positioning_method'
    WHEN 'buyer_trigger_moment' THEN 'positioning_method'
    ELSE 'unknown'
  END
WHERE section_name IS NULL;
```

## Updated Database Structure

### conversations table
- conversation_id (existing)
- transcript (existing)
- user_id (existing)
- user_name (existing)
- extracted_data (existing)
- **agent_id** (NEW)
- **track_type** (NEW)
- created_at (existing)

### user_data_points table  
- user_id (existing)
- data_point_key (existing)
- value (existing)
- rationale (existing)
- answered_at (existing)
- **agent_id** (NEW)
- **track_type** (NEW)  
- **section_name** (NEW)
- **quality_score** (NEW)
- **is_complete** (NEW)

### user_agent_progress table (NEW)
- user_id
- track_type ('founder' or 'executive')
- agent_id ('value_architect', 'positioning_strategist', 'growth_architect')
- status ('not_started', 'in_progress', 'completed')
- started_at, completed_at
- last_conversation_id

## Benefits of This Schema

1. **Multi-Agent Support**: Can track which agent collected which data
2. **Track Management**: Supports both founder and executive tracks
3. **Progress Tracking**: Know exactly where user is in the journey
4. **Quality Monitoring**: Track completion quality per data point
5. **Resume Capability**: Users can continue where they left off
6. **Analytics Ready**: Can analyze completion rates, drop-offs, quality scores

## Next Steps After Schema Update

1. Update webhook to capture agent_id and track_type
2. Update getUserContext to handle multi-agent scenarios
3. Update frontend to show progress and route to correct agent
4. Test with existing Value Architect agent
5. Deploy new agents and test full flow

Run these SQL commands in your Supabase dashboard before deploying the updated backend.
