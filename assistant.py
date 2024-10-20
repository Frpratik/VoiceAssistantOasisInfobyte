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

    # Dictionary with keyword variations mapped to responses
    responses = {
        'hello': ["hello", "hi", "hey", "greetings", "what's up", "howdy"],
        'how are you': ["how are you", "how's it going", "how do you feel", "what's up with you"],
        'time': ["time", "current time", "what's the time", "can you tell me the time", "what time is it"],
        'date': ["date", "today's date", "what's the date", "what day is it", "what is today's date"],
        'weather': ["weather", "check weather", "what's the weather", "tell me the weather", "how's the weather", "is it raining"],
        'joke': ["joke", "make me laugh", "something funny", "tell me a joke", "say something funny", "crack a joke"],
        'projects': ["projects", "my work", "tell me about my projects", "what have i worked on", "show me my projects"],
        'experience': ["experience", "work experience", "what is my experience", "tell me about my job", "what is my professional background"],
        'background': ["background", "education", "tell me about my background", "what have i studied", "what's my academic history"],
        'goal': ["goal", "future plans", "what are my goals", "what do i want to achieve", "what is my ambition"],
        'exit': ["exit", "bye", "goodbye", "see you later", "i'm done", "that's it", "quit"],
        'thank you': ["thanks","thank", "thank you", "i appreciate it", "thanks a lot", "many thanks", "much appreciated"],
        'name': ["what's your name", "who are you", "what do i call you", "your name"],
        'help': ["help", "i need help", "assist me", "can you help me", "what can you do"],
        'purpose': ["what is your purpose", "why are you here", "what's your role", "what do you do", "what's your job"],
        'age': ["how old are you", "what's your age", "tell me your age", "how long have you existed"],
        'thank you': ["thanks", "thank you", "appreciate it", "thankful", "many thanks"],
        'favorite color': ["what's your favorite color", "what color do you like", "your favorite color"],
        'where from': ["where are you from", "where do you come from", "your origin", "where are you based"],
        'what can you do': ["what can you do", "what are your abilities", "how can you help me", "what's your skill set"],
    }

    # Responses mapped to the main intent
    response_texts = {
        'hello': "Hey there! How can I help you today?",
        'how are you': "I'm just a program, but I'm doing great! How about you?",
        'time': f"The current time is {datetime.now().strftime('%H:%M')}.",
        'date': f"Today's date is {datetime.now().strftime('%Y-%m-%d')}.",
        'weather': "I can't check the weather at the moment. Try a weather app for live updates!",
        'joke': "Why don't skeletons fight each other? Because they don’t have the guts!",
        'projects': "You’ve worked on great projects like a Personal Finance Management System and an Online Event Management System.",
        'experience': "You have experience in Python, Django, and you're currently working at Mobitrail Private Limited as a software developer.",
        'background': "You hold a Bachelor's in Computer Applications, with additional full stack development certifications.",
        'goal': "You aim to pursue a Master's in Computer Science and work on real-world projects.",
        'exit': "Goodbye! Let me know if you need any further assistance.",
        'thank you': "You're very welcome! I'm always here to help.",
        'name': "I'm your voice assistant, ready to help with your tasks and queries!",
        'help': "I can assist you with checking the time, answering questions about your experience, or even telling a joke!",
        'purpose': "I'm here to assist you with tasks, answer questions, and make your life easier.",
        'age': "I don't have an age, but I was created recently to help you!",
        'favorite color': "I don't have preferences, but blue seems like a calming choice!",
        'where from': "I exist in the cloud, always ready to assist you.",
        'what can you do': "I can help you with queries, check the time, tell jokes, talk about your work or goals, and much more!",
    }

    for key, variations in responses.items():
        if any(variation in command for variation in variations):
            response_text = response_texts[key]

            if key == 'exit':
                speak(response_text)
                exit(0)

            print(f"Response: {response_text}")
            speak(response_text)
            return response_text

    speak("I'm not sure how to help with that.")
    return "I'm not sure how to help with that."


# Example of running the assistant
if __name__ == "__main__":
    app.run(threaded=True, debug=False)
