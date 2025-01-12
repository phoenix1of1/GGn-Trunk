import os
import re
import shutil
import subprocess
import tkinter as tk
from tkinter import filedialog, simpledialog
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from wcwidth import wcswidth

LOWERCASE_WORDS = ['a', 'an', 'the', 'and', 'but', 'or', 'nor', 'for', 'yet', 'so', 'as', 'at', 'by', 'in', 'of', 'on', 'to', 'vs.', 'v.', 'etc.', 'from', 'it']
ALWAYS_CAPITALIZE = []  # Add words here that should always be capitalized

def capitalize_title(title):
    def capitalize_word(word, is_first_or_last):
        if word.lower() in ALWAYS_CAPITALIZE or is_first_or_last:
            return word.capitalize()
        elif word.lower() in LOWERCASE_WORDS:
            return word.lower()
        else:
            return word.capitalize()

    def capitalize_phrase(phrase):
        words = phrase.split()
        capitalized_words = [
            capitalize_word(word, i == 0 or i == len(words) - 1)
            for i, word in enumerate(words)
        ]
        return ' '.join(capitalized_words)

    # Ensure there is a dash before any parenthesis if it is not already present
    title = re.sub(r'(\S)(\()', r'\1 - \2', title)
    print(f"Title after adding dash before parenthesis: {title}")  # Debug print

    # Split the title into parts outside and inside parentheses
    parts = re.split(r'(\(.*?\))', title)
    print(f"Parts after split: {parts}")  # Debug print
    capitalized_parts = [capitalize_phrase(part) if not part.startswith('(') else capitalize_phrase(part[1:-1]).join(['(', ')']) for part in parts]
    final_title = ''.join(capitalized_parts)
    print(f"Final capitalized title: {final_title}")  # Debug print
    return final_title

def prompt_user_for_capitalization(track_title):
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    response = simpledialog.askstring("Track Title Capitalization", f"Do you want to apply capitalization rules to the track title '{track_title}'? (yes/no)")
    return response.lower() == 'yes'

def get_audio_metadata(file_path):
    audio = MP3(file_path, ID3=EasyID3) if file_path.lower().endswith('.mp3') else FLAC(file_path) if file_path.lower().endswith('.flac') else None
    if not audio:
        return None

    track_number = audio.get('tracknumber', ['Unknown Track Number'])[0].split('/')[0]
    track_title = audio.get('title', ['Unknown Title'])[0]
    artists = audio.get('artist', ['Unknown Artist'])
    length = int(audio.info.length)
    minutes, seconds = divmod(length, 60)
    track_length = f"{minutes}:{seconds:02}"
    
    return track_number, track_title, artists, track_length

def get_flac_bit_depth(file_path):
    result = subprocess.run(['ffmpeg', '-i', file_path], stderr=subprocess.PIPE, text=True, encoding='utf-8')
    for line in result.stderr.split('\n'):
        if 'Stream #0:0' in line and 'Audio:' in line:
            if 's16' in line:
                return '16bit'
            elif 's24' in line or 's32' in line:
                return '24bit'
    return 'Unknown'

def get_mp3_bitrate(file_path):
    result = subprocess.run(['ffmpeg', '-i', file_path], stderr=subprocess.PIPE, text=True, encoding='utf-8')
    for line in result.stderr.split('\n'):
        if 'Stream #0:0' in line and 'Audio:' in line:
            if '320 kb/s' in line:
                return 'mp3 320kbps CBR'
            elif 'VBR' in line:
                return 'mp3 V0 VBR'
    return 'Unknown'

def create_folder_name(artist_name, album_name, year, format_info):
    return f"{artist_name} - {album_name} ({year}) ({format_info})"

def copy_images_folder(src_directory, dest_directories):
    images_folder_path = os.path.join(src_directory, "Images")
    if os.path.exists(images_folder_path) and os.path.isdir(images_folder_path):
        for dest_directory in dest_directories:
            dest_images_folder_path = os.path.join(dest_directory, "Images")
            if not os.path.exists(dest_images_folder_path):
                shutil.copytree(images_folder_path, dest_images_folder_path)
                print(f"Copied 'Images' folder to {dest_directory}")

