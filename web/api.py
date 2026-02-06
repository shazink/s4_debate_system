"""
Flask API for S4 Multi-Agent Debate System.
Exposes debate functionality as REST endpoints for the web UI.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from agents.coordinator import Coordinator
import traceback
import json

app = Flask(__name__, static_folder='.')
CORS(app)

# Initialize coordinator with silent mode (no terminal spam)
import sys
import io

# Redirect stdout to suppress print statements
class SilentMode:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = io.StringIO()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self._original_stdout

coordinator = Coordinator(save_logs=False)


@app.route('/')
def index():
    """Serve the live streaming page."""
    return send_from_directory('.', 'index_live.html')


@app.route('/style.css')
def styles():
    """Serve CSS."""
    return send_from_directory('.', 'style.css')


@app.route('/script_stream.js')
def scripts_stream():
    """Serve streaming JavaScript."""
    return send_from_directory('.', 'script_stream.js')


@app.route('/script.js')
def scripts():
    """Serve JavaScript."""
    return send_from_directory('.', 'script.js')


@app.route('/api/status', methods=['GET'])
def status():
    """Health check endpoint."""
    return jsonify({
        'status': 'online',
        'agents': [
            {'name': 'Utility Agent', 'threshold': '60%'},
            {'name': 'Accuracy Agent', 'threshold': '85%'},
            {'name': 'Safety Agent', 'veto_power': True}
        ]
    })


@app.route('/api/debate/stream', methods=['POST'])
def debate_stream():
    """Stream debate events in real-time as they happen."""
    data = request.get_json()
    query = data.get('query', '').strip()
    
    if not query:
        return jsonify({'success': False, 'error': 'Query cannot be empty'}), 400
    
    def generate():
        """Generator that yields Server-Sent Events."""
        try:
            # Send start event
            yield f"data: {json.dumps({'type': 'start', 'query': query})}\n\n"
            
            # Get agents
            agents = [coordinator.utility_agent, coordinator.accuracy_agent, coordinator.safety_agent]
            agent_names = [a.name for a in agents]
            
            # Round 1: Initial Analysis
            yield f"data: {json.dumps({'type': 'round_start', 'round': 1, 'name': 'Initial Analysis'})}\n\n"
            
            initial_decisions = {}
            for agent in agents:
                yield f"data: {json.dumps({'type': 'agent_thinking', 'agent': agent.name})}\n\n"
                decision = agent.analyze(query)
                initial_decisions[agent.name] = decision
                
                event_data = {
                    'type': 'agent_response',
                    'round': 1,
                    'agent': agent.name,
                    'decision': decision.decision,
                    'confidence': decision.confidence,
                    'risk': decision.risk,
                    'reasoning': decision.reasoning
                }
                yield f"data: {json.dumps(event_data)}\n\n"
            
            # Round 2: Challenges
            yield f"data: {json.dumps({'type': 'round_start', 'round': 2, 'name': 'Challenge Round'})}\n\n"
            
            challenges_dict = {agent.name: [] for agent in agents}
            for challenger in agents:
                for challenged in agents:
                    if challenger.name != challenged.name:
                        yield f"data: {json.dumps({'type': 'agent_thinking', 'agent': challenger.name})}\n\n"
                        
                        challenged_reasoning = initial_decisions[challenged.name].reasoning
                        challenge = challenger.challenge(query, challenged_reasoning)
                        challenges_dict[challenged.name].append(f"[{challenger.name}]: {challenge}")
                        
                        event_data = {
                            'type': 'challenge',
                            'round': 2,
                            'challenger': challenger.name,
                            'challenged': challenged.name,
                            'challenge': challenge
                        }
                        yield f"data: {json.dumps(event_data)}\n\n"
            
            # Round 3: Revisions
            yield f"data: {json.dumps({'type': 'round_start', 'round': 3, 'name': 'Revision'})}\n\n"
            
            revised_decisions = {}
            for agent in agents:
                yield f"data: {json.dumps({'type': 'agent_thinking', 'agent': agent.name})}\n\n"
                
                agent_challenges = "\n".join(challenges_dict[agent.name])
                original = agent.last_decision
                revised = agent.revise(query, original, agent_challenges)
                revised_decisions[agent.name] = revised
                
                event_data = {
                    'type': 'revision',
                    'round': 3,
                    'agent': agent.name,
                    'old_decision': original.decision,
                    'new_decision': revised.decision,
                    'old_confidence': original.confidence,
                    'new_confidence': revised.confidence,
                    'reasoning': revised.reasoning
                }
                yield f"data: {json.dumps(event_data)}\n\n"
            
            # Round 4: Final votes
            yield f"data: {json.dumps({'type': 'round_start', 'round': 4, 'name': 'Final Voting'})}\n\n"
            
            final_votes = []
            for agent in agents:
                decision = revised_decisions[agent.name]
                final_votes.append(decision)
                
                event_data = {
                    'type': 'final_vote',
                    'round': 4,
                    'agent': agent.name,
                    'decision': decision.decision,
                    'confidence': decision.confidence,
                    'risk': decision.risk,
                    'reasoning': decision.reasoning
                }
                yield f"data: {json.dumps(event_data)}\n\n"
            
            # Apply decision rules
            from debate.decision_rules import DecisionRules
            final_decision = DecisionRules.apply(final_votes, agent_names)
            
            event_data = {
                'type': 'final_decision',
                'decision': final_decision.decision,
                'reasoning': final_decision.reasoning,
                'metadata': final_decision.metadata
            }
            yield f"data: {json.dumps(event_data)}\n\n"
            
            yield f"data: {json.dumps({'type': 'complete'})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')


if __name__ == '__main__':
    print("="*80)
    print(" S4 MULTI-AGENT DEBATE SYSTEM - LIVE STREAMING")
    print("="*80)
    print("\n🌐 Starting server...")
    print("📍 URL: http://localhost:5000")
    print("🛡️  Attack Defense: ACTIVE")
    print("🤖 Agents: 3 (Utility, Accuracy, Safety)")
    print("🎬 Live Streaming: ENABLED")
    print("\n" + "="*80)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
