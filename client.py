import socket
import threading
import pyaudio
import wave
import struct
import time

class Client:
    def __init__(self):
        # Initialize socket connection
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to the server
        while 1:
            try:
                self.target_ip = str(input("Enter target IP: ")) #"192.168.1.73"
                self.target_port = int(input("Enter target port: ")) #5000

                self.s.connect((self.target_ip, self.target_port))

                break
            except Exception as e:
                print(f"Couldn't connect to server: {e}")

        # Audio configuration
        chunk_size = 1024
        audio_format = pyaudio.paInt16
        channels = 1
        rate = 44100

        # Initialize PyAudio
        self.p = pyaudio.PyAudio()

        # Get a list of available input devices and prompt the user to choose one
        input_devices = self.get_audio_devices('input')
        selected_input_device = self.choose_audio_device(input_devices, "Select microphone input device") #1
        print("value of selected_input_device:", selected_input_device)

        # Get a list of available output devices and prompt the user to choose one
        output_devices = self.get_audio_devices('output')
        selected_output_device = self.choose_audio_device(output_devices, "Select speaker output device") #5
        print("value of selected_output_device:", selected_output_device)

        # Open streams for playing and recording with the selected devices
        self.playing_stream = self.p.open(
            format=self.p.get_format_from_width(2),
            channels=channels,
            rate=rate,
            output=True,
            frames_per_buffer=chunk_size,
            output_device_index=selected_output_device
        )

        self.recording_stream = self.p.open(
            format=audio_format,
            channels=channels,
            rate=rate,
            input=True,
            frames_per_buffer=chunk_size,
            input_device_index=selected_input_device
        )

        # Print connected message
        print("Connected to Server")

        # Start threads
        self.receive_thread = threading.Thread(target=self.receive_server_data)
        self.send_thread = threading.Thread(target=self.send_data_to_server)

        self.receive_thread.start()
        self.send_thread.start()

    def receive_server_data(self):
        while True:
            try:
                # Receive audio data from the server
                data = self.s.recv(1024)

                # Play the received audio data
                self.playing_stream.write(data)

                # Save received audio to a wave file (server_output.wav)
                frames = []
                frames.append(data)
                wf = wave.open("server_output.wav", 'wb')
                wf.setnchannels(1)
                wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
                wf.setframerate(44100)
                wf.writeframes(b''.join(frames))
                wf.close()

            except Exception as e:
                print(f"Error receiving data: {e}")
                break

    def send_data_to_server(self):
        while True:
            try:
                # Read audio data from the microphone and send it to the server
                data = self.recording_stream.read(1024)
                self.s.sendall(data)

            except Exception as e:
                print(f"Error sending data: {e}")
                break

    def get_audio_devices(self, kind='input'):
        # Get a list of available audio devices
        device_list = []
        for i in range(self.p.get_device_count()):
            device_info = self.p.get_device_info_by_index(i)
            if device_info['max%sChannels' % kind.capitalize()] > 0:
                device_list.append((i, device_info['name']))
        return device_list
    
    def choose_audio_device(self, devices, prompt):
        # Prompt the user to choose an audio device from the list
        print(prompt)
        for i, (index, name) in enumerate(devices):
            print(f"{i + 1}. {name}")
        selected_index = int(input("Enter the corresponding number: ")) - 1

        # Validate the selected device index
        if selected_index < 0 or selected_index >= len(devices):
            print("Invalid device index. Using default.")
            return None

        selected_device = devices[selected_index]
        print(f"Selected device: {selected_device[1]}")
        return selected_device[0]

# Create an instance of the Client class
client = Client()
