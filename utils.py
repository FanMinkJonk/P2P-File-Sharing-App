import os
import hashlib
import json

PIECE_SIZE = 512 * 1024  # 512 KB mặc định

# Chia file thành các mảnh và lưu vào thư mục 'pieces/'
def split_file_to_pieces(file_path, dest_folder="pieces"):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    pieces_info = []
    filename = os.path.basename(file_path)
    filesize = os.path.getsize(file_path)
    total_pieces = (filesize + PIECE_SIZE - 1) // PIECE_SIZE

    with open(file_path, 'rb') as f:
        for i in range(total_pieces):
            piece_data = f.read(PIECE_SIZE)
            piece_hash = hash_piece(piece_data)
            piece_filename = os.path.join(dest_folder, f"{filename}_piece_{i}")

            with open(piece_filename, 'wb') as pf:
                pf.write(piece_data)

            pieces_info.append({
                "index": i,
                "hash": piece_hash
            })

    return pieces_info, filesize

# Tính hash SHA-1 của mảnh dữ liệu
def hash_piece(data):
    return hashlib.sha1(data).hexdigest()

# Ghi metadata dạng .json (tương đương .torrent file)
def save_metadata(filename, filesize, pieces_info, owner_ip, owner_port, out_folder="metadata"):
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    for piece in pieces_info:
        piece["owner"] = f"{owner_ip}:{owner_port}"

    metadata = {
        "filename": filename,
        "size": filesize,
        "pieces": pieces_info
    }

    output_path = os.path.join(out_folder, filename + ".torrent.json")
    with open(output_path, 'w') as f:
        json.dump(metadata, f, indent=4)

    return output_path
