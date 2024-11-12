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
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import wikipedia
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth



app = Flask(__name__)

WEATHER_API_KEY = "816ef82169eafd7d91e40b372684f15a"   # weather api key
NEWS_API_KEY = 'ab2d72cd5956487f9ac809ce71488e1b'      #news api key
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather?'
city = "Mumbai"
reminders = []  # List to store reminders
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# Set a wikipedia custom user-agent and lang 
wikipedia.set_lang("en")
wikipedia.set_user_agent("VoiceAssistant/1.0 (pratikmicrosoft1226@gmail.com)")

def get_weather(city):
    url = f"{BASE_URL}q={city}&appid={WEATHER_API_KEY}&units=metric"
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
    
#================================================================================================================================
#================================================================================================================================

def speak(text):
    print(f"Speaking: {text}")  # Debug print statement
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)  
    engine.setProperty('volume', 1.0) 
    engine.say(text)
    engine.runAndWait()
    engine.stop()
    
#================================================================================================================================
#================================================================================================================================

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
    
#================================================================================================================================
#================================================================================================================================

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

#===============================================================================================================================
#================================================================================================================================

def handle_command(command, service):
    if "calendar" in command:
        return tell_today_events(service)
    
    if "play" in command:
            play_music()
            
    if "pause" in command:
        pause_music()

    if "skip" in command:
        skip_track()
        
    elif "volume up" in command:
        current_volume = sp.current_playback()['device']['volume_percent']
        new_volume = min(current_volume + 10, 100)
        sp.volume(new_volume)
        speak(f"Volume set to {new_volume}%")

    elif "volume down" in command:
        current_volume = sp.current_playback()['device']['volume_percent']
        new_volume = max(current_volume - 10, 0)
        sp.volume(new_volume)
        speak(f"Volume set to {new_volume}%")

    """Check reminders and notify the user if any are due."""
    """Set a reminder to drink water in 5 minutes.>>>>pattern for setting reminders""" 
    
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
        
    if 'send email' in command:
        # No exception handeling needed bcz send_email handles itself
        # Prompt for recipient email, subject, and message
        speak("Please tell me the recipient's email address.")
        recipient_email = listen() 
        
        corrections = {
            "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "six": "6", 
            "seven": "7", "eight": "8", "nine": "9",
            "dot": ".", "at": "@", "com": "com"
        }
    
        for word, replacement in corrections.items():
            recipient_email = recipient_email.replace(word, replacement).lower()
            recipient_email = recipient_email.replace(" ", "")
        
        speak("What is the subject of the email?")
        subject = listen()
        speak("What is the message?")
        body = listen()
        # Send the email
        send_email(recipient_email, subject, body)
    
    if "search wikipedia for" in command:
        topic = command.replace("search wikipedia for", "").strip()
        response = search_wikipedia(topic)
        speak(response)
        return response

    if "search news for" in command:
        news_query = command.replace("search news for", "").strip()
        result = get_top_news(news_query)
        speak(result)
        return result

        
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

#================================================================================================================================
#================================================================================================================================

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

#================================================================================================================================
#================================================================================================================================

# Email setup
EMAIL_ADDRESS = "ghugepratik2619@gmail.com"  # Replace with your email
EMAIL_PASSWORD = "ljfx bwcy fbga xxxu"  # app passwords> created app specific password
def send_email(recipient_email, subject, body):
    try:
        # Setup the MIME
        message = MIMEMultipart()
        message['From'] = EMAIL_ADDRESS
        message['To'] = recipient_email
        message['Subject'] = subject

        # Attach the body of the email to the MIME message
        message.attach(MIMEText(body, 'plain'))

        # Connect to Gmail's SMTP server
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Enable security
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)  # Login to your email account
            # print("Login successfull=================================")
            text = message.as_string()  # Convert the MIME message to a string
            server.sendmail(EMAIL_ADDRESS, recipient_email, text)  # Send the email

        print("Email sent successfully!")
        speak("Email sent successfully!")
        return "Email sent successfully!"


    except Exception as e:
        print(f"Failed to send email: {e}")
        speak("Failed to send the email. Please check the details and try again.")
        return "Failed to send the email. Please check the details and try again."

#================================================================================================================================
#================================================================================================================================

# Function to search Wikipedia
def search_wikipedia(query):
    try:
        # Get the summary of the page
        summary = wikipedia.summary(query, sentences=2)
        return summary
    # except wikipedia.exceptions.DisambiguationError as e:
    #     return f"Multiple results found: {e.options}"
    # except wikipedia.exceptions.HTTPError as e:
    #     return f"HTTP error occurred: {e}"
    # except wikipedia.exceptions.ConnectionError as e:
    #     return f"Connection error occurred: {e}"
    # except wikipedia.exceptions.RedirectError as e:
    #     return f"Redirect error occurred: {e}"
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Something went wrong while searching for wikipedia"
    
