from flask import Flask, render_template, jsonify
from assistant import listen, handle_command, authenticate_google_calendar,get_today_events, tell_today_events, send_email, search_wikipedia,get_top_news     # Import your assistant functions

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
    response = handle_command(command, service)  # Pass service here
    if response == "Goodbye! Let me know if you need any further assistance.":  # Exit command
        return jsonify({"command": command, "response": response, "exit": True}) 
    return jsonify({"command": command, "response": response})


if __name__ == '__main__':
    service = authenticate_google_calendar()
    # get_today_events(service)
    # tell_today_events(service)
    
    # subject = "hi bro"
    # body = "hi body"
    # recipient_email = "pratikmicrosoft1226@gmail.com"
    # send_email(recipient_email,subject,recipient_email)
    
    # query = "Python (programming language)"
    # print(search_wikipedia(query))
    
    # query = "Python programming"
    # print(get_top_news(query))
    
    #for spotify
    # play_music()
    
    # play_youtube_music("Sai ram")
    app.run(threaded=True,debug=True)
