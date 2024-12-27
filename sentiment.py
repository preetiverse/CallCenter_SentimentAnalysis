import torch
import math

# Function to calculate RMS and dBFS
def calculate_loudness_and_dbfs(signal):
    rms = torch.sqrt(torch.mean(signal**2))
    dbfs = 20 * math.log10(rms.item()) if rms.item() > 0 else float('-inf')
    return rms.item(), dbfs

# Predict sentiment based on loudness
def predict_sentiment(rms, dbfs, low_dbfs=-30, high_dbfs=-20):
    sentiment = "Positive" if dbfs <= low_dbfs else "Neutral" if dbfs <= high_dbfs else "Negative"
    return sentiment


def group_audio_by_speaker(words, signal, sample_rate):
    """
    Groups audio segments by speaker ID using Deepgram's output.

    Args:
        words (list): List of word dictionaries from Deepgram transcription.
        signal (Tensor): Audio signal as a PyTorch tensor.
        sample_rate (int): Sampling rate of the audio.

    Returns:
        dict: Dictionary with speaker IDs as keys and their corresponding audio segments.
    """
    from collections import defaultdict

    speaker_audio = defaultdict(list)
    signal_numpy = signal.numpy().squeeze()

    for word in words:
        start_time = word['start']
        end_time = word['end']
        speaker_id = word['speaker']

        # Convert time to sample indices
        start_sample = int(start_time * sample_rate)
        end_sample = int(end_time * sample_rate)

        # Append audio segment to the speaker's list
        speaker_audio[speaker_id].extend(signal_numpy[start_sample:end_sample])

    # Convert lists back to tensors for processing
    return {speaker_id: torch.tensor(audio_data) for speaker_id, audio_data in speaker_audio.items()}



# def align_sentiment_with_transcription(transcription, sentiment_analysis):
#     """
#     Aligns sentiment analysis results with the speakers present in the transcription.
#
#     Args:
#         transcription (str): Transcription text with speaker annotations (e.g., "Speaker 0: Hello").
#         sentiment_analysis (list): List of sentiment analysis results, each containing speaker_id and sentiment.
#
#     Returns:
#         list: Filtered sentiment analysis results aligned with transcription speakers.
#     """
#     import re
#
#     # Step 1: Extract unique speaker IDs from transcription
#     speaker_ids = set()
#     for match in re.finditer(r"Speaker (\d+):", transcription):
#         speaker_ids.add(int(match.group(1)))
#
#     # Step 2: Filter sentiment analysis results
#     aligned_sentiments = [
#         sentiment for sentiment in sentiment_analysis if sentiment['speaker_id'] in speaker_ids
#     ]
#
#     return aligned_sentiments


def align_sentiment_with_transcription(transcription, sentiment_analysis, text_sentiments):
    """
    Aligns sentiment analysis results with the speakers present in the transcription and combines text and audio sentiment.

    Args:
        transcription (str): Transcription text with speaker annotations.
        sentiment_analysis (list): List of audio-based sentiment results.
        text_sentiments (list): List of text-based sentiment results.

    Returns:
        list: Sentiment analysis results including combined sentiment.
    """
    import re

    # Step 1: Extract unique speaker IDs from transcription
    speaker_ids = set()
    for match in re.finditer(r"Speaker (\d+):", transcription):
        speaker_ids.add(int(match.group(1)))

    # Step 2: Combine text and audio sentiment for each speaker
    combined_sentiments = []
    for sentiment in sentiment_analysis:
        speaker_id = sentiment['speaker_id']
        if speaker_id in speaker_ids:
            # Get corresponding text sentiment for this speaker
            text_sentiment = next(
                (s for s in text_sentiments if f"Speaker {speaker_id}:" in s[0]), None
            )
            text_score = text_sentiment[2] if text_sentiment else 0
            audio_score = {"Negative": -1, "Neutral": 0, "Positive": 1}[sentiment['audio_sentiment']]

            # Weighted combination (70% text, 30% audio)
            overall_score = 0.6 * text_score + 0.4 * audio_score
            combined_sentiment = (
                "Positive" if overall_score > 0.3 else
                "Negative" if overall_score < -0.3 else
                "Neutral"
            )

            # Add combined sentiment to the analysis
            combined_sentiments.append({
                **sentiment,
                "overall_sentiment": combined_sentiment,
                "text_sentiment": text_sentiment[1] if text_sentiment else "Neutral",
                # "overall_sentiment": combined_sentiment
            })

    return combined_sentiments
