import random
import webbrowser
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import urllib.parse
import os

class GameLogic:
    """Your original game logic encapsulated"""
    def __init__(self):
        self.youDict = {"s": 1, "w": -1, "g": 0}
        self.reverseDict = {1: "Snake", -1: "Water", 0: "Gun"}
    
    def play_round(self, youstr):
        # Random computer choice
        computer = random.choice([-1, 0, 1])
        
        # Map computer numeric value back to string key ('s', 'w', 'g')
        computer_str = next((k for k, v in self.youDict.items() if v == computer), None)
        
        # Show computer's choice in readable format
        computer_choice_name = self.reverseDict[computer]
        
        # Validate user input
        if youstr not in self.youDict:
            return {"error": "Invalid input!"}
        
        you = self.youDict[youstr]
        
        if computer == you:
            result = "Draw!"
            winner = "draw"
        else:
            if computer == -1 and you == 1:
                result = "You win!"
                winner = "player"
            elif computer == -1 and you == 0:
                result = "You Lose!"
                winner = "computer"
            elif computer == 0 and you == 1:
                result = "You win!"
                winner = "player"
            elif computer == 0 and you == -1:
                result = "You Lose!"
                winner = "computer"
            elif computer == 1 and you == 0:
                result = "You win!"
                winner = "player"
            elif computer == 1 and you == -1:
                result = "You Lose!"
                winner = "computer"
            else:
                result = "Something went wrong"
                winner = "error"
        
        return {
            "computer_choice": computer_str,
            "computer_choice_name": computer_choice_name,
            "result": result,
            "winner": winner
        }

class GameHandler(SimpleHTTPRequestHandler):
    game = GameLogic()
    
    def do_GET(self):
        if self.path == "/" or self.path == "/game.html":
            self.serve_game_page()
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == "/play":
            self.handle_play_request()
        else:
            self.send_error(404)
    
    def serve_game_page(self):
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Snake Water Gun - Python Backend</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow-x: hidden;
        }

        .game-container {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            text-align: center;
            max-width: 600px;
            width: 90%;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        h1 {
            color: white;
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            animation: glow 2s ease-in-out infinite alternate;
        }

        .backend-info {
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.9rem;
            margin-bottom: 30px;
            padding: 10px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
        }

        @keyframes glow {
            from { text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3), 0 0 10px rgba(255, 255, 255, 0.2); }
            to { text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3), 0 0 20px rgba(255, 255, 255, 0.4); }
        }

        .choices-container {
            display: flex;
            justify-content: space-around;
            margin: 40px 0;
            gap: 20px;
            flex-wrap: wrap;
        }

        .choice-btn {
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            border: none;
            border-radius: 15px;
            padding: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 3rem;
            min-width: 120px;
            min-height: 120px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
            position: relative;
            overflow: hidden;
        }

        .choice-btn:hover {
            transform: translateY(-5px) scale(1.05);
            box-shadow: 0 15px 25px rgba(0, 0, 0, 0.3);
        }

        .choice-btn:active {
            transform: translateY(-2px) scale(1.02);
        }

        .choice-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .choice-btn.snake {
            background: linear-gradient(45deg, #2ecc71, #27ae60);
        }

        .choice-btn.water {
            background: linear-gradient(45deg, #3498db, #2980b9);
        }

        .choice-btn.gun {
            background: linear-gradient(45deg, #e74c3c, #c0392b);
        }

        .loading {
            color: white;
            font-size: 1.2rem;
            margin: 20px 0;
            animation: pulse 1s ease-in-out infinite;
        }

        .battle-arena {
            display: none;
            margin: 30px 0;
            padding: 30px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .vs-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 20px 0;
        }

        .player-choice, .computer-choice {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            font-size: 4rem;
            min-width: 150px;
            min-height: 150px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }

        .vs-text {
            color: white;
            font-size: 2rem;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
            animation: pulse 1s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }

        .battle-animation {
            animation: shake 0.5s ease-in-out;
        }

        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-10px); }
            75% { transform: translateX(10px); }
        }

        .result {
            color: white;
            font-size: 1.8rem;
            margin: 20px 0;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
            opacity: 0;
            animation: fadeIn 0.5s ease-in-out forwards;
        }

        @keyframes fadeIn {
            to { opacity: 1; }
        }

        .result.win {
            color: #2ecc71;
            animation: bounce 0.6s ease-in-out;
        }

        .result.lose {
            color: #e74c3c;
            animation: bounce 0.6s ease-in-out;
        }

        .result.draw {
            color: #f39c12;
            animation: bounce 0.6s ease-in-out;
        }

        @keyframes bounce {
            0%, 20%, 60%, 100% { transform: translateY(0); }
            40% { transform: translateY(-20px); }
            80% { transform: translateY(-10px); }
        }

        .score-board {
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
            background: rgba(255, 255, 255, 0.05);
            padding: 15px;
            border-radius: 10px;
        }

        .score {
            color: white;
            font-size: 1.2rem;
            font-weight: bold;
        }

        .play-again-btn {
            background: linear-gradient(45deg, #8e44ad, #9b59b6);
            color: white;
            border: none;
            border-radius: 25px;
            padding: 12px 30px;
            font-size: 1.1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 20px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }

        .play-again-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        }

        .emoji-rain {
            position: fixed;
            top: -50px;
            font-size: 2rem;
            animation: fall 3s linear;
            z-index: 1000;
            pointer-events: none;
        }

        @keyframes fall {
            to {
                transform: translateY(100vh) rotate(360deg);
            }
        }

        @media (max-width: 768px) {
            .choices-container {
                flex-direction: column;
                align-items: center;
            }
            
            .vs-container {
                flex-direction: column;
                gap: 20px;
            }
            
            .vs-text {
                order: 2;
            }
        }
    </style>
