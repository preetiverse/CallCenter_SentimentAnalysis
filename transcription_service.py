from deepgram import Deepgram
import aiofiles
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')
if not DEEPGRAM_API_KEY:
    raise ValueError("DEEPGRAM_API_KEY is not set in environment variables.")

dg_client = Deepgram(DEEPGRAM_API_KEY)


async def transcribe_audio(file_path):
    async with aiofiles.open(file_path, 'rb') as audio:
        audio_data = await audio.read()

    options = {
        'model': 'nova-2',
        'punctuate': True,
        'diarize': True,
        'language': 'hi'
    }
    source = {'buffer': audio_data, 'mimetype': 'audio/mp3'}

    response = await dg_client.transcription.prerecorded(source, options)
    return response

