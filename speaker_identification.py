import re

agent_keywords = {"sir", "loan", "payment", "details", "thankyou" , "धन्यवाद" }


# def identify_roles_by_keyword_introduction(transcription):
#     speaker_keywords = {}
#     keyword_introducer = {}
#
#     for line in transcription.split("\n"):
#         match = re.match(r"Speaker (\d+): (.+)", line)
#         if match:
#             speaker_id, text = int(match.group(1)), match.group(2).lower()
#
#             # Check for keyword introduction
#             for word in agent_keywords:
#                 if word in text and word not in keyword_introducer:
#                     keyword_introducer[word] = speaker_id
#
#     # Determine roles based on keyword introduction
#     likely_agent = max(set(keyword_introducer.values()), key=list(keyword_introducer.values()).count)
#     # return {speaker_id: "agent" if speaker_id == likely_agent else "customer" for speaker_id in {0, 1}}
#     return {speaker_id: "agent" if speaker_id == likely_agent else "customer" for speaker_id in
#             keyword_introducer.values()}


def identify_roles_by_keyword_introduction(transcription):
    speaker_keywords = {}
    keyword_introducer = {}

    for line in transcription.split("\n"):
        match = re.match(r"Speaker (\d+): (.+)", line)
        if match:
            speaker_id, text = int(match.group(1)), match.group(2).lower()

            # Check for keyword introduction
            for word in agent_keywords:
                if word in text and word not in keyword_introducer:
                    keyword_introducer[word] = speaker_id

    # Determine roles based on first keyword introduction
    if keyword_introducer:
        first_keyword_speaker = next(iter(keyword_introducer.values()))  # First speaker to introduce any keyword
        return {speaker_id: "agent" if speaker_id == first_keyword_speaker else "customer" for speaker_id in {0, 1}}

    # Fallback if no keywords are found
    return {}


def fallback_turn_taking_analysis(transcription):
    speaker_turns = {}
    for line in transcription.split("\n"):
        match = re.match(r"Speaker (\d+): (.+)", line)
        if match:
            speaker_id = int(match.group(1))
            speaker_turns[speaker_id] = speaker_turns.get(speaker_id, 0) + 1

    # The speaker with the first turn is likely the agent
    likely_agent = min(speaker_turns, key=speaker_turns.get)
    return {speaker_id: "agent" if speaker_id == likely_agent else "customer" for speaker_id in {0, 1}}


def identify_speaker_roles(transcription):
    # Try identifying roles using keyword introduction
    roles = identify_roles_by_keyword_introduction(transcription)

    # If roles are inconclusive, fall back to turn-taking analysis
    if len(set(roles.values())) < 2:
        roles = fallback_turn_taking_analysis(transcription)

    return roles
