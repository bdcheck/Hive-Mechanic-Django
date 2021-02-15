# pylint: disable=line-too-long, missing-module-docstring

import datetime

from client import HiveClient, TriggerInterruptCommand, SetVariableCommand, VariableScope

#Swap in the correct Hive API URL and Client Token for your game here:
HIVE_API_URL = 'https://workshop.hivemechanic.org/http/'
HIVE_CLIENT_TOKEN = 'testerapi481943' # nosec - This is a placeholder for someone to fill out on their own machine. (Do not delete - see Bandit documentation.)


#Determine what happens when the button is pressed
def send_msg_clicked(event):
    print("Button Pressed" +str(event))

    #DO NOT TOUCH -- this connects your button to Hive Mechanic
    client = HiveClient(api_url= HIVE_API_URL, token= HIVE_CLIENT_TOKEN)

    commands = [
        TriggerInterruptCommand('BUTTON-PRESSED'),
        SetVariableCommand('button_press_ts', datetime.timezone, VariableScope.game)
    ]

    response = client.issue_command(TriggerInterruptCommand('BUTTON-PRESSED'), player='pi:12345')

    audio_url = client.fetch_variable('claimed_audio_file', scope=VariableScope.game)

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
