import torch
import torchaudio
from flask import Blueprint, request, jsonify
from app.services.speaker_utils import group_sentences_by_speaker
from app.services.text_sentiment import perform_sentiment_analysis, compute_overall_sentiment
from app.services.transcription_service import transcribe_audio
from app.services.sentiment import calculate_loudness_and_dbfs, predict_sentiment, group_audio_by_speaker, \
    align_sentiment_with_transcription
from app.services.noise_reduction import reduce_noise
from app.services.s3_service import download_audio_from_url
from app.services.speaker_identification import identify_roles_by_keyword_introduction

routes = Blueprint('routes', __name__)

@routes.route('/')
def home():
    return "Welcome to the Transcription API! Use the /upload endpoint to transcribe audio files."

# @routes.route('/upload', methods=['POST'])
# async def upload_file():
#     audio_url = request.json.get('audio_url', None)
#
#     if not audio_url:
#         return jsonify({"error": "No audio URL provided"}), 400
#
#     # Download the audio from the URL
#     try:
#         file_path = await download_audio_from_url(audio_url)
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400
#
#     # Load the audio file
#     signal, sample_rate = torchaudio.load(file_path)
#
#     # Step 2: Apply noise reduction
#     print("Applying noise reduction...")
#     signal = reduce_noise(signal.mean(dim=0, keepdim=True), sample_rate)
#     print("Transcribing audio...")
#     # Transcribe the file
#     response = await transcribe_audio(file_path)
#     print("Grouping sentences by speaker...")
#     # Process and return the transcription
#     speaker_dialogues = group_sentences_by_speaker(response)
#
#     # Analyze sentiment and loudness for each speaker based on grouped sentences
#     print("\nSentiment Analysis by Speaker:\n")
#     speaker_analysis = []
#     words = response['results']['channels'][0]['alternatives'][0]['words']
#     print("\nGrouping audio by speaker...\n")
#     speaker_audio = group_audio_by_speaker(words, signal, sample_rate)  # Group audio by speaker
#
#     # Perform sentiment analysis
#     print("\nPerforming Sentiment Analysis...\n")
#     sentence_sentiments = await perform_sentiment_analysis(speaker_dialogues)  # Await the result
#
#     print("\nPerforming Sentiment Analysis calculation...\n")
#     for speaker_id, audio_data in speaker_audio.items():
#         speaker_signal = torch.tensor(audio_data)
#         rms, dbfs = calculate_loudness_and_dbfs(speaker_signal)
#         sentiment = predict_sentiment(rms, dbfs)
#
#         # Append analysis results
#         speaker_analysis.append({
#             "audio_sentiment": sentiment,
#             "speaker_id": speaker_id,
#         })
#
#     print("\nAligning sentiment with transcription...\n")
#     # Combine audio and text sentiments
#     aligned_speaker_analysis =  align_sentiment_with_transcription(
#         transcription=speaker_dialogues,  # Pass the speaker_dialogues as the transcription
#         sentiment_analysis=speaker_analysis,
#         text_sentiments=sentence_sentiments  # Ensure that text_sentiments is already awaited
#     )
#
#     return jsonify({
#         "transcription": speaker_dialogues,
#         "speaker_analysis": aligned_speaker_analysis
#     })


@routes.route('/upload', methods=['POST'])
async def upload_file():
    audio_url = request.json.get('audio_url', None)
    if not audio_url:
        return jsonify({"error": "No audio URL provided"}), 400

    # 1. Download the audio
    try:
        file_path = await download_audio_from_url(audio_url)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    # 2. Load and process the audio
    signal, sample_rate = torchaudio.load(file_path)
    print("Applying noise reduction...")
    signal = reduce_noise(signal.mean(dim=0, keepdim=True), sample_rate)

    # 3. Transcribe the audio
    print("Transcribing audio...")
    response = await transcribe_audio(file_path)
    print("Grouping sentences by speaker...")
    speaker_dialogues = group_sentences_by_speaker(response)

    # 4. Identify Agent and Customer
    print("Identifying agent and customer...")
    speaker_roles = identify_roles_by_keyword_introduction(speaker_dialogues)

    # 5. Group audio by speaker
    print("Grouping audio by speaker...")
    words = response['results']['channels'][0]['alternatives'][0]['words']
    speaker_audio = group_audio_by_speaker(words, signal, sample_rate)

    # 6. Perform text sentiment analysis
    print("Performing text sentiment analysis...")
    sentence_sentiments = await perform_sentiment_analysis(speaker_dialogues)

    # 7. Perform audio sentiment analysis
    print("Performing audio sentiment analysis...")
    speaker_analysis = []
    for speaker_id, audio_data in speaker_audio.items():
        speaker_signal = torch.tensor(audio_data)
        rms, dbfs = calculate_loudness_and_dbfs(speaker_signal)
        sentiment = predict_sentiment(rms, dbfs)

        speaker_analysis.append({
            "audio_sentiment": sentiment,
            "speaker_id": speaker_id,
            "role": speaker_roles.get(speaker_id, "unknown"),  # Add role from identified speakers
        })

    # 8. Align text and audio sentiments
    print("Aligning sentiments...")
    aligned_speaker_analysis = align_sentiment_with_transcription(
        transcription=speaker_dialogues,
        sentiment_analysis=speaker_analysis,
        text_sentiments=sentence_sentiments
    )

    # 9. Return the final response
    return jsonify({
        "transcription": speaker_dialogues,
        "speaker_analysis": aligned_speaker_analysis
    })






