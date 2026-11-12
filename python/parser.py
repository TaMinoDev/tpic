import json
import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox


def parse_tpic(raw_text: str) -> dict:
    clean_text = re.sub(r"\s+", "", raw_text)

    if len(clean_text) <= 5:
        raise ValueError("Die Datei ist leer oder zu kurz.")

    data = {}
    parts = clean_text.split(",")

    try:
        for part in parts:
            if part.startswith("t="):
                data["type"] = part[2:]
            elif part.startswith("c="):
                color_str = part[2:]
                color_json = re.sub(
                    r"(#[0-9a-fA-F]+)", r'"\1"', color_str
                ).replace('""', '","')
                data["c"] = json.loads(color_json)
            elif part.startswith("w="):
                data["w"] = int(part[2:])
            elif part.startswith("h="):
                data["h"] = int(part[2:])
            elif part.startswith("m="):
                map_json = part[2:].replace("|", ",")
                data["m"] = json.loads(map_json)
    except Exception as e:
        raise ValueError(f"Fehler beim Erfassen der Metadaten: {e}")

    if data.get("type") != "tpic":
        raise ValueError("Ungültiger Dateityp. 't=tpic' erwartet.")

    return data


def show_tpic(root: tk.Tk, data: dict, filename: str):
    # Hauptfenster wieder einblenden
    root.deiconify()
    root.title(f"{filename} ({data['w']}x{data['h']}) - TPIC Viewer")

    # Automatische Skalierung: Zielgröße ca. 500px auf der längsten Seite
    max_side = max(data["w"], data["h"])
    scale = max(1, 500 // max_side)

    canvas = tk.Canvas(
        root,
        width=data["w"] * scale,
        height=data["h"] * scale,
        highlightthickness=0,
    )
    canvas.pack()

    for y in range(data["h"]):
        for x in range(data["w"]):
            color_index = int(data["m"][y][x])
            color = (
                data["c"][color_index]
                if color_index < len(data["c"])
                else "#000000"
            )

            x1 = x * scale
            y1 = y * scale
            x2 = x1 + scale
            y2 = y1 + scale

            canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")


def main():
    root = tk.Tk()
    # Leeres Hauptfenster verstecken, solange der Datei-Dialog offen ist
    root.withdraw()

    # Datei-Auswahlfenster öffnen
    filepath = filedialog.askopenfilename(
        title="TPIC-Bild auswählen",
        filetypes=[
            ("TPIC Bilder", "*.tpic"),
            ("Textdateien", "*.txt"),
            ("Alle Dateien", "*.*"),
        ],
    )

    # Falls der Nutzer auf "Abbrechen" klickt, Programm sauber beenden
    if not filepath:
        root.destroy()
        return

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()

        parsed_data = parse_tpic(content)
        filename = os.path.basename(filepath)
        show_tpic(root, parsed_data, filename)
        root.mainloop()

    except Exception as e:
        messagebox.showerror("Fehler beim Öffnen", str(e))
        root.destroy()


if __name__ == "__main__":
    main()
