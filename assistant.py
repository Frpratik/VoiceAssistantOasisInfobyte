import pyttsx3
from datetime import datetime, timedelta
import time
import speech_recognition as sr
from flask import Flask, request, jsonify
import requests
import threading 
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

app = Flask(__name__)

API_KEY = "0fd53170c484a6c121a3e9352ec6d5f786f2e921"
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather?'
city = "Mumbai"
reminders = []  # List to store reminders
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_weather(city):
    url = f"{BASE_URL}q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        main = data['main']
        wind = data['wind']
        weather_desc = data['weather'][0]['description']
        temperature = main['temp']
        humidity = main['humidity']
        wind_speed = wind['speed']
        
        return (f"Currently in {city}, the weather is {weather_desc} with a temperature of {temperature}°C, "
                f"humidity at {humidity}%, and wind speed of {wind_speed} m/s.")
    else:
        return "Sorry, I couldn't fetch the weather data."

def speak(text):
    print(f"Speaking: {text}")  # Debug print statement
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)  
    engine.setProperty('volume', 1.0) 
    engine.say(text)
    engine.runAndWait()
    engine.stop()

def listen(retries=5):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        for _ in range(retries):
            try:
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
                command = recognizer.recognize_google(audio)
                print(f"User said: {command}\n")
                return command.lower()
            except (sr.UnknownValueError, sr.RequestError, sr.WaitTimeoutError):
                speak("Sorry, I didn't understand that. Please try again.")
        return None
    
def check_reminders():
    while True:
        now = datetime.now()
        due_reminders = [rem for rem in reminders if rem['time'] <= now]
        for reminder in due_reminders:
            speak(f"Reminder: {reminder['message']}")
            reminders.remove(reminder)
        time.sleep(60)

reminder_thread = threading.Thread(target=check_reminders, daemon=True)
reminder_thread.start()

def handle_command(command, service):
    if "calendar" in command:
        return tell_today_events(service)

    if "set a reminder" in command:
        try:
            reminder_message = command.split("reminder to ")[1].split(" in ")[0]
            time_amount, time_unit = command.split(" in ")[1].split()[:2]
            time_amount = int(time_amount)

            if "minute" in time_unit:
                reminder_time = datetime.now() + timedelta(minutes=time_amount)
            elif "hour" in time_unit:
                reminder_time = datetime.now() + timedelta(hours=time_amount)
            else:
                speak("I can only set reminders in minutes or hours for now.")
                return "Failed to set reminder."

            reminders.append({"message": reminder_message, "time": reminder_time})
            speak(f"Reminder set to {reminder_message} in {time_amount} {time_unit}.")
            return f"Reminder set: {reminder_message} in {time_amount} {time_unit}."
        except Exception:
            speak("Sorry, I couldn't understand the reminder details.")
            return "Failed to set reminder."

    response_texts = {
        'hello': "Hey there! How can I help you today?",
        'how are you': "I'm just a program, but I'm doing great! How about you?",
        'time': f"The current time is {datetime.now().strftime('%H:%M')}.",
        'date': f"Today's date is {datetime.now().strftime('%Y-%m-%d')}.",
        'weather': get_weather(city),
        'joke': "Why don't skeletons fight each other? Because they don’t have the guts!",
        'projects': "You’ve worked on great projects like a Personal Finance Management System and an Online Event Management System.",
        'experience': "You have experience in Python, Django, and you're currently working at Mobitrail Private Limited as a software developer.",
        'background': "You hold a Bachelor's in Computer Applications, with additional full stack development certifications.",
        'goal': "You aim to pursue a Master's in Computer Science and work on real-world projects.",
        'exit': "Goodbye! Let me know if you need any further assistance.",
        'thank you': "You're very welcome! I'm always here to help.",
    }

    for key, response in response_texts.items():
        if key in command:
            speak(response)
            return response

    speak("I'm not sure how to help with that.")
    return "I'm not sure how to help with that."

def authenticate_google_calendar():
    creds = None
    try:
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    except Exception:
        flow = InstalledAppFlow.from_client_secrets_file('C:\\Users\\prati\\OneDrive\\Desktop\\VoiceAssistant.OasisInfobyte\\cred\\credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def get_today_events(service):
    now = datetime.utcnow().isoformat() + 'Z'
    end_of_day = (datetime.utcnow() + timedelta(days=1)).isoformat() + 'Z'
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        timeMax=end_of_day,
        maxResults=10,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    return events_result.get('items', [])

def tell_today_events(service):
    events = get_today_events(service)
    if not events:
        response_text = "You have no events scheduled for today."
    else:
        response_text = "Here are your events for today: "
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            event_summary = event.get('summary', 'No Title')
            response_text += f"At {start}, you have {event_summary}. "
    
    speak(response_text)
    print(response_text)
    return response_text

if __name__ == "__main__":
    app.run(threaded=True, debug=False)
