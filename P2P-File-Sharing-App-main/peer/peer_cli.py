import peer.peer_be as peer
import cmd
import os
import shutil
from transfer.download import download_file
import json
from transfer.magnet import fetch_metadata_from_magnet, download_file_from_metadata  # functions from magnet.py

class Peer_vt(cmd.Cmd):
    intro = "Welcome to the virtual terminal! Type 'help' to see a list of commands."
    prompt = "peer> "
    
    def __init__(self, mode):
        super().__init__()
        assert isinstance(mode, peer.Peer)
        self._peer = mode
     
    def do_help(self, arg):
        args = arg.split()
        if len(args) == 0:
            commands = {
                "connect": "connect to a tracker.",
                "exit": "exit terminal.",
                "list_peers": "display a list of connected peers.",
                "ping": "ping to a specific ip address.",
                "download <filename> <author-ip>": "download a specified file.",
                "upload <filename>": "upload a specified file.",
                "download torrent <file_name> <ip>": "download a file using torrent (metadata required).",
                "create torrent <file_name> <piece_size>": "create torrent metadata for a file.",
                "download magnet <magnet_link> <seed_ip>": "download a file using magnet text.",
                "magnet_text <magnet_text> <tracker_url> <seed_ip>": "fetch metadata from tracker and download file using magnet text.",
                "help <command>": "display the command syntax."
            }
            print()
            print("~~ Help menu ~~")
            for cmd, desc in commands.items():
                print(f"  {cmd:40} - {desc}")
            print()
            return

        if arg == "connect":
            print()
            print("connect <tracker-ip> <tracker-port>")
            print("<tracker-ip>: The ip address of the tracker.")
            print("<tracker-port>: The port of the tracker.")
            print()
        elif arg == "exit":
            print()
            print("exit")
            print("This command doesn't require any arguments.")
            print()
        elif arg == "list_peers":
            print()
            print("list_peers")
            print("This command doesn't require any arguments.")
            print()
        elif arg == "ping":
            print()
            print("ping <peer-index>")
            print("<peer-index>: The index of a peer in connected peers list.")
            print()
        elif arg == "download":
            print()
            print("download <file-name> <author-ip>")
            print("<file-name>: File to download.")
            print("<author-ip>: The ip address of the machine which uploads the file.")
            print()
        elif arg == "upload":
            print()
            print("upload <file-name>")
            print("<file-name>: File to upload.")
            print()
        elif arg == "download torrent":
            print()
            print("download torrent <file_name> <ip>")
            print("<file_name>: Name of the file to download (torrent metadata must exist).")
            print("<ip>: Seed peer IP address.")
            print()
        elif arg == "create torrent":
            print()
            print("create torrent <file_name> <piece_size>")
            print("<file_name>: File for which torrent metadata is to be created.")
            print("<piece_size>: Piece size in bytes (e.g., 524288 for 512KB).")
            print()
        elif arg == "download magnet":
            print()
            print("download magnet <magnet_link> <seed_ip>")
            print("<magnet_link>: Magnet text containing info hash and file display name.")
            print("<seed_ip>: The IP address of the seed peer.")
            print()
        elif arg == "magnet_text":
            print()
            print("magnet_text <magnet_text> <tracker_url> <seed_ip>")
            print("<magnet_text>: Magnet text that contains all necessary information (minimum: info hash).")
            print("<tracker_url>: The URL of your centralized tracker portal.")
            print("<seed_ip>: The IP address of the seed peer.")
            print()
    
    def do_connect(self, arg):
        #print("connect")
        args = arg.split()
        if len(args) != 2:
            print()
            print("Usage: connect <server ip> <server port>")
            print()
            return

        server_ip = args[0]
        server_port = int(args[1])

        print()
        try:
            print("Connecting to tracker")
            self._peer.connect_server(server_ip, server_port)
            print("Tracker connected")
        except Exception as e:
            print(f"Error connecting to tracker:{e}")
        print()

    def do_exit(self, arg):
        print()
        try:
            print("Exiting...")
            self._peer.exit()
        except Exception as e:
            print(f"Error while exiting: {e}")
        print()
        return True
    
    def do_list_peers(self, arg):
        print()
        try:
            if self._peer.is_connected:
                print("Retreiving connected peers")
                print()
                
                list_peers, list_peers_files = self._peer.get_list_peers()

                if len(list_peers) == 0:
                    print("There are no peer connected to that tracker!!!")
                    print()
                else:
                    print("Peer list:")
                    for i in range(len(list_peers)):
                        print(i+1, list_peers[i][0], ":", list_peers[i][1])
                        for p in list_peers_files:
                            if p["author"][0] == list_peers[i][0] and p["author"][1] == list_peers[i][1]:
                                print(f"  - File name: {p['file name']}, file size: {p['file size']}KB")
            else:
                print("This peer is not connected to any tracker")
        except Exception as e:
            print(f"Error retreiving connected peers list: {e}")
        
        print()
    
    def do_ping(self, arg):
        args = arg.split()
        if len(args) != 1:
            print("\nUsage: ping <peer-index>\n")
            return
        try:
            peer_index = int(args[0])
        except ValueError:
            print("\nError: peer-index must be an integer.\n")
            return
        try:
            result = self._peer.ping(peer_index)
            print(f"\nPing response from peer {peer_index}: {result}\n")
        except Exception as e:
            print(f"\nError pinging peer {peer_index}: {e}\n")
    
    def do_download(self, arg):
        args = arg.split()
        if len(args) != 2:
            print("\nUsage: download <filename> <author-ip>\n")
            return

        filename, author_ip = args
        destination_folder = "downloaded_files"  # Use only one folder here
        author_port = 22237  # Fixed port for file transfers

        print()
        try:
            file_path = download_file(author_ip, author_port, filename, destination_folder)
            print(f"Downloaded file saved at: {file_path}")
        except Exception as e:
            print(f"Error during file download:{e}")
        print()
    
    def do_upload(self, arg):
        args = arg.split()
        if len(args) != 1:
            print("\nUsage: upload <filepath>\n")
            return

        # Get the file path from input argument
        filepath = args[0]
        destination_folder = "shared_files"  # Folder where the upload server serves files
        
        print()
        try:
            if self._peer.upload(filepath, destination_folder):
                print(f"File '{filepath}' uploaded successfully to '{destination_folder}'.")
            else:
                print(f"File '{filepath}' has already been uploaded to tracker!")
        except Exception as e:
            print("Error during file upload:", e)
        
        print()

    # Preprocess commands: translate custom command strings into method calls.
    def precmd(self, line):
        # Translate "download torrent <file_name> <ip>" into "download_torrent <file_name> <ip>"
        if line.startswith("download torrent"):
            tokens = line.split()
            if len(tokens) >= 3:  # Expected: download torrent <file_name> <ip>
                new_line = "download_torrent " + " ".join(tokens[2:])
                return new_line
        # Translate "create torrent <file_name> <piece_size>" into "create_torrent <file_name> <piece_size>"
        if line.startswith("create torrent"):
            tokens = line.split()
            if len(tokens) >= 3:
                new_line = "create_torrent " + " ".join(tokens[2:])
                return new_line
        # Translate "download magnet <magnet_link> <seed_ip>" into "download_magnet <magnet_link> <seed_ip>"
        if line.startswith("download magnet"):
            tokens = line.split()
            if len(tokens) >= 3:
                new_line = "download_magnet " + " ".join(tokens[2:])
                return new_line
        # Translate "show magnet <file_name>" into "show_magnet <file_name>"
        if line.startswith("show magnet"):
            tokens = line.split()
            # If there are more tokens regarding the file name, append them.
            if len(tokens) >= 3:
                new_line = "show_magnet " + " ".join(tokens[2:])
                return new_line
            else:
                return "show_magnet"
        return line

    # -----------------------------------------------------------------------
    # Downloads a file using torrent metadata.
    # Usage: download torrent <file_name> <ip>
    def do_download_torrent(self, arg):
        args = arg.split()
        if len(args) != 2:
            print("\nUsage: download torrent <file_name> <ip>\n")
            return
        file_name, seed_ip = args
        destination_folder = "downloaded_files"
        metadata_file = os.path.join("metadata", f"{file_name}.torrent.json")
        
        if not os.path.exists(metadata_file):
            print(f"\nMetadata file '{metadata_file}' not found. Create torrent metadata first.\n")
            return
        
        try:
            with open(metadata_file, "r") as f:
                metadata = json.load(f)
            filename = metadata.get("filename")
            pieces = metadata.get("pieces", [])
            seed_port = 22237  # Default port for file transfers
            # Update the owner info for each piece with the provided seed IP and fixed port.
            for piece in pieces:
                piece["owner"] = f"{seed_ip}:{seed_port}"
            if not os.path.exists(destination_folder):
                os.makedirs(destination_folder)
            downloaded_pieces = []
            from transfer.download import download_piece  # Inline import for piece download
            for piece in pieces:
                index = piece.get("index")
                ip, port = piece["owner"].split(":")
                print(f"Downloading piece {index} from {ip}:{port}...")
                piece_data = download_piece(ip, int(port), filename, index)
                downloaded_pieces.append((index, piece_data))
            downloaded_pieces.sort(key=lambda x: x[0])
            output_path = os.path.join(destination_folder, filename)
            with open(output_path, "wb") as outfile:
                for idx, data in downloaded_pieces:
                    outfile.write(data)
            print(f"\nFile downloaded via torrent saved at: {output_path}\n")
        except Exception as e:
            print(f"\nError during torrent download: {e}\n")

    # Creates torrent metadata for a given file.
    # Usage: create torrent <file_name> <piece_size>
    def do_create_torrent(self, arg):
        args = arg.split()
        if len(args) != 2:
            print("\nUsage: create torrent <file_name> <piece_size>\n")
            return
        file_name, piece_size_str = args
        try:
            piece_size = int(piece_size_str)
        except ValueError:
            print("\nError: piece_size must be an integer.\n")
            return

        output_metadata = os.path.join("metadata", f"{os.path.basename(file_name)}.torrent.json")
        if not os.path.exists("metadata"):
            os.makedirs("metadata")
        
        try:
            file_path = file_name  # Assumes the file is in the current directory or provide full path.
            file_size = os.path.getsize(file_path)
            num_pieces = file_size // piece_size
            if file_size % piece_size != 0:
                num_pieces += 1
            pieces = [{"index": i} for i in range(num_pieces)]
            metadata = {
                "filename": os.path.basename(file_name),
                "piece_size": piece_size,
                "num_pieces": num_pieces,
                "pieces": pieces
            }
            with open(output_metadata, "w") as f:
                json.dump(metadata, f, indent=4)
            print(f"\nTorrent metadata successfully created at: {output_metadata}\n")
        except Exception as e:
            print(f"\nError during torrent metadata creation: {e}\n")

    # Downloads a file using a magnet link.
    # Usage: download magnet <magnet_link> <seed_ip>
    def do_download_magnet(self, arg):
        import urllib.parse
        args = arg.split()
        if len(args) != 2:
            print("\nUsage: download magnet <magnet_link> <seed_ip>\n")
            return
        magnet_link, seed_ip = args
        # Parse the magnet link
        parsed = urllib.parse.urlparse(magnet_link)
        qs = urllib.parse.parse_qs(parsed.query)
        if 'dn' not in qs:
            print("\nError: Magnet link does not contain a display name ('dn').\n")
            return
        file_name = qs['dn'][0]
        if 'xt' not in qs:
            print("\nError: Magnet link does not contain an info hash ('xt').\n")
            return
        xt = qs['xt'][0]
        if not xt.startswith("urn:btih:"):
            print("\nError: The 'xt' value in the magnet link is invalid.\n")
            return
        info_hash = xt[9:]
        print(f"\nParsed magnet link: file name = {file_name}, info hash = {info_hash}\n")
        
        metadata_file = os.path.join("metadata", f"{file_name}.torrent.json")
        if not os.path.exists(metadata_file):
            print(f"\nMetadata file '{metadata_file}' not found. Create torrent metadata first.\n")
            return
        
        command = f"{file_name} {seed_ip}"
        self.do_download_torrent(command)

    # Fetches metadata from a tracker using magnet text and downloads the file.
    # Usage: magnet_text <magnet_text> <tracker_url> <seed_ip>
    def do_magnet_text(self, arg):
        args = arg.split()
        if len(args) != 3:
            print("\nUsage: magnet_text <magnet_text> <tracker_url> <seed_ip>\n")
            return
        magnet_text, tracker_url, seed_ip = args
        # Fetch metadata using the magnet text by contacting the tracker.
        metadata = fetch_metadata_from_magnet(magnet_text, tracker_url)
        if metadata is None:
            print("\nFailed to retrieve metadata from tracker.\n")
            return
        # Use the fetched metadata to download the file.
        download_file_from_metadata(metadata, seed_ip)
    
    # Displays the magnet link for a given file based on its torrent metadata.
    # Usage: show magnet <file_name>
    def do_show_magnet(self, arg):
        args = arg.split()
        if len(args) != 1:
            print("\nUsage: show magnet <file_name>\n")
            return
        file_name = args[0]
        metadata_file = os.path.join("metadata", f"{file_name}.torrent.json")
        if not os.path.exists(metadata_file):
            print(f"\nMetadata file '{metadata_file}' not found. Create torrent metadata first.\n")
            return
        try:
            with open(metadata_file, "r") as f:
                metadata = json.load(f)
            # Compute the info hash from a subset of metadata:
            # We use the keys: 'filename', 'piece_size', 'num_pieces', 'pieces'
            import hashlib
            info_dict = {k: metadata[k] for k in ("filename", "piece_size", "num_pieces", "pieces") if k in metadata}
            info_str = json.dumps(info_dict, sort_keys=True)
            info_hash = hashlib.sha1(info_str.encode('utf-8')).hexdigest().upper()
            magnet_link = f"magnet:?xt=urn:btih:{info_hash}&dn={metadata.get('filename')}"
            print(f"\nMagnet link for file '{file_name}':")
            print(magnet_link)
        except Exception as e:
            print(f"\nError generating magnet link: {e}\n")    # This method displays the magnet link for a given file based on its torrent metadata.
    
    def do_show_magnet(self, arg):
        args = arg.split()
        if len(args) != 1:
            print("\nUsage: show magnet <file_name>\n")
            return
        file_name = args[0]
        metadata_file = os.path.join("metadata", f"{file_name}.torrent.json")
        if not os.path.exists(metadata_file):
            print(f"\nMetadata file '{metadata_file}' not found. Create torrent metadata first.\n")
            return
        try:
            with open(metadata_file, "r") as f:
                metadata = json.load(f)
            # Compute the info hash using a subset of metadata fields.
            import hashlib
            info_dict = {k: metadata[k] for k in ("filename", "piece_size", "num_pieces", "pieces") if k in metadata}
            info_str = json.dumps(info_dict, sort_keys=True)
            info_hash = hashlib.sha1(info_str.encode('utf-8')).hexdigest().upper()
            magnet_link = f"magnet:?xt=urn:btih:{info_hash}&dn={metadata.get('filename')}"
            print(f"\nMagnet link for file '{file_name}':")
            print(magnet_link)
        except Exception as e:
            print(f"\nError generating magnet link: {e}\n")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="P2P Virtual Terminal")
    parser.add_argument("--mode", type=str, default="peer", help="Mode to run (peer)")
    args = parser.parse_args()

    p = peer.Peer()
    cli = Peer_vt(p)
    cli.cmdloop()