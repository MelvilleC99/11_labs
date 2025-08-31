# Enhanced getUserContext for Multi-Agent Support

@app.route('/tools/getUserContext', methods=['POST'])
def get_user_context():
    """Enhanced tool endpoint for multi-agent context retrieval"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'test_user_123')
        
        print(f"🔍 Multi-agent context lookup for user: {user_id}")
        
        # ========================================
        # Get user's data points and progress
        # ========================================
        
        # Get all user data points with agent information
        result = supabase.table('user_data_points')\
            .select('data_point_key, value, agent_id, track_type')\
            .eq('user_id', user_id)\
            .execute()
        
        # Get user's current progress
        progress_result = supabase.table('user_progress')\
            .select('track_type, current_agent, last_active')\
            .eq('user_id', user_id)\
            .execute()
        
        # ========================================
        # Process results
        # ========================================
        
        if not result.data:
            return jsonify({
                "status": "new_user",
                "message": "Hi! I'm here to help you build your business foundation. Let's start - what's a broad domain where you have deep expertise?",
                "context_summary": "No previous sessions found",
                "user_progress": "Starting fresh"
            })
        
        # Organize data by agent
        user_data = {}
        agents_completed = set()
        
        for item in result.data:
            user_data[item['data_point_key']] = item['value']
            if item.get('agent_id'):
                agents_completed.add(item['agent_id'])
        
        # Get current progress info
        current_agent = 'value_architect'  # default
        track_type = 'founder'  # default
        
        if progress_result.data:
            progress = progress_result.data[0]
            current_agent = progress.get('current_agent', 'value_architect')
            track_type = progress.get('track_type', 'founder')
        
        print(f"📊 User has data from agents: {list(agents_completed)}")
        print(f"🎯 Current/last agent: {current_agent}")
        print(f"📋 Track: {track_type}")
        
        # ========================================
        # Build context message based on completed agents
        # ========================================
        
        # Define agent progression and their key fields
        agent_fields = {
            'value_architect': ['broad_domain_expertise', 'specific_niche_focus', 'ideal_client_definition', 
                               'target_customer_problems', 'signature_outcomes'],
            'positioning_strategist': ['value_explanation', 'unique_method', 'contrarian_belief', 
                                     'voice_vibe', 'content_approach'],
            'growth_architect': ['content_business_purpose', 'audience_struggles', 'future_vision', 
                                'success_signals']
        }
        
        # Check completion status for each agent
        completion_status = {}
        for agent, fields in agent_fields.items():
            completed_count = sum(1 for field in fields if field in user_data and user_data[field])
            completion_status[agent] = {
                'completed': completed_count,
                'total': len(fields),
                'percentage': round((completed_count / len(fields)) * 100) if fields else 0
            }
        
        # ========================================
        # Generate appropriate context message
        # ========================================
        
        # Build foundation summary for later agents
        foundation_summary = ""
        if completion_status['value_architect']['completed'] > 0:
            foundation_parts = []
            if 'broad_domain_expertise' in user_data:
                foundation_parts.append(f"expertise in {user_data['broad_domain_expertise']}")
            if 'ideal_client_definition' in user_data:
                foundation_parts.append(f"serving {user_data['ideal_client_definition']}")
            if 'target_customer_problems' in user_data:
                foundation_parts.append(f"solving {user_data['target_customer_problems'][:60]}...")
            
            foundation_summary = ", ".join(foundation_parts)
        
        # Build positioning summary for growth agent
        positioning_summary = ""
        if completion_status['positioning_strategist']['completed'] > 0:
            positioning_parts = []
            if 'unique_method' in user_data:
                positioning_parts.append(f"unique approach: {user_data['unique_method'][:50]}...")
            if 'voice_vibe' in user_data:
                positioning_parts.append(f"voice: {user_data['voice_vibe'][:40]}...")
            
            positioning_summary = ", ".join(positioning_parts)
        
        # Generate context message based on what's been completed
        total_completed = sum(status['completed'] for status in completion_status.values())
        
        if total_completed == 0:
            context_message = "Let's build your business foundation from the ground up. What's a broad domain where you have deep expertise?"
        
        elif completion_status['value_architect']['completed'] > 0 and completion_status['positioning_strategist']['completed'] == 0:
            # Value Architect complete, moving to Positioning
            context_message = f"Great foundation! I can see your {foundation_summary}. Now let's explore how you position yourself differently in the market."
        
        elif completion_status['positioning_strategist']['completed'] > 0 and completion_status['growth_architect']['completed'] == 0:
            # Both foundation and positioning done, moving to growth
            context_message = f"Excellent! With your foundation ({foundation_summary}) and positioning ({positioning_summary}) clear, let's architect your growth strategy."
        
        else:
            # Partial completion - continue where left off
            incomplete_agents = [agent for agent, status in completion_status.items() if status['completed'] < status['total']]
            if incomplete_agents:
                agent_name = incomplete_agents[0].replace('_', ' ').title()
                context_message = f"Welcome back! Let's continue building your {agent_name} profile. I have some of your information - let's fill in the gaps."
            else:
                context_message = "Welcome back! You've completed all sections. Let me provide a comprehensive summary of everything we've built together."
        
        # ========================================
        # Return enhanced context response
        # ========================================
        
        return jsonify({
            "status": "returning_user",
            "message": context_message,
            "context_summary": f"Total progress: {total_completed} elements completed across {len(agents_completed)} agents",
            "user_progress": {
                "current_agent": current_agent,
                "track_type": track_type,
                "agents_completed": list(agents_completed),
                "completion_status": completion_status,
                "total_elements": total_completed
            },
            "foundation_summary": foundation_summary,
            "positioning_summary": positioning_summary
        })
        
    except Exception as e:
        print(f"❌ Error in enhanced getUserContext: {str(e)}")
        return jsonify({
            "status": "error", 
            "message": "Let's build your business foundation! What's a broad domain where you have deep expertise?",
            "context_summary": f"Error retrieving context: {str(e)}"
        }), 200  # Return 200 so agent continues