</head>
<body>
    <div class="game-container">
        <h1>🐍 Snake Water Gun 🔫</h1>
        <div class="backend-info">
            🔧 Powered by Python http.server Backend
        </div>
        
        <div class="score-board">
            <div class="score">You: <span id="player-score">0</span></div>
            <div class="score">Computer: <span id="computer-score">0</span></div>
        </div>

        <div class="choices-container">
            <button class="choice-btn snake" onclick="playGame('s')" title="Snake">🐍</button>
            <button class="choice-btn water" onclick="playGame('w')" title="Water">💧</button>
            <button class="choice-btn gun" onclick="playGame('g')" title="Gun">🔫</button>
        </div>

        <div id="loading" class="loading" style="display: none;">
            Processing your move...
        </div>

        <div class="battle-arena" id="battle-arena">
            <div class="vs-container">
                <div class="player-choice" id="player-choice"></div>
                <div class="vs-text">VS</div>
                <div class="computer-choice" id="computer-choice"></div>
            </div>
            <div class="result" id="result"></div>
            <button class="play-again-btn" onclick="resetGame()">Play Again</button>
        </div>
    </div>

    <script>
        // Game state
        let playerScore = 0;
        let computerScore = 0;

        // Emoji and name mapping
        const emojiDict = {"s": "🐍", "w": "💧", "g": "🔫"};
        const nameDict = {"s": "Snake", "w": "Water", "g": "Gun"};
        // Use the same mapping for computer choice
        const emojiReverseDict = {"s": "🐍", "w": "💧", "g": "🔫"};

        async function playGame(youstr) {
            // Disable buttons during processing
            const buttons = document.querySelectorAll('.choice-btn');
            buttons.forEach(btn => btn.disabled = true);
            
            // Show loading
            document.getElementById('loading').style.display = 'block';
            document.getElementById('battle-arena').style.display = 'none';

            try {
                // Send request to Python backend
                const response = await fetch('/play', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ choice: youstr })
                });

                const data = await response.json();
                
                if (data.error) {
                    alert(data.error);
                    return;
                }

                // Hide loading
                document.getElementById('loading').style.display = 'none';
                
                // Show battle arena
                document.getElementById('battle-arena').style.display = 'block';
                
                // Show choices with animation
                const playerChoiceEl = document.getElementById('player-choice');
                const computerChoiceEl = document.getElementById('computer-choice');
                
                playerChoiceEl.innerHTML = `${emojiDict[youstr]}<br><small>You (${nameDict[youstr]})</small>`;
                computerChoiceEl.innerHTML = `${emojiReverseDict[data.computer_choice]}<br><small>Computer (${data.computer_choice_name})</small>`;
                
                // Add battle animation
                playerChoiceEl.classList.add('battle-animation');
                computerChoiceEl.classList.add('battle-animation');
                
                // Remove animation after it completes
                setTimeout(() => {
                    playerChoiceEl.classList.remove('battle-animation');
                    computerChoiceEl.classList.remove('battle-animation');
                }, 500);

                // Show result
                const resultEl = document.getElementById('result');
                setTimeout(() => {
                    resultEl.textContent = data.result;
                    
                    if (data.winner === 'player') {
                        resultEl.className = "result win";
                        playerScore++;
                        createEmojiRain("🎉");
                    } else if (data.winner === 'computer') {
                        resultEl.className = "result lose";
                        computerScore++;
                    } else {
                        resultEl.className = "result draw";
                    }
                    
                    updateScore();
                }, 300);

            } catch (error) {
                console.error('Error:', error);
                alert('Error connecting to server!');
                document.getElementById('loading').style.display = 'none';
            } finally {
                // Re-enable buttons
                buttons.forEach(btn => btn.disabled = false);
            }
        }

        function updateScore() {
            document.getElementById('player-score').textContent = playerScore;
            document.getElementById('computer-score').textContent = computerScore;
        }

        function resetGame() {
            document.getElementById('battle-arena').style.display = 'none';
            document.getElementById('result').className = 'result';
        }

        function createEmojiRain(emoji) {
            for (let i = 0; i < 15; i++) {
                setTimeout(() => {
                    const emojiEl = document.createElement('div');
                    emojiEl.className = 'emoji-rain';
                    emojiEl.textContent = emoji;
                    emojiEl.style.left = Math.random() * 100 + 'vw';
                    emojiEl.style.animationDelay = Math.random() * 2 + 's';
                    document.body.appendChild(emojiEl);
                    
                    setTimeout(() => {
                        emojiEl.remove();
                    }, 3000);
                }, i * 100);
            }
        }

        // Add keyboard support
        document.addEventListener('keydown', (e) => {
            const key = e.key.toLowerCase();
            if (key === 's' || key === 'w' || key === 'g') {
                playGame(key);
            }
        });
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())
    
    def handle_play_request(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode())
        
        result = self.game.play_round(data['choice'])
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())