#================================================================================================================================
#================================================================================================================================

def fetch_news(query):
    try:
        # NewsAPI endpoint for search
        url = f'https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}'
        
        # Make a GET request to fetch the news
        response = requests.get(url)
        data = response.json()

        # Check if the response contains articles
        if data.get('status') == 'ok' and 'articles' in data:
            articles = data['articles']
            return articles
        else:
            return "No news found for your query."
    except Exception as e:
        return f"An error occurred: {e}"

def get_top_news(query, num_results=3):
    news = fetch_news(query)
    
    if isinstance(news, str):  # Error or no results
        return news
    
    # Extract the top 'num_results' from the news articles
    top_news = []
    for article in news[:num_results]:
        title = article['title']
        description = article['description']
        url = article['url']
        top_news.append(f"Title: {title}\nDescription: {description}\n")
    
    return "\n\n".join(top_news)

#================================================================================================================================
#================================================================================================================================
# Define the necessary scopes
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="8645f414b1bd47bc9c4cc15ca782e3f4",
                                               client_secret="7ea1f214793b4681a28232859959b618",
                                               redirect_uri="http://127.0.0.1:5000",
                                               scope=["user-library-read", "user-read-playback-state", "user-modify-playback-state"]))

# Function to play music
def play_music():
    sp.start_playback()
    speak("Playing music.")

# Function to pause music
def pause_music():
    sp.pause_playback()
    speak("Music paused.")

# Function to skip to next track
def skip_track():
    sp.skip_to_next()
    speak("Skipping to next track.")

#================================================================================================================================
#================================================================================================================================

# import pywhatkit as kit

# def play_youtube_music(song_name):
#     kit.playonyt(song_name)  # This will open the default browser and play the first YouTube result
    
#================================================================================================================================
#================================================================================================================================
# 🚀 Introducing My Personal Voice Assistant Project 🚀

# I’m excited to share my Personal Voice Assistant project, developed using Python, Flask, and integrated with several APIs to simplify daily tasks through voice commands.



# ⏺️ Project Overview:

# This voice assistant includes features like Google Calendar integration, Wikipedia search, weather updates, and the ability to send emails. It also supports Spotify for music control, although full functionality is limited without a Spotify Premium account.



# ⏺️Key Features:

# ✔️ Google Calendar Integration (via Firebase) 📅

# Voice Command: “What’s on my calendar today?”

# The assistant syncs with Google Calendar through Firebase to manage and retrieve events. It provides live updates of your schedule.

# ✔️ Voice-Activated Email ✉️

# Voice Command: “Send an email to [contact name]”

# Dictate emails to the assistant, which converts speech into text and sends them to the intended recipient—perfect for on-the-go communications.

# ✔️ Weather Updates 🌦️

# Voice Command: “What’s the weather today?”

# Get real-time weather information by asking the assistant for today’s forecast.

# ✔️ News Fetching 📰

# Voice Command: “Search news for [topic]”

# Stay updated with the latest news. The assistant will read the latest headlines on your chosen topic.

# ✔️ Spotify Integration (Limited) 🎶

# Voice Commands: “Play”, “Pause”, “Next”, "Previous",“Volume up/down”

# Play, pause, skip, and control the volume via voice commands. However, full functionality is unavailable due to the lack of a Spotify Premium account. With a premium account, music streaming will be uninterrupted.

# ✔️ Wikipedia Search 📚

# Voice Command: “Search Wikipedia for [topic]”

# Ask the assistant to search Wikipedia for any topic, and it will read out relevant articles for you.

# ✔️ Setting Reminders ⏰

# Voice Command: “Set a reminder for [time] to [task]”

# The assistant allows users to set reminders through voice commands. It uses threading to handle multiple reminders at once, ensuring you get notified at the right time without any delays.



# ⏺️Technologies Used:

# ▶️ Python: Backend scripting and voice command processing

# ▶️Flask: Web server and API handling

# ▶️Google Calendar API: Event management and reminders

# ▶️OpenWeatherMap API: Weather information

# ▶️News API: Latest news headlines

# ▶️Wikipedia API: Wikipedia content retrieval

# ▶️SpeechRecognition: Converts voice to text

# ▶️Spotify API: Music control (limited with free account)

# ▶️Threading: Handles multiple reminders simultaneously



# ⏺️Future Enhancements:

# ⬆️ Full Spotify Premium integration for uninterrupted music.

# ⬆️Smart home and task management features.

# ⬆️Improved UI/UX for a better user experience.



# 💡 GitHub Repository:

# https://github.com/Frpratik/VoiceAssistantOasisInfobyte



# A special thanks to Oasis Infobyte for the valuable feedback throughout development!



# #VoiceAssistant #Python #Flask #Firebase #GoogleCalendar #SpotifyIntegration #WikipediaSearch #APIIntegration