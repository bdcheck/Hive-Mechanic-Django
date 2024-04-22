# pylint: disable=line-too-long, missing-module-docstring

import datetime

from client import HiveClient, TriggerInterruptCommand, SetVariableCommand, VariableScope

#INSTRUCTIONS: swap out the variables in the list below with the variables specific to your game:
HIVE_API_URL = 'https://workshop.hivemechanic.org/http/'
# This is a placeholder for someone to fill out on their own machine. (Do not delete - see Bandit documentation.)
HIVE_CLIENT_TOKEN = 'testerapi481943' # nosec
# DEVICE_NAME should be a unique name for your computer or RasPi (ex. "RasPi_202A")
DEVICE_NAME = 'pi:12345'
AUDIO_VARIABLE_NAME = 'claimed_audio_file'

#More advanced code follows

#Here we define what we want the button to do when pressed
def send_msg_clicked(event):
    print("Button Pressed" +str(event))

    #DO NOT TOUCH -- this connects your button to Hive Mechanic
    client = HiveClient(api_url= HIVE_API_URL, token= HIVE_CLIENT_TOKEN)

    commands = [
        TriggerInterruptCommand('BUTTON-PRESSED'),
        SetVariableCommand('button_press_ts', datetime.timezone, VariableScope.game)
    ]

    response = client.issue_command(TriggerInterruptCommand('BUTTON-PRESSED'), player=DEVICE_NAME)

    audio_url = client.fetch_variable(AUDIO_VARIABLE_NAME, scope=VariableScope.game)

#UI for window + button, using the Python Tkinter library
try:
    from tkinter import Tk, Label, Button

    window=Tk()
    lbl=Label(window, text="Welcome to the Knock-Knock Game!", fg='red', font=("Helvetica", 16))
    lbl.place(x=125, y=100)
    #btn=Button(window, text="Press to Send Message", fg='blue', command=send_msg_clicked)
    #btn.place(x=175, y=175)

    window.bind('<space>', send_msg_clicked)

    window.title('Knock-Knock Game Button')
    window.geometry("500x300+400+275")
    window.mainloop()
except ImportError:
    print('TK not installed - please implement alternative UI')
