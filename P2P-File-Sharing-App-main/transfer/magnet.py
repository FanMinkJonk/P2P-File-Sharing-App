# magnet.py
import os
import json
import urllib.parse
import requests

def fetch_metadata_from_magnet(magnet_text, tracker_url):
    # Parse the magnet text using urllib.parse
    parsed = urllib.parse.urlparse(magnet_text)
    qs = urllib.parse.parse_qs(parsed.query)
    
    # Validate that 'xt' (the info hash) exists in the magnet text.
    if 'xt' not in qs:
        print("\nError: Magnet text does not contain an info hash ('xt').\n")
        return None
    xt = qs['xt'][0]
    if not xt.startswith("urn:btih:"):
        print("\nError: Invalid info hash in the magnet text.\n")
        return None
    
    # Extract the info hash from the magnet text
    info_hash = xt[9:]  # remove "urn:btih:" part

    # Contact the tracker to retrieve the metadata
    try:
        print(f"\nContacting tracker at {tracker_url}...\n")
        response = requests.get(f"{tracker_url}/get_metadata?hash={info_hash}")
        if response.status_code == 200:
            metadata = response.json()  # Tracker returns JSON metadata
            print("\nMetadata fetched successfully.\n")
            return metadata
        else:
            print(f"\nFailed to fetch metadata: {response.status_code} {response.reason}\n")
            return None
    except Exception as e:
        print(f"\nError connecting to tracker: {e}\n")
        return None

def download_file_from_metadata(metadata, seed_ip):
    try:
        filename = metadata.get("filename")
        pieces = metadata.get("pieces", [])
        destination_folder = "downloaded_files"
        seed_port = 22237  # Default upload server port
        
        # Create the destination folder if it doesn't exist.
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
        
        # Download each piece from the provided seed IP using the specified port.
        downloaded_pieces = []
        from transfer.download import download_piece  # Import function for piece download
        for piece in pieces:
            index = piece.get("index")
            print(f"Downloading piece {index} from {seed_ip}:{seed_port}...")
            piece_data = download_piece(seed_ip, seed_port, filename, index)
            downloaded_pieces.append((index, piece_data))
        
        # Sort pieces by index and write the combined data to the output file.
        downloaded_pieces.sort(key=lambda x: x[0])
        output_path = os.path.join(destination_folder, filename)
        with open(output_path, "wb") as outfile:
            for idx, data in downloaded_pieces:
                outfile.write(data)
        print(f"\nFile downloaded successfully via magnet text saved at: {output_path}\n")
    except Exception as e:
        print(f"\nError during file download: {e}\n")