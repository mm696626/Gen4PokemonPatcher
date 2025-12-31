import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import shutil
import hashlib

CHECK_BYTES = b"\x25\x63"
PATCH_BYTES = b"\x00\x00"

GAMES = {
    "Diamond": {
        "fps_offset": 0x4DB0,
        "shiny_offset": 0x6CAC4,
        "image": "diamond.png",
        "signature": b'POKEMON D\x00',
    },
    "Pearl": {
        "fps_offset": 0x4DB0,
        "shiny_offset": 0x6CAC4,
        "image": "pearl.png",
        "signature": b'POKEMON P\x00',
    },
    "Platinum": {
        "fps_offset": 0x4DF8,
        "shiny_offset": 0x79E50,
        "image": "platinum.png",
        "signature": b'POKEMON PL',
    },
    "HeartGold": {
        "fps_offset": 0x4E28,
        "shiny_offset": 0x559AA,
        "image": "heartgold.png",
        "signature": b'POKEMON HG',
    },
    "SoulSilver": {
        "fps_offset": 0x4E28,
        "shiny_offset": 0x559AC,
        "image": "soulsilver.png",
        "signature": b'POKEMON SS',
    },
}

EXPECTED_MD5 = {
    "Diamond": "02a1af2a677d101394b1d99164a8c249",
    "Pearl": "e5da92c8cfabedd0d037ff33a2f2b6ba",
    "Platinum": "ab828b0d13f09469a71460a34d0de51b",
    "HeartGold": "258cea3a62ac0d6eb04b5a0fd764d788",
    "SoulSilver": "8a6c8888bed9e1dce952f840351b73f2",
}

EXPECTED_SIZES = {
    "Diamond": 67108864,
    "Pearl": 67108864,
    "Platinum": 134217728,
    "HeartGold": 134217728,
    "SoulSilver": 134217728,
}

def validate_rom(rom_path, expected_signature):
    try:
        with open(rom_path, "rb") as f:
            return f.read(len(expected_signature)) == expected_signature
    except Exception:
        return False

def check_md5(rom_path, game_name):
    md5_hash = hashlib.md5()
    try:
        with open(rom_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
    except Exception:
        return False

    rom_md5 = md5_hash.hexdigest()
    return rom_md5.lower() == EXPECTED_MD5[game_name].lower()

def check_rom_size(rom_path, game_name):
    try:
        size = os.path.getsize(rom_path)
        expected = EXPECTED_SIZES[game_name]
        return size == expected
    except Exception:
        return False

def patch_60fps(rom_path, offset):
    with open(rom_path, "rb+") as f:
        f.seek(offset)
        current = f.read(2)

        if current == PATCH_BYTES:
            return "already"

        if current != CHECK_BYTES:
            raise ValueError(
                f"Expected 25 63 at {hex(offset)}, got {current.hex(' ')}"
            )

        f.seek(offset)
        f.write(PATCH_BYTES)

    return "patched"

def patch_shiny_rate(rom_path, offset, value):
    with open(rom_path, "rb+") as f:
        f.seek(offset)
        f.write(bytes([value]))

def ask_backup(rom_path):
    choice = messagebox.askyesnocancel(
        "Create Backup?",
        "Would you like to create a backup before patching?"
    )

    if choice is None:
        return False

    if choice:
        try:
            shutil.copy2(rom_path, rom_path + ".bak")
        except Exception as e:
            messagebox.showerror("Backup Failed", str(e))
            return False

    return True

def start_patch(game_name, do_fps, do_shiny, shiny_value):
    game = GAMES[game_name]

    rom_path = filedialog.askopenfilename(
        title=f"Select Pokémon {game_name} ROM",
        filetypes=[("Nintendo DS ROMs", "*.nds")]
    )

    if not rom_path:
        return

    if not validate_rom(rom_path, game["signature"]):
        messagebox.showerror("Invalid ROM", f"Not Pokémon {game_name}")
        return

    if not check_md5(rom_path, game_name):
        messagebox.showerror("MD5 Mismatch", "ROM does not match known MD5 hash!")
        return

    if not check_rom_size(rom_path, game_name):
        messagebox.showerror("Invalid ROM Size", f"{game_name} ROM size does not match expected value!")
        return

    if not ask_backup(rom_path):
        return

    try:
        messages = []

        if do_fps:
            result = patch_60fps(rom_path, game["fps_offset"])
            messages.append(
                "60 FPS patch: " +
                ("already applied" if result == "already" else "patched")
            )

        if do_shiny:
            patch_shiny_rate(rom_path, game["shiny_offset"], shiny_value)
            messages.append(f"Shiny rate value written: {shiny_value}")

        messagebox.showinfo("Success", "\n".join(messages))

    except Exception as e:
        messagebox.showerror("Error", str(e))

def open_options(game_name):
    win = tk.Toplevel(root)
    win.title(f"{game_name} Patch Options")
    win.resizable(False, False)

    fps_var = tk.BooleanVar(value=True)
    shiny_var = tk.BooleanVar(value=False)
    shiny_value = tk.IntVar(value=8)

    def update_display(*_):
        val = shiny_value.get()
        denom = 65536

        if val == 0:
            approx = "0"
        else:
            approx_den = round(denom / val)
            approx = f"1/{approx_den}"

        percent = (val / denom) * 100

        display_label.config(
            text=(
                f"Shiny Odds: {approx}\n"
                f"≈ {percent:.4f}%"
            )
        )

    def toggle_slider():
        state = "normal" if shiny_var.get() else "disabled"
        slider.config(state=state)
        display_label.config(state=state)

    tk.Checkbutton(
        win,
        text="Enable 60 FPS Patch",
        variable=fps_var
    ).pack(anchor="w", padx=10, pady=5)

    tk.Checkbutton(
        win,
        text="Enable Shiny Rate Modifier",
        variable=shiny_var,
        command=toggle_slider
    ).pack(anchor="w", padx=10)

    slider = tk.Scale(
        win,
        from_=0,
        to=255,
        orient="horizontal",
        variable=shiny_value,
        command=lambda _: update_display(),
        state="disabled"
    )
    slider.pack(fill="x", padx=10, pady=(5, 0))

    display_label = tk.Label(
        win,
        justify="left",
        font=("TkDefaultFont", 9),
        state="disabled"
    )
    display_label.pack(anchor="w", padx=12, pady=(2, 8))

    update_display()

    tk.Button(
        win,
        text="Select ROM & Patch",
        command=lambda: (
            win.destroy(),
            start_patch(
                game_name,
                fps_var.get(),
                shiny_var.get(),
                shiny_value.get()
            )
        )
    ).pack(pady=10)

def load_image(filename):
    try:
        img = Image.open(os.path.join("images", filename))
        return ImageTk.PhotoImage(img)
    except:
        return None

root = tk.Tk()
root.title("Gen 4 Pokémon Patcher")
root.resizable(False, False)

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

row = col = 0
images = {}

for game_name, data in GAMES.items():
    img = load_image(data["image"])
    images[game_name] = img

    btn = tk.Button(
        frame,
        image=img,
        command=lambda g=game_name: open_options(g)
    )
    btn.grid(row=row, column=col, padx=10, pady=10)

    col += 1
    if col == 3:
        col = 0
        row += 1

root.mainloop()