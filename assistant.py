import pyttsx3
from datetime import datetime
import time
import speech_recognition as sr
from flask import Flask, request, jsonify

app = Flask(__name__)

def speak(text):
    """Speak the given text using the text-to-speech engine."""
    print(f"Speaking: {text}")  # Debug print statement
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)  # 0 = Male & 1 = Female
    engine.setProperty('rate', 150)  # Speed adjustment
    engine.setProperty('volume', 1.0)  # Volume level adjustment
    engine.say(text)
    engine.runAndWait()
    engine.stop()

def listen(retries=5):
    """Listen for a voice command with multiple retry attempts."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)  # Adjust for background noise
        for attempt in range(retries):
            try:
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
                command = recognizer.recognize_google(audio)
                print(f"User said: {command}\n")
                return command.lower()
            except sr.UnknownValueError:
                speak("Sorry, I didn't understand that. Please try again.")
                time.sleep(1)
            except sr.RequestError:
                speak("Sorry, my speech service is down.")
                return None
            except sr.WaitTimeoutError:
                speak("Listening timed out. Please try again.")
                return None
        speak("I couldn't hear you clearly. Let's try again.")
        return None

def handle_command(command):
    """Handle the recognized voice command and respond accordingly."""
    command = command.lower()
    responses = {
        'hello': "Hello! How can I assist you?",
        'your name': "I'm your voice assistant.",
        'time': f"The time is {datetime.now().strftime('%H:%M')}.",
        'date': f"Today's date is {datetime.now().strftime('%Y-%m-%d')}.",
        'weather': "I'm unable to check the weather right now. Please check a weather app.",
        'purpose': "I'm here to assist you with your queries and tasks.",
        'joke': "Why did the scarecrow win an award? Because he was outstanding in his field!",
        'projects': "You've worked on various projects, including a Personal Finance Management System and an Online Event Management System.",
        'experience': "You have 1 year of professional experience primarily in Python and Django, and you are currently working as a software developer at Mobitrail Private Limited.",
        'background': "You have a Bachelor in Computer Applications from Pune University and have completed a Master's course in Full Stack Development.",
        'interest': "You love coding, learning new technologies, and exploring new skills.",
        'goal': "You aim to pursue a Master's in Computer Science and are particularly interested in projects that integrate computer science with real-world applications.",
        'exit': "Goodbye!"  # This will signal the conversation to stop
    }
    for key in responses.keys():
        if key in command:
            response_text = responses[key]
            if key == 'exit':
                speak(response_text)  # Speak the response
                exit(0)
            print(f"Response: {response_text}")  # Print the response for debugging
            speak(response_text)  # Speak the response
            return response_text
    speak("I'm not sure how to help with that.")
    return "I'm not sure how to help with that."

# Example of running the assistant
if __name__ == "__main__":
    app.run(threaded=True, debug=False)
