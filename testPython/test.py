from flask import Flask, render_template_string, request, jsonify
import json
import os

app = Flask(__name__)

# File to store data
DATA_FILE = 'scoreboard_data.json'

# Initialize or load data
def load_data():
    default_data = {
        'current_match': {'team1': '', 'team2': '', 'score1': 0, 'score2': 0, 'team1_streak': 0, 'team2_streak': 0},
        'queue': [],
        'all_teams': [],
        'stats': {}
    }
    
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            loaded_data = json.load(f)
        
        # Merge with defaults to ensure all keys exist
        for key in default_data:
            if key not in loaded_data:
                loaded_data[key] = default_data[key]
        
        # Ensure current_match has all fields
        if 'team1_streak' not in loaded_data['current_match']:
            loaded_data['current_match']['team1_streak'] = 0
        if 'team2_streak' not in loaded_data['current_match']:
            loaded_data['current_match']['team2_streak'] = 0
        
        return loaded_data
    
    return default_data

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

data = load_data()

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scoreboard & Queue</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        h1, h2 {
            color: #333;
            margin-bottom: 20px;
        }
        .scoreboard {
            display: grid;
            grid-template-columns: 1fr auto 1fr;
            gap: 20px;
            align-items: center;
            margin-bottom: 30px;
        }
        .team {
            text-align: center;
        }
        .team-name {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
            color: #667eea;
            word-wrap: break-word;
        }
        .streak {
            font-size: 14px;
            color: #f59e0b;
            margin-bottom: 10px;
            font-weight: bold;
        }
        .score {
            font-size: 48px;
            font-weight: bold;
            color: #333;
            margin-bottom: 15px;
        }
        .btn-group {
            display: flex;
            gap: 10px;
            justify-content: center;
        }
        button {
            padding: 12px 24px;
            font-size: 16px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
        }
        .btn-plus {
            background: #4ade80;
            color: white;
        }
        .btn-minus {
            background: #f87171;
            color: white;
        }
        .btn-primary {
            background: #667eea;
            color: white;
        }
        .btn-danger {
            background: #ef4444;
            color: white;
        }
        .btn-secondary {
            background: #64748b;
            color: white;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        button:active {
            transform: translateY(0);
        }
        .vs {
            font-size: 32px;
            font-weight: bold;
            color: #764ba2;
        }
        input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 16px;
            margin-bottom: 10px;
        }
        input:focus {
            outline: none;
            border-color: #667eea;
        }
        .queue-item {
            background: #f8fafc;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .queue-teams {
            font-weight: bold;
            color: #333;
        }
        .team-chip {
            background: #e0e7ff;
            color: #4338ca;
            padding: 8px 16px;
            border-radius: 20px;
            margin: 5px;
            display: inline-flex;
            align-items: center;
            gap: 10px;
            font-weight: bold;
        }
        .team-chip button {
            background: #ef4444;
            color: white;
            border: none;
            border-radius: 50%;
            width: 24px;
            height: 24px;
            cursor: pointer;
            padding: 0;
            font-size: 12px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 15px;
        }
        .stat-item {
            background: #f8fafc;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-name {
            font-weight: bold;
            color: #333;
            margin-bottom: 8px;
        }
        .stat-record {
            color: #667eea;
            font-size: 18px;
        }
        .controls {
            display: flex;
            gap: 10px;
            margin-top: 20px;
            flex-wrap: wrap;
        }
        .info-box {
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 8px;
        }
        .info-box h3 {
            color: #92400e;
            margin-bottom: 8px;
            font-size: 16px;
        }
        .info-box p {
            color: #78350f;
            font-size: 14px;
            line-height: 1.5;
        }
        .teams-container {
            display: flex;
            flex-wrap: wrap;
            margin-top: 15px;
        }
        @media (max-width: 600px) {
            .scoreboard {
                grid-template-columns: 1fr;
                gap: 30px;
            }
            .vs {
                font-size: 24px;
            }
            .score {
                font-size: 36px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>🏆 Scoreboard</h1>
            <div class="scoreboard">
                <div class="team">
                    <div class="team-name" id="team1Name">Team 1</div>
                    <div class="streak" id="team1Streak"></div>
                    <div class="score" id="score1">0</div>
                    <div class="btn-group">
                        <button class="btn-plus" onclick="updateScore(1, 1)">+1</button>
                        <button class="btn-minus" onclick="updateScore(1, -1)">-1</button>
                    </div>
                </div>
                <div class="vs">VS</div>
                <div class="team">
                    <div class="team-name" id="team2Name">Team 2</div>
                    <div class="streak" id="team2Streak"></div>
                    <div class="score" id="score2">0</div>
                    <div class="btn-group">
                        <button class="btn-plus" onclick="updateScore(2, 1)">+1</button>
                        <button class="btn-minus" onclick="updateScore(2, -1)">-1</button>
                    </div>
                </div>
            </div>
            <div class="controls">
                <button class="btn-primary" onclick="finishMatch()">Finish Match</button>
                <button class="btn-secondary" onclick="resetScore()">Reset Score</button>
            </div>
        </div>

        <div class="card">
            <h2>👥 Teams Management</h2>
            <div class="info-box">
                <h3>📋 How it works:</h3>
                <p>• Add teams one at a time to the pool<br>
                • Winner stays, loser goes to back of queue<br>
                • With 3 teams: Winner stays indefinitely<br>
                • With 4+ teams: Winner goes to queue after 2 consecutive wins<br>
                • Next team in queue replaces the loser</p>
            </div>
            <input type="text" id="newTeam" placeholder="Enter team name">
            <button class="btn-primary" onclick="addTeam()" style="width: 100%; margin-bottom: 20px;">Add Team</button>
            
            <h3 style="margin-top: 20px; margin-bottom: 10px;">All Teams (<span id="teamCount">0</span>)</h3>
            <div class="teams-container" id="teamsList"></div>
        </div>

        <div class="card">
            <h2>🎯 Current Queue</h2>
            <p style="color: #64748b; margin-bottom: 15px;">Next team to play: <strong id="nextTeam">-</strong></p>
            <div id="queueList"></div>
        </div>

        <div class="card">
            <h2>📊 Team Statistics</h2>
            <div class="stats-grid" id="statsList"></div>
            <button class="btn-danger" onclick="clearStats()" style="width: 100%; margin-top: 20px;">Clear All Stats</button>
        </div>
    </div>

    <script>
        function loadData() {
            fetch('/get_data')
                .then(r => r.json())
                .then(data => {
                    // Update scoreboard
                    document.getElementById('team1Name').textContent = data.current_match.team1 || 'Team 1';
                    document.getElementById('team2Name').textContent = data.current_match.team2 || 'Team 2';
                    document.getElementById('score1').textContent = data.current_match.score1;
                    document.getElementById('score2').textContent = data.current_match.score2;
                    
                    // Update streaks
                    const streak1 = data.current_match.team1_streak;
                    const streak2 = data.current_match.team2_streak;
                    document.getElementById('team1Streak').textContent = streak1 > 0 ? `🔥 ${streak1} win streak` : '';
                    document.getElementById('team2Streak').textContent = streak2 > 0 ? `🔥 ${streak2} win streak` : '';

                    // Update all teams
                    const teamsList = document.getElementById('teamsList');
                    teamsList.innerHTML = '';
                    document.getElementById('teamCount').textContent = data.all_teams.length;
                    data.all_teams.forEach(team => {
                        const chip = document.createElement('div');
                        chip.className = 'team-chip';
                        chip.innerHTML = `
                            ${team}
                            <button onclick="removeTeam('${team.replace(/'/g, "\\'")}')">×</button>
                        `;
                        teamsList.appendChild(chip);
                    });

                    // Update queue display
                    const queueList = document.getElementById('queueList');
                    queueList.innerHTML = '';
                    if (data.queue.length === 0) {
                        queueList.innerHTML = '<p style="color: #64748b;">Queue is empty</p>';
                        document.getElementById('nextTeam').textContent = '-';
                    } else {
                        document.getElementById('nextTeam').textContent = data.queue[0];
                        data.queue.forEach((team, idx) => {
                            const div = document.createElement('div');
                            div.className = 'queue-item';
                            div.innerHTML = `
                                <span class="queue-teams">#${idx + 1}: ${team}</span>
                            `;
                            queueList.appendChild(div);
                        });
                    }

                    // Update stats
                    const statsList = document.getElementById('statsList');
                    statsList.innerHTML = '';
                    Object.entries(data.stats).forEach(([team, record]) => {
                        const div = document.createElement('div');
                        div.className = 'stat-item';
                        div.innerHTML = `
                            <div class="stat-name">${team}</div>
                            <div class="stat-record">${record.wins}W - ${record.losses}L</div>
                        `;
                        statsList.appendChild(div);
                    });
                });
        }

        function updateScore(team, delta) {
            fetch('/update_score', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({team, delta})
            }).then(() => loadData());
        }

        function resetScore() {
            if (confirm('Reset current scores to 0?')) {
                fetch('/reset_score', {method: 'POST'})
                    .then(() => loadData());
            }
        }

        function finishMatch() {
            fetch('/finish_match', {method: 'POST'})
                .then(r => r.json())
                .then(result => {
                    if (result.error) {
                        alert(result.error);
                    } else if (result.message) {
                        alert(result.message);
                    }
                    loadData();
                });
        }

        function addTeam() {
            const team = document.getElementById('newTeam').value.trim();
            if (!team) {
                alert('Please enter a team name');
                return;
            }
            fetch('/add_team', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({team})
            }).then(r => r.json())
            .then(result => {
                if (result.error) {
                    alert(result.error);
                } else {
                    document.getElementById('newTeam').value = '';
                }
                loadData();
            });
        }

        function removeTeam(team) {
            if (confirm(`Remove ${team} from the system?`)) {
                fetch('/remove_team', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({team})
                }).then(() => loadData());
            }
        }

        function clearStats() {
            if (confirm('Clear all team statistics? This cannot be undone.')) {
                fetch('/clear_stats', {method: 'POST'})
                    .then(() => loadData());
            }
        }

        // Load data on page load
        loadData();
        // Refresh data every 2 seconds
        setInterval(loadData, 2000);
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/get_data')
def get_data():
    return jsonify(data)

