import re

def group_sentences_by_speaker(response):
    try:
        words = response['results']['channels'][0]['alternatives'][0]['words']
        speaker_dialogues = []
        current_sentence = ""
        current_speaker = None

        for word_info in words:
            speaker_id = word_info['speaker']
            word = word_info['punctuated_word']

            if re.search(r'[.!?]', word):  # Check if the word ends a sentence (punctuation)
                current_sentence += " " + word
                speaker_dialogues.append((current_speaker, current_sentence.strip()))
                current_sentence = ""  # Reset sentence after punctuation
            else:
                current_sentence += " " + word

            if current_speaker is None or current_speaker != speaker_id:
                current_speaker = speaker_id  # Switch to a new speaker when speaker_id changes

        # Format the dialogues into alternating speaker format
        formatted_dialogue = []
        speaker_toggle = 0  # Start with Speaker 0

        for speaker, sentence in speaker_dialogues:
            if speaker_toggle == 0:
                formatted_dialogue.append(f"Speaker 0: {sentence}")
                speaker_toggle = 1  # Alternate to Speaker 1
            else:
                formatted_dialogue.append(f"Speaker 1: {sentence}")
                speaker_toggle = 0  # Alternate to Speaker 0

        return "\n".join(formatted_dialogue)

    except KeyError:
        return "Error: Unable to extract speaker information or words from the response."


