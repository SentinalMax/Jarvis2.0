import pyttsx3

def simple_text_to_speech(message):
    #engine = pyttsx3.init()
    engine = pyttsx3.init(driverName='sapi5') 
    voices = engine.getProperty('voices')

    engine.setProperty('voice', voices[1].id)

    engine.say(str(message))
    engine.runAndWait()
    

simple_text_to_speech("test")