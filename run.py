import openai
import winsound
import sys
import pytchat
import time
import re
import pyaudio
import keyboard
import wave
import threading
import json
import socket
from emoji import demojize
from api import *
from utils.translate import *
from utils.TTS import *
from utils.subtitle import *
from utils.promptmaker import *
from utils.twitch import *
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.llms import OpenAI
from langchain.vectorstores import Chroma
import pdfplumber
import PyPDF4
from typing import Callable, List, Tuple, Dict
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from langchain.schema import HumanMessage, AIMessage
import subprocess

sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf8", buffering=1)

openai.api_key = api_key
os.environ["OPENAI_API_KEY"] = api_key

conversation = []
history = {"history": conversation}

mode = 0
total_characters = 0
chat = ""
chat_now = ""
chat_prev = ""
is_Speaking = False
blacklist = ["Nightbot", "streamelements"]
cn = ""
source_file_path = "Ruby_AI\document(s) data\Data of CN and FP.txt"


def record_audio():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    WAVE_OUTPUT_FILENAME = "input.wav"
    p = pyaudio.PyAudio()
    stream = p.open(
        format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK
    )
    frames = []
    print("\rListening...")
    while keyboard.is_pressed("RIGHT_SHIFT"):
        data = stream.read(CHUNK)
        frames.append(data)
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(WAVE_OUTPUT_FILENAME, "wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b"".join(frames))
    wf.close()
    transcribe_audio("input.wav")


def transcribe_audio(file):
    global chat_now
    try:
        audio_file = open(file, "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        chat_now = transcript.text
        print(chat_now)
    except Exception as e:
        print("Error transcribing audio: {0}".format(e))
        return

    result = chat_now
    if result in [
        "Type.",
        "Type mode.",
        "type.",
        "type mode.",
        "Type",
        "Type mode",
        "type",
        "type mode",
    ]:
        print('you can change to Mic by type "mic or mm"')
        while True:
            type_text()
    if result in [
        "Quit.",
        "quit.",
        "Quit",
        "quit",
    ]:
        sys.exit()
    conversation.append({"role": "user", "content": result})
    openai_answer()


def type_text():
    global chat
    while True:
        chat = input("(You)> ")
        if chat in ["mic", "mm"]:
            print(
                'Press and Hold Right Shift to record audio\nYou can change to Type mode by saying "type" or "type mode"'
            )
            while True:
                if keyboard.is_pressed("RIGHT_SHIFT"):
                    record_audio()
        if chat in ["quit", "Quit", "quit.", "Quit.", "q", "Q"]:
            sys.exit()
        if chat in ["read pdf"]:
            read_document_1()
        type_chat = chat
        conversation.append({"role": "user", "content": type_chat})
        openai_answer()


def read_document_1():
    cnt = input('To load documents, type "0"\nTo upload new documents, type "1"\n>> ')
    if cnt in ["0"]:
        collectionName()
    if cnt in ["1"]:
        subprocess.call(["python", "ingest.py"])
        read_document_1()


def collectionName():
    global cn, source_file_path
    cn = input("To view Collection Names history, type \"history\"\nCollection Name: ")

    if cn in ["History", "history"]:
        with open(source_file_path, "r") as source_file:
            content = source_file.read()
            print("\nHistory:\n", content)
            collectionName()
    read_document_2()


def read_document_2():
    def make_chain():
        global cn
        model = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            max_tokens="256",
            temperature="0",
            # verbose=True
        )
        embedding = OpenAIEmbeddings()

        vector_store = Chroma(
            collection_name=cn,
            embedding_function=embedding,
            persist_directory="Ruby_AI\document(s) data\chroma",
        )

        return ConversationalRetrievalChain.from_llm(
            model,
            retriever=vector_store.as_retriever(),
            return_source_documents=True,
            # verbose=True,
        )

    if __name__ == "__main__":
        load_dotenv()

        chain = make_chain()
        chat_history = []
        print('\nGo to Type mode by typing "typ md"\nTo change file, type "ch fl"')
        while True:
            question = input("(You)> ") + (
                ",answer with language that i used in the last sentences before."
            )
            if re.search(r"(typ|Typ)\s+(Md|md)", question):
                type_text()
            if re.search(r"(ch|Ch)\s+(Fl|fl)", question):
                collectionName()
            # Generate answer
            response = chain({"question": question, "chat_history": chat_history})

            # Retrieve answer
            answer = response["answer"]
            source = response["source_documents"]
            chat_history.append(HumanMessage(content=question))
            chat_history.append(AIMessage(content=answer))

            # Display answer
            print("\n\nSources:\n")
            for document in source:
                print(f"Page: {document.metadata['page_number']}")
                print(f"Text chunk: {document.page_content[:160]}...\n")
            translate_text(answer)


def openai_answer():
    global total_characters, conversation

    total_characters = sum(len(d["content"]) for d in conversation)

    while total_characters > 4000:
        try:
            conversation.pop(2)
            total_characters = sum(len(d["content"]) for d in conversation)
        except Exception as e:
            print("Error removing old messages: {0}".format(e))

    with open("history.json", "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)

    prompt = getPrompt()

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=prompt,
        max_tokens=256,
        temperature=0.5,
        top_p=0.9,
    )
    message = response["choices"][0]["message"]["content"]
    conversation.append({"role": "assistant", "content": message})

    translate_text(message)


def yt_livechat(video_id):
    global chat

    live = pytchat.create(video_id=video_id)
    while live.is_alive():
        # while True:
        try:
            for c in live.get().sync_items():
                # Ignore chat from the streamer and Nightbot, change this if you want to include the streamer's chat
                if c.author.name in blacklist:
                    continue
                # if not c.message.startswith("!") and c.message.startswith('#'):
                if not c.message.startswith("!"):
                    # Remove emojis from the chat
                    chat_raw = re.sub(r":[^\s]+:", "", c.message)
                    chat_raw = chat_raw.replace("#", "")
                    # chat_author makes the chat look like this: "Nightbot: Hello". So the assistant can respond to the user's name
                    chat = c.author.name + " said " + chat_raw
                    print(chat)

                time.sleep(1)
        except Exception as e:
            print("Error receiving chat: {0}".format(e))


def twitch_livechat():
    global chat
    sock = socket.socket()

    sock.connect((server, port))

    sock.send(f"PASS {token}\n".encode("utf-8"))
    sock.send(f"NICK {nickname}\n".encode("utf-8"))
    sock.send(f"JOIN {channel}\n".encode("utf-8"))

    regex = r":(\w+)!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :(.+)"

    while True:
        try:
            resp = sock.recv(2048).decode("utf-8")

            if resp.startswith("PING"):
                sock.send("PONG\n".encode("utf-8"))

            elif not user in resp:
                resp = demojize(resp)
                match = re.match(regex, resp)

                username = match.group(1)
                message = match.group(2)

                if username in blacklist:
                    continue

                chat = username + " said " + message
                print(chat)

        except Exception as e:
            print("Error receiving chat: {0}".format(e))


def translate_text(text):
    global is_Speaking

    detect = detect_google(text)

    try:
        print("(Ruby)>", text)
    except Exception as e:
        print("Error printing text: {0}".format(e))
        return

    if detect == "RU":
        silero_tts_ru(text, "ru", "v3_1_ru", "xenia")
    elif detect == "DE":
        silero_tts_de(text, "de", "v3_de", "eva_k")
    elif detect == "ES":
        silero_tts_es(text, "es", "v3_es", "es_0")
    elif detect == "FR":
        silero_tts_fr(text, "fr", "v3_fr", "fr_4")
    else:
        tts_source = translate_google(text, f"{detect}", "EN")
        silero_tts(tts_source, "en", "v3_en", "en_50")

    generate_subtitle(chat_now, text)

    time.sleep(1)

    is_Speaking = True
    winsound.PlaySound("test.wav", winsound.SND_FILENAME)
    is_Speaking = False

    time.sleep(1)
    with open("output.txt", "w") as f:
        f.truncate(0)


def preparation():
    global conversation, chat_now, chat, chat_prev
    while True:
        chat_now = chat
        if is_Speaking == False and chat_now != chat_prev:
            conversation.append({"role": "user", "content": chat_now})
            chat_prev = chat_now
            openai_answer()
        time.sleep(1)


if __name__ == "__main__":
    try:
        mode = input("Mode (1-Mic, 2-Type, 3-Youtube Live, 4-Twitch Live): ")

        if mode == "1":
            print(
                'Press and Hold Right Shift to record audio\nYou can change to Type mode by saying "type" or "type mode"\n'
            )
            while True:
                if keyboard.is_pressed("RIGHT_SHIFT"):
                    record_audio()

        elif mode == "2":
            print(
                'you can change to Mic mode by typing "mic" or "mm"\nto access Read PDF mode, type "read pdf"'
            )
            while True:
                type_text()

        elif mode == "3":
            live_id = input("Livestream ID: ")
            # Threading is used to capture livechat and answer the chat at the same time
            t = threading.Thread(target=preparation)
            t.start()
            yt_livechat(live_id)

        elif mode == "4":
            # Threading is used to capture livechat and answer the chat at the same time
            print(
                "To use this mode, make sure to change utils/twitch_config.py to your own config"
            )
            t = threading.Thread(target=preparation)
            t.start()
            twitch_livechat()
    except KeyboardInterrupt:
        t.join()
        print("Stopped")
