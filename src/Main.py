import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

PATCH_BYTES = b"\x25\x63"

GAMES = {
    "Diamond": {
        "offset": 0x4DB0,
        "image": "diamond.png",
    },
    "Pearl": {
        "offset": 0x4DB0,
        "image": "pearl.png",
    },
    "Platinum": {
        "offset": 0x4DF8,
        "image": "platinum.png",
    },
    "HeartGold": {
        "offset": 0x4E28,
        "image": "heartgold.png",
    },
    "SoulSilver": {
        "offset": 0x4E28,
        "image": "soulsilver.png",
    },
}

def patch_rom(rom_path, offset):
    with open(rom_path, "rb+") as f:
        f.seek(offset)
        current = f.read(2)

        if current == PATCH_BYTES:
            messagebox.showinfo(
                "Already Patched",
                "This ROM already contains the correct bytes."
            )
            return

        f.seek(offset)
        f.write(PATCH_BYTES)

    messagebox.showinfo(
        "Success",
        "ROM patched successfully!"
    )

def select_and_patch(game_name):
    game = GAMES[game_name]

    rom_path = filedialog.askopenfilename(
        title=f"Select Pokémon {game_name} ROM",
        filetypes=[("Nintendo DS ROMs", "*.nds")]
    )

    if not rom_path:
        return

    if not os.path.isfile(rom_path):
        messagebox.showerror("Error", "Invalid ROM file.")
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