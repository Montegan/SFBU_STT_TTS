import os
import time
import speech_recognition as sr
import torch
import numpy as np
import queue
import threading
import whisper
from openai import OpenAI
import click
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
load_dotenv()


# @click.command()
# @click.option("--model", default="base", help="Whisper model to use", type=click.Choice(["tiny", "base", "small", "medium", "large"]))
# @click.option("--english", default=True, help="Whether to use the english model or not", is_flag=True, type=bool)
# @click.option("--energy", default=300, help="The minumum genergy level to recognize a speech", type=int)
# @click.option("--pause", default=0.8, help="waiting seconds for the recoder to decide end of a speech", type=float)
# @click.option("--dynamic_energy", default=False, help="Flag to enable dynamic energy", is_flag=True, type=bool)
# @click.option("--wake_word", default="hello", help=" word used to wake up the model", type=str)
# @click.option("--verbose", default=True, help="enables detailed processing output", type=bool)
def its_working():
    return "working fine"


@app.post("/")
def main():
    model = "tiny"
    english = True
    energy = 200
    pause = 0.8
    dynamic_energy = False
    wake_word = "hello"
    verbose = True

    if model != "large" and english:
        model = model + ".en"
    audio_model = whisper.load_model(model)
    audio_queue = queue.Queue()
    results_queue = queue.Queue()
    stop_word = "stop"
    llm = OpenAI()

    stop_event = threading.Event()

    threading.Thread(target=record_audio, args=(
        audio_queue, energy, pause, dynamic_energy, stop_event)).start()
    threading.Thread(target=transcribe_audio, args=(
        audio_model, audio_queue, results_queue, english, wake_word, verbose, stop_event, stop_word,)).start()
    threading.Thread(target=reply, args=(
        llm, stop_event, results_queue,)).start()

    while not stop_event.is_set():
        time.sleep(1)


def record_audio(audio_queue, energy, pause, dynamic_energy, stop_event):
    # Create a speech recognizer and set energy and pause thresholds
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = energy
    recognizer.pause_threshold = pause
    recognizer.dynamic_energy_threshold = dynamic_energy

    with sr.Microphone(sample_rate=16000) as source:
        print("Listening...")
        i = 0
        while not stop_event.is_set():
            # Get and save audio to a WAV file
            audio = recognizer.listen(source)
            # Convert audio to Torch tensor
            torch_audio = torch.from_numpy(
                np.frombuffer(audio.get_raw_data(),  # type: ignore
                              np.int16) .flatten()
                .astype(np.float32) / 32768.0)
            audio_data = torch_audio
            audio_queue.put_nowait(audio_data)
            i += 1
        print("stopping exiting the loop mic should be off")


def transcribe_audio(audio_model, audio_queue, results_queue, english, wake_word, verbose, stop_event, stop_word):
    while not stop_event.is_set():
        audio_data = audio_queue.get()
        if english:
            result = audio_model.transcribe(
                audio_data, language="english", fp16=False)
        else:
            result = audio_model.transcribe(audio_data, fp16=False)

        predicted_text = result["text"]

        if predicted_text.strip().lower().startswith(wake_word.strip().lower()):
            cleaned_text = predicted_text[len(wake_word)+1:]
            punc = '''!()-[]{};:'",<>./?@#$%^&*_~'''
            text_only_prediction = cleaned_text.translate(
                {ord(i): None for i in punc})

            if verbose:
                print("You have said the wake word...Processing {}".format(
                    text_only_prediction))
            results_queue.put_nowait(text_only_prediction)
        elif predicted_text.strip().lower().startswith(stop_word.strip().lower()):
            stop_event.set()
            return
        else:
            if verbose:
                print("wake word did not detected, Please try again")


def reply(llm, stop_event, results_queue):
    while not stop_event.is_set():
        result = results_queue.get()
        reponse = llm.chat.completions.create(
            model="gpt-4o", messages=[
                {"role": "system",
                 "content": """You are helpfull voice assistant, Your task is to 
                 understand what the transcribed text is talking about and give a valid response. 
                 if You didn't understand what the user is asking politly ask them to clarify thier question. 
                 give the output in plain english"""},
                {"role": "user", "content": result}], temperature=0, max_tokens=100)
        answer = reponse.choices[0].message.content
        mp3_obj = gTTS(text=answer, lang="en", slow=False)
        mp3_obj.save("answer.mp3")
        reply_audio = AudioSegment.from_mp3("answer.mp3")
        play(reply_audio)

# main()
