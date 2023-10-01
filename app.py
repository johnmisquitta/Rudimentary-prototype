from flask import Flask, request, render_template
import os
from moviepy.editor import AudioFileClip
import speech_recognition as sr


app = Flask(__name__)

def convert_audio_to_wav(input_path, output_path):
    # Check if the output directory exists and create it if not
    output_dir = "output_audio"#os.path.dirname(output_path)

    if not os.path.exists(output_dir):

        os.makedirs(output_dir)
    print("check")

    # Load the audio clip using moviepy
    audio = AudioFileClip(input_path)

    # Export audio as WAV
    audio.write_audiofile(output_path, codec='pcm_s16le')

def transcribe_audio(audio_file_path):
    # Convert audio to WAV format
    wav_file_path = "converted_audio.wav"
    convert_audio_to_wav(audio_file_path, wav_file_path)

    # Initialize the recognizer
    recognizer = sr.Recognizer()

    try:
        # Load the WAV audio file
        with sr.AudioFile(wav_file_path) as source:
            print(f"Transcribing {audio_file_path}...")
            audio_data = recognizer.record(source)  # Record the entire audio file

            # Use Google Web Speech API to transcribe the audio
            transcription = recognizer.recognize_sphinx(audio_data)
            print("check1")

            return transcription
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError as e:
        return f"Could not request results from Google Web Speech API; {e}"
    finally:
        # Clean up the temporary WAV file
        os.remove(wav_file_path)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    message = None
    message1 = None

    if request.method == 'POST':
        if 'file' not in request.files:
            message = 'No file part'
        file = request.files['file']
        if file.filename == '':
            message = 'No selected file'
        elif file:
            # Handle the uploaded file (e.g., save it or process it)
            file.save('uploads/' + file.filename)
            message = 'uploading file'
            message1 = input()
    return render_template('upload.html', message=message, message1=message1)


def input():
    input_audio_path = "uploads/sample.mp3"  # Replace with the actual path to your input MP3 file
    print("hh")

    try:
        transcription = transcribe_audio(input_audio_path)
        print("Transcription:")
        print(transcription)


        message = 'file uploaded sucessfully'
        search_word=request.form.get('search_word')
        word_count = transcription.lower().count(search_word.lower())

        #text="Word    \n:"+search_word+"\n       Transcription :\n"+transcription
        return f"The word '{search_word}' appears {word_count} times in the text."
        #return render_template('upload.html',message1=text)


    except Exception as e:
        message = f"Error during transcription: {str(e)}"
        return message

if __name__ == '__main__':
    app.run(debug=True)
