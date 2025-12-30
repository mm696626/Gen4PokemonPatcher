import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import shutil

CHECK_BYTES = b"\x25\x63"
PATCH_BYTES = b"\x00\x00"

GAMES = {
    "Diamond": {
        "offset": 0x4DB0,
        "image": "diamond.png",
        "signature": b'POKEMON D\x00',
    },
    "Pearl": {
        "offset": 0x4DB0,
        "image": "pearl.png",
        "signature": b'POKEMON P\x00',
    },
    "Platinum": {
        "offset": 0x4DF8,
        "image": "platinum.png",
        "signature": b'POKEMON PL',
    },
    "HeartGold": {
        "offset": 0x4E28,
        "image": "heartgold.png",
        "signature": b'POKEMON HG',
    },
    "SoulSilver": {
        "offset": 0x4E28,
        "image": "soulsilver.png",
        "signature": b'POKEMON SS',
    },
}

def validate_rom(rom_path, expected_signature):
    try:
        with open(rom_path, "rb") as f:
            return f.read(len(expected_signature)) == expected_signature
    except Exception:
        return False

def patch_rom(rom_path, offset):
    with open(rom_path, "rb+") as f:
        f.seek(offset)
        current = f.read(2)

        if current == PATCH_BYTES:
            messagebox.showinfo(
                "Already Patched",
                "This ROM is already patched."
            )
            return

        if current != CHECK_BYTES:
            messagebox.showerror(
                "Unexpected Data",
                f"Expected bytes 25 63 at offset {hex(offset)}, "
                f"but found {current.hex(' ').upper()}.\n\n"
                "ROM was NOT modified."
            )
            return

        f.seek(offset)
        f.write(PATCH_BYTES)

    messagebox.showinfo(
        "Success",
        "ROM patched successfully!"
    )

def ask_backup(rom_path):
    choice = messagebox.askyesnocancel(
        "Create Backup?",
        "Would you like to create a backup before patching?\n\n"
        "A .bak file will be created in the same folder."
    )

    if choice is None:
        return False

    if choice is True:
        backup_path = rom_path + ".bak"
        try:
            shutil.copy2(rom_path, backup_path)
        except Exception as e:
            messagebox.showerror(
                "Backup Failed",
                f"Failed to create backup:\n{e}"
            )
            return False

    return True

def select_and_patch(game_name):
    game = GAMES[game_name]

    rom_path = filedialog.askopenfilename(
        title=f"Select Pokémon {game_name} ROM",
        filetypes=[("Nintendo DS ROMs", "*.nds")]
    )

    if not rom_path:
        return

    if not os.path.isfile(rom_path):
        messagebox.showerror("Error", "Invalid file.")
        return

    if not validate_rom(rom_path, game["signature"]):
        messagebox.showerror(
            "Invalid ROM",
            f"This ROM is not Pokémon {game_name}.\n\n"
            f"Expected header:\n{game['signature'].decode(errors='ignore')}"
        )
        return

    if not ask_backup(rom_path):
        return

    try:
        patch_rom(rom_path, game["offset"])
    except Exception as e:
        messagebox.showerror(
            "Error",
            f"Failed to patch ROM:\n{e}"
        )

def load_image(filename):
    try:
        img = Image.open(os.path.join("images", filename))
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Failed to load image {filename}: {e}")
        return None

root = tk.Tk()
root.title("Gen 4 Pokémon 60FPS Patcher")
root.resizable(False, False)

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

row = 0
col = 0
images = {}

for game_name, data in GAMES.items():
    img = load_image(data["image"])
    images[game_name] = img

    btn = tk.Button(
        frame,
        image=img,
        command=lambda g=game_name: select_and_patch(g)
    )
    btn.grid(row=row, column=col, padx=10, pady=10)

    col += 1
    if col == 3:
        col = 0
        row += 1

root.mainloop()