import speech_recognition as sr
import pyttsx3
from datetime import datetime
import time

recognizer = sr.Recognizer()
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen(retries=3):
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)  # Adjusts to background noise
        for attempt in range(retries):
            try:
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
                command = recognizer.recognize_google(audio)
                print(f"User said: {command}\n")
                return command.lower()
            except sr.UnknownValueError:
                speak("Sorry, I didn't understand that. Please try again.")
                time.sleep(1)  # Wait a moment before listening again
            except sr.RequestError:
                speak("Sorry, my speech service is down.")
                return None
            except sr.WaitTimeoutError:
                speak("Listening timed out. Please try again.")
                return None
        speak("I couldn't hear you clearly. Let's try again.")
        return None

def handle_command(command):
    command = command.lower()

    if 'hello' in command:
        speak("Hello! How can I assist you?")
    elif 'your name' in command:
        speak("I'm your voice assistant.")
    elif 'time' in command:
        now = datetime.now().strftime("%H:%M")
        speak(f"The time is {now}.")
    elif 'date' in command:
        today = datetime.now().strftime("%Y-%m-%d")
        speak(f"Today's date is {today}.")
    elif 'weather' in command:
        speak("I'm unable to check the weather right now. Please check a weather app.")
    elif 'purpose' in command:
        speak("I'm here to assist you with your queries and tasks.")
    elif 'joke' in command:
        speak("Why did the scarecrow win an award? Because he was outstanding in his field!")
    elif 'projects' in command:
        speak("You've worked on various projects, including a Personal Finance Management System and an Online Event Management System.")
    elif 'experience' in command:
        speak("You have 1 years of professional experience primarily in Python and Django, and you are currently working as a software developer at Mobitrail Private Limited.")
    elif 'background' in command:
        speak("You have a Bachelor in Computer Applications from Pune University and have completed a Master's course in Full Stack Development.")
    elif 'interest' in command or 'hobby' in command:
        speak("You love coding, learning new technologies, and exploring new skills.")
    elif 'goal' in command or 'aspiration' in command:
        speak("You aim to pursue a Master's in Computer Science and are particularly interested in projects that integrate computer science with real-world applications.")
    elif 'friend' in command or 'ranjan' in command:
        speak("Ranjan is an excellent boy and a great friend.")
    elif 'why did' in command or 'create' in command:
        speak("You created this voice assistant because you want to explore new things.")
    elif 'exit' in command:
        return False 
    else:
        speak("I'm not sure how to help with that.")
        
    return True  



# Main function to run the assistant
def run_voice_assistant():
    speak("How can I assist you?")
    fail_count = 0  # To count the number of failed attempts
    while True:
        command = listen(retries=3)
        if command:
            if not handle_command(command):
                speak("Goodbye!")
                break
            fail_count = 0  # Reset fail count on success
        else:
            fail_count += 1  # Increment fail count on failure

        if fail_count >= 5:
            speak("I couldn't understand you five times in a row. Exiting now.")
            break

if __name__ == "__main__":
    run_voice_assistant()
