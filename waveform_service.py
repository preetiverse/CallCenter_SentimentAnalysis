from collections import defaultdict


def plot_waveforms_separately(signal, sample_rate, words):
    """
    Plot waveforms for the two speakers with the longest total duration on the same graph.
    """
    # Map of speaker IDs to their respective audio samples and total duration
    speaker_audio = defaultdict(list)
    speaker_durations = defaultdict(float)
    signal_numpy = signal.numpy().squeeze()  # Convert signal to NumPy array

    # Step 1: Group audio samples and calculate total duration for each speaker
    for word_info in words:
        start_time = word_info['start']  # Start time in seconds
        end_time = word_info['end']  # End time in seconds
        speaker_id = word_info['speaker']

        # Convert time to sample indices
        start_sample = int(start_time * sample_rate)
        end_sample = int(end_time * sample_rate)

        # Append the segment to the speaker's audio
        speaker_audio[speaker_id].extend(signal_numpy[start_sample:end_sample])

        # Update total duration for the speaker
        speaker_durations[speaker_id] += (end_time - start_time)

    # Step 2: Identify the two speakers with the longest total duration
    top_speakers = sorted(speaker_durations, key=speaker_durations.get, reverse=True)[:2]

    # # Step 3: Plot waveforms for the top 2 speakers on the same graph
    # colors = ['blue', 'orange']  # Colors for the two speakers
    # plt.figure(figsize=(6, 3))
    # for idx, speaker_id in enumerate(top_speakers):
    #     audio_data = speaker_audio[speaker_id]
    #     time = torch.arange(0, len(audio_data)) / sample_rate
    #     plt.plot(time, audio_data, color=colors[idx % len(colors)], linewidth=0.5, label=f"Speaker {speaker_id}")
    #
    # # Configure plot details
    # plt.title("Waveforms for Agent and customer")
    # plt.xlabel("Time (s)")
    # plt.ylabel("Amplitude")
    # plt.legend()
    # plt.grid(True)
    # plt.tight_layout()
    # plt.show()

    return {speaker_id: speaker_audio[speaker_id] for speaker_id in top_speakers}
