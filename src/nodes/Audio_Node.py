from nodes.Node import Node
from VALUES import v
from nodes.components.cButton import cButton
import numpy as np
import sounddevice as sd
from pydub import AudioSegment
from tkinter import filedialog
import cupy as cp



class Audio_Node(Node):
    # Frame parameters
    sample_size = 1024  # Number of further after every frame
    sample_buffer = 10000 #nomber of samples we gonna use

    #Visualization settings
    width, height = 400, 300  # Canvas dimensions
    num_bars = 50  # Number of bars
    bar_width = width // num_bars
    max_bar_height = height // 2
    sample_rate = None
    audio_data = None
    num_frames = None
    time_in_seconds = 0
    fps = 60
    current_frame = int(0)
    length = 0

    def __init__(self,window,canvas, rectangle):
        self.busy = False
        self.load_audio()
        self.frame = cp.zeros((self.height, self.width, 3), dtype=cp.uint8)

        # Assign the deep blue background using broadcasting
        self.frame[:, :] = cp.array([25, 25, 112], dtype=cp.uint8)

        # Initialize components
        self.components = [
            cButton(
            self, canvas, rectangle, command=self.generate_audio,args=None, text="open file select")
            #Scale(self),
            #Translate(self),
        ]

        # Call parent initializer
        super().__init__(window,canvas,"Audio Input", rectangle, anchor_option="LR")
        v.ACTIVE_AUDIO_NODE = self

    def generate_audio(self):
        self.update_visualizer()


    def image_operation(self,image, x_offset=0, y_offset=0):
        self.update_visualizer()
        return self.image, x_offset, y_offset


    def load_audio(self):
        # Load audio file
        audio_path = filedialog.askopenfilename(filetypes=[("Audio files", "*.wav;*.flac;*.mp3")])
        try:
            self.is_playing = False
            audio = AudioSegment.from_file(audio_path)
            self.sample_rate = audio.frame_rate

            # Convert audio to mono and resample to a common rate
            audio = audio.set_channels(1) # Convert to mono and set sample rate to 44.1 kHz

            # Convert audio data to NumPy array
            audio_data = np.array(audio.get_array_of_samples(), dtype=np.float32)
            # Normalize audio data to range [-1, 1]
            self.audio_data = audio_data / np.max(np.abs(audio_data))
            self.length = len(self.audio_data)

            time_in_seconds = self.length / self.sample_rate
            self.num_frames = time_in_seconds * v.FPS
            self.sample_size = self.length // self.num_frames
            print(self.sample_size)

        except Exception as e:
            print(f"Error loading audio file: {e}")

    def play_audio(self):
        if self.audio_data is None:
            print("No audio loaded to play.")
            return

        # Calculate the starting sample based on the current frame
        start_sample = int(v.CURRENT_FRAME * self.sample_size)
        if start_sample >= len(self.audio_data):
            print("No more audio to play.")
            return

        # Start playback from the calculated sample
        try:
            self.is_playing = True
            sd.play(self.audio_data[start_sample:], self.sample_rate, blocking=False)
            print(
                f"Audio playback started from frame {self.current_frame} ({start_sample / self.sample_rate:.2f} seconds).")
        except Exception as e:
            print(f"Error during audio playback: {e}")

    def pause_audio(self):
        if self.is_playing:
            try:
                # Stop playback and record the current playback position
                sd.stop()
                print(f"Audio paused")
            except Exception as e:
                print(f"Error during audio pause: {e}")

    def update_visualizer(self):
        if self.current_frame >= self.length:
            return

        # Get current audio frame
        start = int(v.CURRENT_FRAME * self.sample_size)
        start = max(0, start)
        end = int(start + self.sample_buffer)

        if end > self.length:
            return
        else:
            waveform = self.audio_data[start:end]

        # Convert waveform to CuPy array for GPU processing
        waveform_gpu = cp.asarray(waveform)

        # Compute FFT for frequency visualization
        fft_amplitude = cp.abs(cp.fft.rfft(waveform_gpu))
        # Handle zero-filled FFT
        if cp.max(fft_amplitude) > 0:
            fft_amplitude = fft_amplitude / cp.max(fft_amplitude)  # Normalize FFT
        else:
            fft_amplitude = cp.zeros_like(fft_amplitude)  # Keep it as zeros if max is 0

        # Generate the visualization frame
        self.image = self.generate_frame(fft_amplitude)

    def scale_factor(self, value, in_min, in_max, out_min, out_max):
        return (value - in_min) / (in_max - in_min) * (out_max - out_min) + out_min

    def generate_frame(self, fft_amplitude):
        # Create an empty black frame
        frame = cp.asarray(self.frame.copy())  # Convert frame to CuPy array
        number_frequencies = len(fft_amplitude)
        frequencies_per_bar = int(number_frequencies / self.num_bars)

        max_value = cp.max(fft_amplitude)
        avg_value = cp.mean(fft_amplitude)

        # Calculate bar heights
        bar_heights = []
        for index in range(0, number_frequencies, frequencies_per_bar):
            amplitude_bar = cp.max(fft_amplitude[index:index + frequencies_per_bar])
            bar_h = self.scale_factor(amplitude_bar, 0, max_value, 0, 1000)
            bar_heights.append(bar_h)

        bar_heights = cp.asarray(bar_heights)  # Convert to CuPy array

        # Draw bars on the frame
        white_color = cp.array([255, 255, 255], dtype=cp.uint8)  # Define white color as a CuPy array
        for i, bar_height in enumerate(bar_heights):
            x_start = i * self.bar_width
            y_start = self.height // 2
            y_end = int(y_start - bar_height)
            frame[y_end:y_start, x_start:x_start + self.bar_width - 2] = white_color  # Use CuPy array for color

        return frame



















