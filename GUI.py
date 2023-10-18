from os import makedirs
from threading import Thread
from tkinter import Entry, Label, Button, StringVar, ttk
from tkinter.ttk import Combobox
from idlelib.tooltip import Hovertip
from download import Downloader

class AudioDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.setup_variables()
        self.setup_ui()        
        self.create_widgets()
        self.configure_style()
        self.root.mainloop()

    def setup_ui(self):        
        self.root.title("YouTube Audio Downloader")
        app_size = str(self.app_width) + "x" + str(self.app_height) 
        self.root.geometry(app_size)
        self.style = ttk.Style()

    def setup_variables(self):
        self.output_dir = "Song downloads"
        self.advanced_options_visible = False

        self.format_options = ['mp3',  'wav', 'flac', 'vorbis', 'm4a', 'opus', 'aac', 'alac']
        self.predefined_bitrates = ['64', '128', '192', '256', '320']
        self.predefined_channels = ['Mono', 'Stereo']
        self.channel_mapping = {"Mono": 1, "Stereo": 2}

        makedirs(self.output_dir, exist_ok=True)
        self.downloader = Downloader(self.output_dir)

        self.app_width = 450
        self.app_height = 325        

    def create_widgets(self):
        self.create_url_entry()
        self.create_artist_and_song_name_entries()
        self.create_format_selection()
        self.create_download_button()
        self.create_advanced_options()        
        self.create_result_label()

    def create_url_entry(self):
        self.url_label = Label(self.root, text="YouTube URL:")
        self.url_label.pack()
        self.url_entry = Entry(self.root, width=50)
        self.url_entry.pack()
        self.url_entry.bind("<KeyRelease>", self.url_entry_change)

    def create_artist_and_song_name_entries(self):
        self.artist_label = Label(self.root, text="Artist:")
        self.artist_label.pack()
        self.artist_entry = Entry(self.root, width=50)
        self.artist_entry.pack()

        self.song_name_label = Label(self.root, text="Song Name:")
        self.song_name_label.pack()
        self.song_name_entry = Entry(self.root, width=50)
        self.song_name_entry.pack()

    def create_format_selection(self):
        self.format_label = Label(self.root, text="Preferred Format:", height=2)
        self.format_label.pack()
        self.format_var = StringVar()
        self.format_var.set(self.format_options[0])
        self.format_combobox = Combobox(self.root, textvariable=self.format_var, values=self.format_options)
        self.format_combobox.pack()
        self.format_tip = Hovertip(self.format_label, "aac and alac are packed within the .m4a file container.", hover_delay=500)
    
    def create_download_button(self):
        self.space_label = Label(self.root, text="", height=1)
        self.space_label.pack()
        self.download_button = Button(self.root, text="Download", command=self.download_button_click)
        self.download_button.pack()   

    def create_advanced_options(self):
        self.space_label2 = Label(self.root, text="", height=1)
        self.space_label2.pack()
        self.advanced_options_button = ttk.Label(self.root, text="Show advanced options: +", cursor="hand2")
        self.advanced_options_button.pack()
        self.advanced_options_button.bind("<Button-1>", self.toggle_advanced_options)
        
        self.advanced_options_frame = ttk.LabelFrame(self.root, text="Advanced Options:")

        self.create_bitrate_selection()
        self.create_audio_channels_selection()    
    
    def create_bitrate_selection(self):
        self.bitrate_label = Label(self.advanced_options_frame, text="Bitrate:")
        self.bitrate_label.pack()
        self.bitrate_var = StringVar()
        self.bitrate_var.set(self.predefined_bitrates[4])
        self.bitrate_combobox = Combobox(self.advanced_options_frame, textvariable=self.bitrate_var, values=self.predefined_bitrates)
        self.bitrate_combobox.pack()
        self.bitrate_tip = Hovertip(self.bitrate_label, "Only applies to mp3.", hover_delay=500)

    def create_audio_channels_selection(self):
        self.channels_label = Label(self.advanced_options_frame, text="Audio Channels:")
        self.channels_label.pack()
        self.channels_var = StringVar()
        self.channels_var.set(self.predefined_channels[1])
        self.channels_combobox = Combobox(self.advanced_options_frame, textvariable=self.channels_var, values=self.predefined_channels)
        self.channels_combobox.pack()

    def create_result_label(self):
        self.result_label = Label(self.root, text="Enter a YouTube URL or provide the artist and song name.")
        self.result_label.pack(side="bottom")

    def download_button_click(self):
        artist = self.artist_entry.get()
        song_name = self.song_name_entry.get()
        url = self.url_entry.get()        

        if not (artist and song_name) and not url:
            self.result_label.config(text="Please provide artist and song name or a YouTube URL.")
            return

        if not artist and not song_name:
            artist = "Unknown"
            song_name = "Unknown"

        preferred_format = self.format_var.get()
        selected_bitrate = self.bitrate_var.get()
        selected_channels = self.channels_var.get()
        selected_channels = self.channel_mapping[selected_channels]
        
        self.result_label.config(text="Downloading...")

        download_thread = Thread(target=self.download_audio_thread, args=(artist, song_name, url, preferred_format, selected_bitrate, selected_channels))
        download_thread.start()

    def download_audio_thread(self, artist, song_name, url, preferred_format, selected_bitrate, selected_channels):
        result = self.downloader.download_audio(artist, song_name, url, preferred_format, selected_bitrate, selected_channels)
        self.result_label.config(text=result)

    def url_entry_change(self, event):
        if self.url_entry.get():
            self.artist_entry.config(state="disabled")
            self.song_name_entry.config(state="disabled")
        else:
            self.artist_entry.config(state="normal")
            self.song_name_entry.config(state="normal")
        
    def toggle_advanced_options(self, event):
        self.advanced_options_visible = not self.advanced_options_visible        

        if self.advanced_options_visible:
            self.advanced_options_frame.pack()
            self.advanced_options_button.config(text="Hide Advanced Options: -")
            self.app_height += 100
        else:
            self.advanced_options_frame.pack_forget()
            self.advanced_options_button.config(text="Show Advanced Options: +")
            self.app_height -= 100
            
        app_size = str(self.app_width) + "x" + str(self.app_height)
        self.root.geometry(app_size)

    def configure_style(self):
        self.style.configure("TLabel", foreground="black", font=("Arial", 10, "bold"))