@app.route('/update_score', methods=['POST'])
def update_score():
    req = request.json
    team = req['team']
    delta = req['delta']
    
    if team == 1:
        data['current_match']['score1'] = max(0, data['current_match']['score1'] + delta)
    else:
        data['current_match']['score2'] = max(0, data['current_match']['score2'] + delta)
    
    save_data(data)
    return jsonify({'success': True})

@app.route('/reset_score', methods=['POST'])
def reset_score():
    data['current_match']['score1'] = 0
    data['current_match']['score2'] = 0
    save_data(data)
    return jsonify({'success': True})

@app.route('/finish_match', methods=['POST'])
def finish_match():
    team1 = data['current_match']['team1']
    team2 = data['current_match']['team2']
    score1 = data['current_match']['score1']
    score2 = data['current_match']['score2']
    
    if not team1 or not team2:
        return jsonify({'error': 'Need at least 2 teams playing to finish a match'})
    
    if score1 == score2:
        return jsonify({'error': 'Cannot finish match with a tie. Please adjust scores.'})
    
    # Initialize stats if needed
    if team1 not in data['stats']:
        data['stats'][team1] = {'wins': 0, 'losses': 0}
    if team2 not in data['stats']:
        data['stats'][team2] = {'wins': 0, 'losses': 0}
    
    # Determine winner and loser
    if score1 > score2:
        winner = team1
        loser = team2
        winner_streak = data['current_match']['team1_streak'] + 1
        loser_pos = 1  # team2 position
    else:
        winner = team2
        loser = team1
        winner_streak = data['current_match']['team2_streak'] + 1
        loser_pos = 0  # team1 position
    
    # Update stats
    data['stats'][winner]['wins'] += 1
    data['stats'][loser]['losses'] += 1
    
    # Add loser to back of queue
    if loser in data['queue']:
        data['queue'].remove(loser)
    data['queue'].append(loser)
    
    total_teams = len(data['all_teams'])
    message = f"{winner} wins! "
    
    # Check if winner should go to queue
    if total_teams > 3 and winner_streak >= 2:
        # Winner has won 2 games, send to queue
        if winner in data['queue']:
            data['queue'].remove(winner)
        data['queue'].append(winner)
        message += f"{winner} has won 2 games in a row and goes to the queue. "
        
        # Get next 2 teams from queue
        if len(data['queue']) >= 2:
            next_team1 = data['queue'].pop(0)
            next_team2 = data['queue'].pop(0)
            data['current_match'] = {
                'team1': next_team1,
                'team2': next_team2,
                'score1': 0,
                'score2': 0,
                'team1_streak': 0,
                'team2_streak': 0
            }
            message += f"Next match: {next_team1} vs {next_team2}"
        else:
            data['current_match'] = {'team1': '', 'team2': '', 'score1': 0, 'score2': 0, 'team1_streak': 0, 'team2_streak': 0}
            message += "Not enough teams in queue for next match."
    else:
        # Winner stays, loser replaced
        message += f"{winner} stays on (streak: {winner_streak}). "
        
        # Get next team from queue to replace loser
        if data['queue'] and data['queue'][0] != winner:
            next_team = data['queue'].pop(0)
            
            # Update current match - winner stays in same position
            if loser_pos == 0:  # loser was team1
                data['current_match'] = {
                    'team1': next_team,
                    'team2': winner,
                    'score1': 0,
                    'score2': 0,
                    'team1_streak': 0,
                    'team2_streak': winner_streak
                }
            else:  # loser was team2
                data['current_match'] = {
                    'team1': winner,
                    'team2': next_team,
                    'score1': 0,
                    'score2': 0,
                    'team1_streak': winner_streak,
                    'team2_streak': 0
                }
            message += f"{next_team} comes in to challenge!"
        else:
            data['current_match'] = {'team1': '', 'team2': '', 'score1': 0, 'score2': 0, 'team1_streak': 0, 'team2_streak': 0}
            message += "No teams in queue to replace loser."
    
    save_data(data)
    return jsonify({'success': True, 'message': message})