def run_console_game():
    """Your original console game"""
    game = GameLogic()
    
    print("🐍 Snake Water Gun Console Game 🔫")
    print("Commands: s=Snake, w=Water, g=Gun, q=Quit")
    
    while True:
        youstr = input("\nEnter your choice (s/w/g) or 'q' to quit: ").lower().strip()
        
        if youstr == 'q':
            print("Thanks for playing!")
            break
        
        result = game.play_round(youstr)
        
        if "error" in result:
            print(result["error"])
        else:
            print(f"Computer chose: {result['computer_choice_name']}")
            print(result["result"])

def run_web_server():
    """Run the web server"""
    port = 5500
    server = HTTPServer(('127.0.0.1', 5500), GameHandler)
    print(f"🌐 Web server running at http://127.0.0.1:{port}")
    print("Opening browser...")
    
    # Open browser after a short delay
    threading.Timer(1, lambda: webbrowser.open(f'http://127.0.0.1:{port}')).start()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()

if __name__ == "__main__":
    print("🎮 Snake Water Gun Game")
    print("Choose how to play:")
    print("1. Console Game")
    print("2. Web Game")
    choice = input("Enter 1 or 2 (or 'q' to quit): ").lower().strip()
    
    if choice == '1':
        run_console_game()
    elif choice == '2':
        run_web_server()
    elif choice == 'q':
        print("Goodbye!")
    else:
        print("Invalid choice! Please enter 1, 2, or 'q'.")