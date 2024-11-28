import os
import re
import speech_recognition as sr
import torch
import numpy as np
import queue
from openai import OpenAI
import whisper
import threading
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from dotenv import load_dotenv
import click

load_dotenv()


@click.command()
@click.option("--model", default="base", help="Whisper model to use", type=click.Choice(["tiny", "base", "small", "medium", "large"]))
@click.option("--english", default=True, help="Whether to use the english model or not", is_flag=True, type=bool)
@click.option("--energy", default=300, help="The minumum genergy level to recognize a speech", type=int)
@click.option("--pause", default=0.8, help="waiting seconds for the recoder to decide end of a speech", type=float)
@click.option("--dynamic_energy", default=False, help="Flag to enable dynamic energy", is_flag=True, type=bool)
@click.option("--wake_word", default="hello", help=" word used to wake up the model", type=str)
@click.option("--verbose", default=True, help="enables detailed processing output", type=bool)
def main(model, english, energy, pause, dynamic_energy, wake_word, verbose):

    if model != "large" and english:
        model = model + ".en"
    audio_model = whisper.load_model(model)
    audio_queue = queue.Queue()
    result_queue = queue.Queue()
    llm = OpenAI()

    threading.Thread(target=record_audio, args=(
        audio_queue, energy, pause, dynamic_energy,)).start()
    threading.Thread(target=transcribe_forever, args=(
        audio_queue, result_queue, audio_model, english, wake_word, verbose,)).start()
    threading.Thread(target=reply, args=(result_queue, llm,)).start()

    while True:
        print(result_queue.get())


def record_audio(audio_queue, energy, pause, dynamic_energy):
    r = sr.Recognizer()
    r.energy_threshold = energy
    r.pause_threshold = pause
    r.dynamic_energy_threshold = dynamic_energy

    with sr.Microphone(sample_rate=16000) as source:
        print("Listening...")
        i = 0
        while True:
            audio = r.listen(source)
            torch_audio = torch.from_numpy(np.frombuffer(
                audio.get_raw_data(), np.int16).flatten().astype(np.float32) / 32768.0)  # type: ignore
            audio_data = torch_audio
            print(audio_data)
            audio_queue.put_nowait(audio_data)
            i += 1


def transcribe_forever(audio_queue, result_queue, audio_model, english, wake_word, verbose):
    while True:
        audio_data = audio_queue.get()
        if english:
            result = audio_model.transcribe(
                audio_data, language='english', fp16=False)
        else:
            result = audio_model.transcribe(audio_data, fp16=False)

        predicted_text = result["text"]

        if predicted_text.strip().lower().startswith(wake_word.strip().lower()):
            pattern = re.compile(re.escape(wake_word), re.IGNORECASE)
            predicted_text = pattern.sub("", predicted_text).strip()
            punc = '''!()-[]{};:'",<>./?@#$%^&*_~'''
            predicted_text = predicted_text.translate(
                {ord(i): None for i in punc})
            if verbose:
                print("You said the wake word.. Processing {}...".format(
                    predicted_text))

            result_queue.put_nowait(predicted_text)
        else:
            if verbose:
                print("You did not say the wake word.. Ignoring")


def reply(result_queue, llm):
    while True:
        result = result_queue.get()
        print(result)
        data = llm.chat.completions.create(
            model="gpt-4o-mini", messages=[{"role": "user", "content": result}], temperature=0, max_tokens=150)
        answer = data.choices[0].message.content
        mp3_obj = gTTS(text=answer, lang="en", slow=False)
        mp3_obj.save("reply.mp3")
        reply_audio = AudioSegment.from_mp3("reply.mp3")
        play(reply_audio)
        os.remove("reply.mp3")


main()