@app.route('/add_team', methods=['POST'])
def add_team():
    team = request.json['team']
    
    if team in data['all_teams']:
        return jsonify({'error': 'Team already exists'})
    
    data['all_teams'].append(team)
    
    # Initialize stats
    if team not in data['stats']:
        data['stats'][team] = {'wins': 0, 'losses': 0}
    
    # Auto-setup initial match
    if not data['current_match']['team1']:
        data['current_match']['team1'] = team
        data['current_match']['team1_streak'] = 0
    elif not data['current_match']['team2']:
        data['current_match']['team2'] = team
        data['current_match']['team2_streak'] = 0
    else:
        # Add to queue
        data['queue'].append(team)
    
    save_data(data)
    return jsonify({'success': True})

@app.route('/remove_team', methods=['POST'])
def remove_team():
    team = request.json['team']
    
    # Remove from all_teams
    if team in data['all_teams']:
        data['all_teams'].remove(team)
    
    # Remove from queue
    if team in data['queue']:
        data['queue'].remove(team)
    
    # Remove from current match if present
    if data['current_match']['team1'] == team:
        data['current_match']['team1'] = ''
        data['current_match']['team1_streak'] = 0
        data['current_match']['score1'] = 0
    if data['current_match']['team2'] == team:
        data['current_match']['team2'] = ''
        data['current_match']['team2_streak'] = 0
        data['current_match']['score2'] = 0
    
    save_data(data)
    return jsonify({'success': True})

@app.route('/clear_stats', methods=['POST'])
def clear_stats():
    data['stats'] = {}
    data['current_match'] = {'team1': '', 'team2': '', 'score1': 0, 'score2': 0, 'team1_streak': 0, 'team2_streak': 0}
    data['queue'] = []
    data['all_teams'] = []
    save_data(data)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)