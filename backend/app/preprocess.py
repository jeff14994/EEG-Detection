import numpy as np
from scipy import signal
from scipy.signal import butter, filtfilt

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = filtfilt(b, a, data)
    return y

def preprocess_eeg_data(eeg_data):
    """
    Preprocess raw EEG data
    Args:
        eeg_data (dict): Raw EEG data from device
    Returns:
        dict: Preprocessed EEG data
    """
    if eeg_data is None:
        return None
        
    # Extract values from the data
    values = np.array([d['value'] for d in eeg_data['data']])
    fs = 256  # Sample rate
    
    # Bandpass filter (4-30 Hz)
    filtered_data = bandpass_filter(values, 4, 30, fs)
    
    # Normalize data
    normalized_data = (filtered_data - np.mean(filtered_data)) / np.std(filtered_data)
    
    return {
        "timestamp": eeg_data['timestamp'],
        "processed_data": normalized_data.tolist()
    }

def extract_features(processed_data):
    """
    Extract features from preprocessed EEG data
    Args:
        processed_data (dict): Preprocessed EEG data
    Returns:
        dict: Extracted features
    """
    if processed_data is None:
        return None
        
    data = np.array(processed_data['processed_data'])
    fs = 256  # Sample rate
    
    # Calculate power spectral density
    freqs, psd = signal.welch(data, fs, nperseg=1024)
    
    # Define frequency bands
    bands = {
        'delta': (0.5, 4),
        'theta': (4, 8),
        'alpha': (8, 13),
        'beta': (13, 30)
    }
    
    # Calculate band powers
    features = {}
    for band, (low, high) in bands.items():
        idx = np.logical_and(freqs >= low, freqs <= high)
        features[f'{band}_power'] = np.mean(psd[idx])
    
    return features 