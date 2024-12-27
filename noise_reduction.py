import noisereduce as nr
import torch


# Function to apply noise reduction
def reduce_noise(signal, sample_rate):
    """
    Apply noise reduction to the audio signal using spectral gating.
    """
    reduced_noise_signal = nr.reduce_noise(y=signal.numpy(), sr=sample_rate, prop_decrease=1.0)
    return torch.tensor(reduced_noise_signal)