import os
import qbittorrentapi
import tkinter as tk
from tkinter import filedialog

def get_torrent_files(directory):
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.torrent')]

def main():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    directory = filedialog.askdirectory(title="Select the directory of torrent files")
    
    if not directory:
        print("No directory selected. Exiting.")
        return

    torrent_files = get_torrent_files(directory)

    qb = qbittorrentapi.Client(host='localhost', port=8080)
    qb.auth_log_in(username='yourusernamehere', password='yourpasswordhere!')

    print(f"Found {len(torrent_files)} torrent files in {directory}")

    for torrent_file in torrent_files:
        print(f"Adding torrent: {torrent_file}")
        qb.torrents_add(
            torrent_files=torrent_file,
            save_path='Savepath/to/data',
            is_paused=False,
            use_auto_torrent_management=False,
            tags='anytags here',
            upload_limit=-1,
            download_limit=-1,
            is_sequential_download=False,
            is_first_last_piece_priority=False,
            root_folder=True,
            rename=None,
            auto_tmm=False,
            temp_path='set this if you have a staging disk'
        )
        print(f"Successfully added: {torrent_file}")

if __name__ == "__main__":
    main()
