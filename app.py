from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

# Your original backend logic
youDict = {"s": 1, "w": -1, "g": 0}
reverseDict = {1: "Snake", -1: "Water", 0: "Gun"}

@app.route('/')
def index():
    return render_template('game.html')

@app.route('/play', methods=['POST'])
def play_game():
    data = request.get_json()
    youstr = data.get('choice')
    
    # Random computer choice (your original logic)
    computer = random.choice([-1, 0, 1])
    
    # Map computer numeric value back to string key ('s', 'w', 'g')
    computer_str = next((k for k, v in youDict.items() if v == computer), None)
    
    # Validate user input (your original logic)
    if youstr not in youDict:
        return jsonify({'error': 'Invalid input!'})
    
    you = youDict[youstr]
    computer_choice_name = reverseDict[computer]
    
    # Determine winner (your exact backend logic)
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
    
    return jsonify({
        'computer_choice': computer_str,
        'computer_choice_name': computer_choice_name,
        'result': result,
        'winner': winner
    })

if __name__ == '__main__':
    app.run(debug=True, port=5500)