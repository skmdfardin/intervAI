import ffmpeg
import sounddevice as sd
import numpy as np
import logging

def format_audio(audio_data, sample_rate=16000):
    try:
        audio_bytes = audio_data.tobytes()
        process = (
            ffmpeg
            .input('pipe:', format='f32le', acodec='pcm_f32le', ac=1, ar=sample_rate)
            .output('pipe:', format='s16le', acodec='pcm_s16le', ac=1, ar=16000)
            .run_async(pipe_stdin=True, pipe_stdout=True)
        )
        output_bytes = process.communicate(input=audio_bytes)[0]
        return np.frombuffer(output_bytes, dtype=np.int16)
    except Exception as e:
        logging.error(f"Audio formatting error: {e}")
        return None

def get_available_microphones():
    devices = sd.query_devices()
    input_devices = []
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            input_devices.append({
                'index': i,
                'name': device['name'],
                'channels': device['max_input_channels'],
                'sample_rate': device['default_samplerate'],
                'latency': {
                    'low': device['default_low_input_latency'],
                    'high': device['default_high_input_latency']
                }
            })
    return input_devices

def check_audio_quality(device_index):
    try:
        device_info = sd.query_devices(device_index, 'input')
        sample_rate = int(device_info['default_samplerate'])
        duration = 1
        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype='float32',
            device=device_index
        )
        sd.wait()
        
        signal_level = np.abs(recording).mean()
        noise_level = np.std(recording)
        snr = 20 * np.log10(signal_level/noise_level) if noise_level > 0 else 0
        
        return {
            'signal_level': float(signal_level),
            'noise_level': float(noise_level),
            'snr': float(snr),
            'clipping': bool(np.any(np.abs(recording) > 0.95))
        }
    except Exception as e:
        return {'error': str(e)}
