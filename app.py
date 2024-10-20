from flask import Flask, render_template, jsonify
from assistant import listen, handle_command  # Import your assistant functions

app = Flask(__name__)

# Route for the homepage
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/voice-command', methods=['POST'])
def voice_command():
    command = listen()
    if command is None:
        return jsonify({"error": "Unable to listen. Please try again!"}), 500
    response = handle_command(command)  # Process the command
    if response =="Goodbye! Let me know if you need any further assistance.":  # Exit command
        return jsonify({"command": command, "response": response, "exit": True}) 
    return jsonify({"command": command, "response": response})

if __name__ == '__main__':
    app.run(debug=True)
