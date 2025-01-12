import os
import subprocess
import tkinter as tk
from tkinter import filedialog
from concurrent.futures import ThreadPoolExecutor

def select_directory(prompt):
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    directory = filedialog.askdirectory(title=prompt, initialdir='your initial directory here')
    return directory

def convert_file(input_file, output_file_v0, output_file_320, output_file_flac_16bit=None):
    try:
        # Convert to MP3 V0
        subprocess.run(['ffmpeg', '-i', input_file, '-q:a', '0', output_file_v0], check=True)
        print(f"Converted to MP3 V0: {output_file_v0}")

        # Convert to MP3 320kbps
        subprocess.run(['ffmpeg', '-i', input_file, '-b:a', '320k', output_file_320], check=True)
        print(f"Converted to MP3 320kbps: {output_file_320}")

        # Convert to FLAC 16bit if output directory is specified
        if output_file_flac_16bit:
            subprocess.run(['ffmpeg', '-i', input_file, '-sample_fmt', 's16', output_file_flac_16bit], check=True)
            print(f"Converted to FLAC 16bit: {output_file_flac_16bit}")

    except subprocess.CalledProcessError as e:
        print(f"Error converting file {input_file}: {e}")

def convert_flac_to_mp3(input_dir, output_dir_v0, output_dir_320, output_dir_flac_16bit=None):
    os.makedirs(output_dir_v0, exist_ok=True)
    os.makedirs(output_dir_320, exist_ok=True)
    if output_dir_flac_16bit:
        os.makedirs(output_dir_flac_16bit, exist_ok=True)
    
    with ThreadPoolExecutor() as executor:
        futures = []
        for file in os.listdir(input_dir):
            if file.endswith(".flac"):
                input_file = os.path.join(input_dir, file)
                base_name = os.path.splitext(file)[0]
                
                # Output file paths
                output_file_v0 = os.path.join(output_dir_v0, f"{base_name}.mp3")
                output_file_320 = os.path.join(output_dir_320, f"{base_name}.mp3")
                output_file_flac_16bit = os.path.join(output_dir_flac_16bit, f"{base_name}.flac") if output_dir_flac_16bit else None
                
                # Submit the conversion task to the executor
                futures.append(executor.submit(convert_file, input_file, output_file_v0, output_file_320, output_file_flac_16bit))
        
        # Wait for all futures to complete
        for future in futures:
            future.result()

if __name__ == "__main__":
    input_directory = select_directory("Select the directory containing FLAC files")
    output_directory_v0 = select_directory("Select the directory to save V0 MP3 files")
    output_directory_320 = select_directory("Select the directory to save 320kbps MP3 files")
    output_directory_flac_16bit = select_directory("Select the directory to save FLAC 16bit files (optional)")

    if not output_directory_flac_16bit:
        print("No directory selected for FLAC 16bit files. Skipping FLAC 16bit conversion.")

    convert_flac_to_mp3(input_directory, output_directory_v0, output_directory_320, output_directory_flac_16bit)
