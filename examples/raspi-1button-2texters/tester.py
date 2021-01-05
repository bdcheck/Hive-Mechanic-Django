import logging
import sys
import time
import client
import settings
import datetime

from client import *
from tkinter import *

#Swap in the correct Hive API URL and Client Token for your game here:
HIVE_API_URL = 'https://workshop.hivemechanic.org/http/'
HIVE_CLIENT_TOKEN = 'abc12345'


#Determine what happens when the button is pressed
def SendMsgClicked():
        print("Button Pressed")

        #DO NOT TOUCH -- this connects your button to Hive Mechanic
        client = HiveClient(api_url= HIVE_API_URL, token= HIVE_CLIENT_TOKEN)

        commands = [
            TriggerInterruptCommand('BUTTON-PRESSED'),
            SetVariableCommand('button_press_ts', datetime.timezone, VariableScope.game)
                ]

        response = client.issue_command(TriggerInterruptCommand('BUTTON-PRESSED'), player='pi:12345')

        audio_url = client.fetch_variable('claimed_audio_file', scope=VariableScope.game)

        
#UI for window + button, using the Python Tkinter library
window=Tk()
lbl=Label(window, text="Welcome to the Knock-Knock Game!", fg='red', font=("Helvetica", 16))
lbl.place(x=125, y=100)
btn=Button(window, text="Press to Send Message", fg='blue', command=SendMsgClicked)
btn.place(x=175, y=175)

window.title('Knock-Knock Game Button')
window.geometry("500x300+400+275")
window.mainloop()