def calc_display_width(text):
    return wcswidth(text)

def pad_text(text, width):
    current_width = calc_display_width(text)
    padding = width - current_width
    return text + ' ' * padding

def rename_files_in_directory(directory):
    # Scan for and delete "khinsider.info.txt"
    khinsider_info_path = os.path.join(directory, "khinsider.info.txt")
    if os.path.exists(khinsider_info_path):
        os.remove(khinsider_info_path)
        print('Deleted "khinsider.info.txt"')

    track_list = []
    all_artists = set()
    bit_depth = 'Unknown'
    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)) and (filename.lower().endswith('.mp3') or filename.lower().endswith('.flac')):
            match = re.match(r'^(\d+)[\.\- ]? (.+)\.(mp3|flac)$', filename)
            if not match:
                print(f"Skipping file with unexpected format: {filename}")
                continue
            track_number, track_title, extension = match.groups()
            print(f"Original track title: {track_title}")  # Debug print

            # Check for multiple periods and prompt user for capitalization
            if re.search(r'\.\w\.', track_title):
                if prompt_user_for_capitalization(track_title):
                    new_track_title = capitalize_title(track_title)
                else:
                    new_track_title = track_title
            else:
                new_track_title = capitalize_title(track_title)
            print(f"New track title: {new_track_title}")  # Debug print

            # Ensure there is a dash before any parenthesis in the new track title
            new_track_title = re.sub(r'(\S)(\()', r'\1 - \2', new_track_title)

            file_path = os.path.join(directory, filename)
            audio = MP3(file_path, ID3=EasyID3) if extension.lower() == 'mp3' else FLAC(file_path)
            if extension.lower() == 'mp3':
                bitrate = get_mp3_bitrate(file_path)
            elif extension.lower() == 'flac' and bit_depth == 'Unknown':
                bit_depth = get_flac_bit_depth(file_path)

            audio['title'] = new_track_title
            audio.save()

            artists = audio.get('artist', ['Unknown Artist'])
            all_artists.update(artists)
            artist = ', '.join(artists)
            print(f"Collected artists for {filename}: {artist}")  # Debug print

            # Check the number of unique artists before renaming the file
            if len(all_artists) > 1:
                new_filename = f"{track_number}. {artist} - {new_track_title}.{extension}"
            else:
                new_filename = f"{track_number}. {artist} - {new_track_title}.{extension}"
            print(f'Renaming "{filename}" to "{new_filename}"')
            os.rename(file_path, os.path.join(directory, new_filename))

            track_number, track_title, artists, track_length = get_audio_metadata(os.path.join(directory, new_filename))
            track_list.append((track_number, new_filename, artists, track_length))

    if not track_list:
        print("No valid audio files found in the directory.")
        return

    single_artist = len(all_artists) == 1
    artist_name = list(all_artists)[0] if single_artist else "Various Artists"

    parent_dir = os.path.dirname(directory)

    with open(os.path.join(parent_dir, 'track_list.txt'), 'w', encoding='utf-8') as f:
        for track in track_list:
            track_number, new_filename, artists, track_length = track
            if single_artist:
                f.write(f"{track_number} - {new_filename} - {track_length}\n")
            else:
                artist = ', '.join(artists)
                f.write(f"{track_number} - {artist} - {new_filename} - {track_length}\n")

    longest_track_number = max(calc_display_width(track[0]) for track in track_list)
    longest_track_title = max(calc_display_width(track[1]) for track in track_list)
    longest_track_length = max(calc_display_width(track[3]) for track in track_list)

    with open(os.path.join(parent_dir, 'track_list_bbcode.txt'), 'w', encoding='utf-8') as f:
        f.write("[align=center][pre]\nTrack List\n")
        for track in track_list:
            track_number, new_filename, artists, track_length = track
            if single_artist:
                line = f"{pad_text(track_number, longest_track_number)}  {pad_text(new_filename, longest_track_title)}  {pad_text(track_length, longest_track_length)}"
            else:
                artist = ', '.join(artists)
                line = f"{pad_text(track_number, longest_track_number)}  {pad_text(artist, longest_track_title)}  {pad_text(new_filename, longest_track_title)}  {pad_text(track_length, longest_track_length)}"
            print(f"Writing to BBCode file: {line}")  # Debug print
            f.write(f"{line}\n")
        f.write("[/pre][/align]")

    folder_name = os.path.basename(directory)

    format_info = "Unknown"
    for filename in os.listdir(directory):
        if filename.lower().endswith('.mp3'):
            format_info = get_mp3_bitrate(os.path.join(directory, filename))
            break
        elif filename.lower().endswith('.flac'):
            bit_depth = get_flac_bit_depth(os.path.join(directory, filename))
            format_info = f"FLAC {bit_depth}"
            break

    try:
        if folder_name.count('(') == 1 and folder_name.count(')') == 1:
            album_name, year = folder_name.rsplit('(', 1)
            year = year.strip(') ')
        else:
            album_name, year, _ = folder_name.rsplit('(', 2)
            album_name = album_name.strip()
            year = year.strip(') ')
    except ValueError:
        print(f"Error: The folder name '{folder_name}' does not follow the expected format '<artist> - <album title> (year) (format)'.")
        return

    if artist_name not in folder_name:
        new_folder_name = create_folder_name(artist_name, album_name, year, format_info)
    else:
        new_folder_name = f"{album_name} ({year}) ({format_info})"

    new_folder_path = os.path.join(parent_dir, new_folder_name)
    os.rename(directory, new_folder_path)
    print(f"Renamed folder to: {new_folder_name}")

    directory = new_folder_path

    new_directories = []

    contains_mp3_320 = any("320 kb/s" in get_mp3_bitrate(os.path.join(directory, f)) for f in os.listdir(directory) if f.lower().endswith('.mp3'))
    contains_mp3_v0 = any("V0 VBR" in get_mp3_bitrate(os.path.join(directory, f)) for f in os.listdir(directory) if f.lower().endswith('.mp3'))

    if "FLAC" in format_info or not contains_mp3_320:
        mp3_320_folder_name = f"{album_name} ({year}) (mp3 320kbps CBR)" if artist_name in folder_name else create_folder_name(artist_name, album_name, year, "mp3 320kbps CBR")
        mp3_320_folder_path = os.path.join(parent_dir, mp3_320_folder_name)
        if not os.path.exists(mp3_320_folder_path):
            os.makedirs(mp3_320_folder_path, exist_ok=True)
            print(f"Created folder: {mp3_320_folder_name}")
            new_directories.append(mp3_320_folder_path)
        else:
            print(f"Skipped creating folder: {mp3_320_folder_name} (already exists)")

    if "FLAC" in format_info or not contains_mp3_v0:
        mp3_v0_folder_name = f"{album_name} ({year}) (mp3 V0 VBR)" if artist_name in folder_name else create_folder_name(artist_name, album_name, year, "mp3 V0 VBR")
        mp3_v0_folder_path = os.path.join(parent_dir, mp3_v0_folder_name)
        if not os.path.exists(mp3_v0_folder_path):
            os.makedirs(mp3_v0_folder_path, exist_ok=True)
            print(f"Created folder: {mp3_v0_folder_name}")
            new_directories.append(mp3_v0_folder_path)
        else:
            print(f"Skipped creating folder: {mp3_v0_folder_name} (already exists)")

    if "FLAC 24bit" in format_info:
        flac_16_folder_name = f"{album_name} ({year}) (FLAC 16bit)" if artist_name in folder_name else create_folder_name(artist_name, album_name, year, "FLAC 16bit")
        flac_16_folder_path = os.path.join(parent_dir, flac_16_folder_name)
        if not os.path.exists(flac_16_folder_path):
            os.makedirs(flac_16_folder_path, exist_ok=True)
            print(f"Created folder: {flac_16_folder_name}")
            new_directories.append(flac_16_folder_path)
        else:
            print(f"Skipped creating folder: {flac_16_folder_name} (already exists)")

    copy_images_folder(directory, new_directories)

def select_directory(prompt):
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    directory = filedialog.askdirectory(title=prompt, initialdir="L:\\Uploads")
    return directory

if __name__ == "__main__":
    directory_to_check = select_directory("Select the directory containing audio files")
    if directory_to_check:
        rename_files_in_directory(directory_to_check)
    else:
        print("No directory selected.")
