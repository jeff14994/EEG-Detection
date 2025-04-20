# EEG Signal Simulator

A real-time EEG (Electroencephalogram) simulation and visualization tool for brain activity data.

## Overview

This project provides a full-stack solution for simulating and visualizing EEG signals in real-time. It generates synthetic EEG data with realistic frequency components (alpha, beta, theta, and delta waves) and displays them both as time series and frequency spectra.

## Features

- Real-time EEG signal generation at 250 Hz sampling rate
- Visualization of 4 EEG channels (O1, O2, T3, T4)
- Time series display with 10-second scrolling window
- Frequency spectrum analysis using Discrete Fourier Transform
- WebSocket-based communication for real-time data streaming
- Responsive visualization with adjustable parameters
- Performance optimized for smooth real-time display

## Signal Components

The simulator generates synthetic EEG data with the following frequency components:

- **Alpha waves (8-13 Hz)**: Prominent in occipital channels (O1, O2)
- **Beta waves (13-30 Hz)**: Present in O2 and T4 channels
- **Theta waves (4-8 Hz)**: Present in O1 and T3 channels
- **Delta waves (0.5-4 Hz)**: Present in T3 and T4 channels

## Technical Architecture

- **Backend**: FastAPI with native WebSocket support
- **Frontend**: HTML/JavaScript with Chart.js for visualization
- **Data Processing**: Custom DFT implementation for spectral analysis
- **Communication**: WebSocket protocol for real-time data transmission

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd eeg_simulator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the server:
```bash
python -m uvicorn app.main:app --reload
```

2. Open your browser and navigate to:
```
http://localhost:8000
```

3. The visualization should start automatically, showing real-time EEG data.

## Configuration

You can adjust the following parameters in the code:

### Server (app/main.py)
- `SAMPLING_RATE`: Frequency of data generation (default: 250 Hz)
- Signal component amplitudes in the `generate_eeg_data()` function

### Client (test.html)
- `maxDataPoints`: Number of data points to display (default: 2500)
- `displaySeconds`: Time window width (default: 10 seconds)
- `fftWindowSize`: Window size for spectral analysis (default: 512 samples)

## Requirements

- Python 3.7+
- FastAPI
- Uvicorn
- WebSockets
- Modern web browser with JavaScript enabled

## License

[MIT License](LICENSE)

## Acknowledgements

This project is for educational and demonstration purposes only and should not be used for medical diagnosis. 