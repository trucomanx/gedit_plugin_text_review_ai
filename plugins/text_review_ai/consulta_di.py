#!/usr/bin/python3

from gtts import gTTS
from playsound import playsound
import tempfile

def play_message(texto, lang="en"):
    # Cria um arquivo temporário para o MP3
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        caminho_temp = temp_audio.name  # Obtém o caminho do arquivo temporário

    # Gera o áudio e salva no arquivo temporário
    tts = gTTS(texto, lang=lang)
    tts.save(caminho_temp)

    # Reproduz o áudio
    playsound(caminho_temp)


from openai import OpenAI

import subprocess


def comparar_textos(texto_in, texto_out, program="meld"):
    with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".input.tex") as temp1, \
         tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".output.tex") as temp2:
        
        temp1.write(texto_in)
        temp2.write(texto_out)
        
        temp1_path = temp1.name
        temp2_path = temp2.name

    # Executa o Meld sem bloquear a execução do script
    subprocess.Popen([program, temp1_path, temp2_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def consulta_deepinfra(base_url,api_key,msg,model,program='meld',speak=True):

    openai = OpenAI(
        api_key=api_key,
        base_url=base_url,
    )

    stream = True # or False

    chat_completion = openai.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": 
            '''You are an expert system that detects spelling, grammar, punctuation, coherence or cohesion errors in latex texts in any language.
    If you find no errors, only return the text "<NOERROR>".
    If you find errors, without any further response comment, only return a corrected version of the text respecting line breaks and try to make the least amount of changes possible, respecting the spirit of the content.
    The review will be done on each text that you receive from the user.'''
            },
            {"role": "user", "content": msg},
        ],
        stream=stream,
    )

    OUT='';
    if stream:
        for event in chat_completion:
            if event.choices[0].finish_reason:
                print(event.choices[0].finish_reason,
                      event.usage.prompt_tokens,
                      event.usage.completion_tokens)
            else:
                OUT=OUT+event.choices[0].delta.content
    else:
        print(chat_completion.choices[0].message.content)
        print(chat_completion.usage.prompt_tokens, chat_completion.usage.completion_tokens)


    if len(OUT)>0:
        if "<NOERROR>" in OUT or msg.strip()==OUT.strip():
            if speak:
                play_message("No errors found")
            else:
                print("<NOERROR>")
        else:
            comparar_textos(msg,OUT,program)
    else:
        if speak:
            play_message("The output has zero length")
        else:
            print("<ZERO>")

