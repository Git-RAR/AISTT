from tkinter import *
from deepgram import Deepgram
import asyncio
import json
import os
import sys
import numpy
import wavio
import sounddevice

recording = False
audio_chunks = []

with open('config.json') as f:
    config = json.load(f)

api_key = config['API_KEY']


def deepgram_api():
    DEEPGRAM_API_KEY = api_key

    FILE = os.path.abspath('recording1.wav')

    MIMETYPE = 'audio/wav'

    async def main():

        deepgram = Deepgram(DEEPGRAM_API_KEY)

        if FILE.startswith('http'):
            source = {'url': FILE}
        else:
            audio = open(FILE, 'rb')
            source = {'buffer': audio, 'mimetype': MIMETYPE}

        response = await asyncio.create_task(deepgram.transcription.prerecorded(source, {'smart_format': True, 'model': 'nova', }))
        #fmt:off
        text_area.insert(END, str(response["results"]["channels"][0]["alternatives"][0]["transcript"]))
        #fmt:on
    try:
        asyncio.run(main())
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        print(f'line {line_number}: {exception_type} - {e}')


def callback(indata, frames, time, status):
    global audio_chunks
    if status:
        print(status, file=sys.stderr)
    if recording:
        audio_chunks.append(indata.copy())


def start_recording():
    record_button.config(text="Recording...")
    global recording
    recording = not recording
    if not recording:
        save_audio()


def save_audio():
    global audio_chunks
    if audio_chunks:
        record_button.config(text="Start Recording")
        audio_data = numpy.concatenate(audio_chunks, axis=0)
        wavio.write('recording1.wav', audio_data, 48000, sampwidth=2)

        audio_chunks = []

    deepgram_api()


def copy():
    text = text_area.get("1.0", END)
    window.clipboard_clear()
    window.clipboard_append(text)


def clear():
    text_area.delete('1.0', END)


window = Tk()

icon = PhotoImage(file='icon.png')
window.wm_iconphoto(False, icon)

bg_color = 'LightGray'

window.title("Speech To Text")

# ? This is to open the window in the center of your screen

window_width = 600
window_height = 600
window.geometry(f"{window_width}x{window_height}")

screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

x_coordinate = (screen_width/2) - (window_width/2)
y_coordinate = (screen_height/2) - (window_height/2)

# fmt: off
window.geometry(f"{window_width}x{window_height}+{int(x_coordinate)}+{int(y_coordinate)}")
# fmt: on

# ?
###########################################################################################################################################################################
# ? Setup for the labels, text area and, buttons

# fmt: off
label = Label(window, text='Area to recieve and edit text:',font=("Helvetica", 12), bg=bg_color)
label.grid(row=0, column=0, sticky='w', padx=10, pady=10)

text_area = Text(window, width=50, height=25, wrap=WORD)
text_area.grid(row=1, column=0, sticky="nsew")
text_area.configure(font=("Ariel", 12))

text_area.grid_rowconfigure(1, weight=1)
text_area.grid_columnconfigure(0, weight=1)

record_button = Button(window, text='Start Recording',command=start_recording, width=20, height=3)
record_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

copy_button = Button(window, text='Copy Text', width=10, height=2, command=copy)
copy_button.grid(row=0, column=1, padx=25, pady=10, rowspan=2)

clear_button = Button(window, text='Clear Text', width=10, height=2, command=clear)
clear_button.grid(row=1, column=1, padx=25, pady=10, rowspan=2)

ChatGpt_button = Button(window, text='ChatGpt Rework',width=15, height=3, state=DISABLED)
ChatGpt_button.grid(row=2, column=1, padx=25, pady=10, rowspan=1)
#fmt:on

window.resizable(False, False)
window.configure(bg=bg_color)
with sounddevice.InputStream(samplerate=48000, callback=callback):
    window.mainloop()
