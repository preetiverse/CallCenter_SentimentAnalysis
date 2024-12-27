from transformers import pipeline
import asyncio

# def perform_sentiment_analysis(transcript):
#     sentiment_model = pipeline('sentiment-analysis', model="cardiffnlp/twitter-xlm-roberta-base-sentiment")
#
#     sentences = transcript.split("\n")
#     sentence_sentiments = []
#     for sentence in sentences:
#         if sentence.strip():
#             sentiment = sentiment_model(sentence)
#             sentence_sentiments.append((sentence, sentiment[0]['label'], sentiment[0]['score']))
#
#     return sentence_sentiments


# Initialize sentiment model globally to avoid re-loading it every time
sentiment_model = pipeline('sentiment-analysis', model="cardiffnlp/twitter-xlm-roberta-base-sentiment")

async def analyze_sentiment(sentence):
    result = await asyncio.to_thread(sentiment_model, sentence)
    return sentence, result[0]['label'], result[0]['score']

async def perform_sentiment_analysis(transcript):
    sentences = transcript.split("\n")
    tasks = [analyze_sentiment(sentence) for sentence in sentences if sentence.strip()]
    sentence_sentiments = await asyncio.gather(*tasks)
    return sentence_sentiments

def compute_overall_sentiment(sentiments):
    sentiment_scores = {"POSITIVE": 1, "NEUTRAL": 0, "NEGATIVE": -1}

    # Ensure the sentiment label is in uppercase
    total_score = sum(sentiment_scores[label.upper()] * score for _, label, score in sentiments)

    avg_score = total_score / len(sentiments)

    if avg_score > 0.3:
        return "Positive"
    elif avg_score < -0.3:
        return "Negative"
    else:
        return "Neutral"