from os import path
from yt_dlp import YoutubeDL
from mutagen.id3 import ID3, TIT2, TPE1
from mutagen.flac import FLAC

class Downloader:
    def __init__(self, output_dir):
        self.output_dir = output_dir

    def download_audio(self, artist, song_name, url, preferred_format, selected_bitrate, amount_channels):
        filename = f"{artist} - {song_name}"
        ydl_opts = {
            'outtmpl': path.join(self.output_dir, filename),
            'extract_audio': True,
            'format': f'bestaudio/best[ext={preferred_format}]',
            'audio-format': preferred_format,            
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': preferred_format,
                'preferredquality': selected_bitrate,                
            }],
            'postprocessor_args': [                
                '-ac', str(amount_channels)            
            ],          
            'match_filter': filter_duration,            
        }

        result = ""        

        with YoutubeDL(ydl_opts) as ydl:
            result = ""
            if url:
                query = url
            else:
                query = f"ytsearch:{artist} {song_name} audio"
            try:
                ydl.download([query])
                result = "Download completed."
                self.add_metadata(filename, artist, song_name, preferred_format)
            except Exception as e:               
                result = f"Error while downloading\n {query}\n{e}"
        return result

    # Only works for mp3 and flac files
    def add_metadata(self, filename, artist, song_name, format):
        file_path = path.join(self.output_dir, filename + f'.{format}')
        if format == 'mp3':
            audiofile = ID3(file_path)
            audiofile['TIT2'] = TIT2(encoding=3, text=song_name)
            audiofile['TPE1'] = TPE1(encoding=3, text=artist)
            audiofile.save()  
        elif format == 'flac':
            audiofile = FLAC(file_path)
            audiofile['title'] = song_name
            audiofile['artist'] = artist
            audiofile.save()       


def filter_duration(info, *, incomplete):
    duration = info.get('duration')
    min_duration = 20  # 20 seconds
    max_duration = 2 * 60 * 60  # 2 hours

    if duration and duration < min_duration:
        return '[error]: Video too short'
    if duration and duration > max_duration:
        return '[error]: Video too long'
    
