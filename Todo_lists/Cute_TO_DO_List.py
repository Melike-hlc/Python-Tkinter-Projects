import json
import tkinter as tk
import tkinter.font as tkfont
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageTk

# Windows'ta bulanık görüntüyü engelle
try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

BASE_DIR = Path(__file__).parent
IMAGE_PATH = BASE_DIR / "to_do_bg.png"
DATA_PATH = BASE_DIR / "todos.json"       # görevler burada saklanır

# Renkler (sararmış kağıt teması)
PAPER_RGBA = (243, 226, 178, 225)   # sararmış kağıt, hafif saydam
LINE_COLOR = "#cdb67f"              # çizgili satır rengi
MARGIN_COLOR = "#d49a8a"            # sol kenar boşluk çizgisi
INK = "#4a3520"                     # mürekkep (koyu kahve)
INK_DONE = "#9b8a6a"                # tamamlanan görev rengi
BOX_COLOR = "#6b4f2a"
DEL_COLOR = "#a8523f"

MAX_CHARS = 30


def pick_handwriting_font():
    """Sistemde bulunan ilk el yazısı benzeri fontu seç."""
    candidates = ["Segoe Print", "Bradley Hand", "Ink Free", "Comic Sans MS",
                  "Chalkboard SE", "Noteworthy", "Comic Neue", "TkDefaultFont"]
    available = set(tkfont.families())
    for name in candidates:
        if name in available:
            return name
    # return "TkDefaultFont"
    return "Segoe Print"


class TodoApp:
    def __init__(self, root):
        self.root = root
        root.title("TO-DO List")
        root.resizable(False, False)

        # ---- Resmi yükle ve ekrana sığacak şekilde ölçekle ----
        img = Image.open(IMAGE_PATH).convert("RGBA")
        iw, ih = img.size
        screen_h = root.winfo_screenheight()
        self.h = int(min(screen_h * 0.85, 900))
        self.w = int(self.h * iw / ih)
        img = img.resize((self.w, self.h), Image.LANCZOS)

        # ---- Kağıt bölgesi ----
        self.px0 = int(self.w * 0.10)
        self.px1 = int(self.w * 0.90)
        self.py0 = int(self.h * 0.12)
        self.py1 = int(self.h * 0.90)

        img = self._add_paper(img)
        self.bg = ImageTk.PhotoImage(img)

        self.canvas = tk.Canvas(root, width=self.w, height=self.h,
                                highlightthickness=0, bd=0)
        self.canvas.pack()
        self.canvas.create_image(0, 0, image=self.bg, anchor="nw")

        # ---- Fontlar ----
        self.line_h = int(self.h * 0.058)
        size = max(11, int(self.line_h * 0.42))
        family = pick_handwriting_font()
        self.font = tkfont.Font(family=family, size=size)
        self.font_done = tkfont.Font(family=family, size=size, overstrike=True)
        self.font_title = tkfont.Font(family=family, size=int(size * 1.6),
                                      weight="bold")

        # ---- Satır yerleşimi ----
        self.title_y = self.py0 + int(self.line_h * 0.9)
        self.first_line_y = self.py0 + int(self.line_h * 2.0)   # ilk çizgi
        self.entry_y = self.py1 - int(self.line_h * 0.9)
        usable = self.entry_y - int(self.line_h * 0.6) - self.first_line_y
        self.rows = max(1, usable // self.line_h)

        self._draw_static()

        # ---- Giriş alanı ----
        self.var = tk.StringVar()
        self.var.trace_add("write", self._limit)
        entry_w = self.px1 - self.px0 - int(self.w * 0.30)
        self.entry = tk.Entry(root, textvariable=self.var, font=self.font,
                              bg="#f7ecc9", fg=INK, relief="flat",
                              insertbackground=INK, highlightthickness=1,
                              highlightbackground=LINE_COLOR,
                              highlightcolor=BOX_COLOR)
        self.canvas.create_window(self.px0 + int(self.w * 0.07), self.entry_y,
                                  window=self.entry, anchor="w",
                                  width=entry_w)
        btn = tk.Button(root, text="Add", font=self.font, command=self.add,
                        bg="#d9c08a", fg=INK, activebackground="#c9ae72",
                        relief="flat", cursor="hand2")
        self.canvas.create_window(self.px1 - int(self.w * 0.05), self.entry_y,
                                  window=btn, anchor="e")
        self.entry.bind("<Return>", lambda e: self.add())
        self.entry.focus_set()

        # ---- Veri ----
        self.todos = self._load()
        self.offset = 0
        self.canvas.bind_all("<MouseWheel>", self._on_wheel)       # Win/Mac
        self.canvas.bind_all("<Button-4>", lambda e: self._scroll(-1))  # Linux
        self.canvas.bind_all("<Button-5>", lambda e: self._scroll(1))
        self.render()

    # ------------------------------------------------------------------
    def _add_paper(self, img):
        """Resmin üstüne gölgeli, yuvarlak köşeli, yarı saydam kağıt ekle."""
        shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        off = 5
        sd.rounded_rectangle((self.px0 + off, self.py0 + off,
                              self.px1 + off, self.py1 + off),
                             radius=18, fill=(60, 40, 10, 90))
        shadow = shadow.filter(ImageFilter.GaussianBlur(6))
        img = Image.alpha_composite(img, shadow)

        paper = Image.new("RGBA", img.size, (0, 0, 0, 0))
        pd = ImageDraw.Draw(paper)
        pd.rounded_rectangle((self.px0, self.py0, self.px1, self.py1),
                             radius=18, fill=PAPER_RGBA,
                             outline=(200, 175, 120, 255), width=2)
        return Image.alpha_composite(img, paper)

    def _draw_static(self):
        c = self.canvas
        c.create_text(self.w // 2, self.title_y, text="TO-DO List",
                      font=self.font_title, fill=INK)
        # Çizgili satırlar
        for i in range(self.rows + 1):
            y = self.first_line_y + i * self.line_h
            c.create_line(self.px0 + 14, y, self.px1 - 14, y,
                          fill=LINE_COLOR, width=1)
        # Sol kenar boşluk çizgisi
        mx = self.px0 + int(self.w * 0.07)
        c.create_line(mx, self.py0 + 12, mx, self.py1 - 12,
                      fill=MARGIN_COLOR, width=1)
        # Giriş satırının çizgisi
        y = self.entry_y + int(self.line_h * 0.55)
        c.create_line(self.px0 + 14, y, self.px1 - 14, y,
                      fill=LINE_COLOR, width=1)

    # ------------------------------------------------------------------
    def render(self):
        c = self.canvas
        c.delete("todo")
        visible = self.todos[self.offset:self.offset + self.rows]
        box = max(12, int(self.line_h * 0.38))
        mx = self.px0 + int(self.w * 0.07)
        for row, item in enumerate(visible):
            idx = self.offset + row
            line_y = self.first_line_y + (row + 1) * self.line_h
            cy = line_y - self.line_h // 2 - 2

            # Kutucuk
            bx0 = self.px0 + 22
            c.create_rectangle(bx0, cy - box // 2, bx0 + box, cy + box // 2,
                               outline=BOX_COLOR, width=2, tags=("todo", f"b{idx}"))
            if item["done"]:
                c.create_text(bx0 + box // 2, cy, text="✓", fill=BOX_COLOR,
                              font=self.font, tags=("todo", f"b{idx}"))
            c.tag_bind(f"b{idx}", "<Button-1>",
                       lambda e, i=idx: self.toggle(i))

            # Metin
            c.create_text(mx + 12, cy, text=item["text"], anchor="w",
                          font=self.font_done if item["done"] else self.font,
                          fill=INK_DONE if item["done"] else INK,
                          tags=("todo",))

            # Silme işareti
            c.create_text(self.px1 - 28, cy, text="✕", fill=DEL_COLOR,
                          font=self.font, tags=("todo", f"d{idx}"))
            c.tag_bind(f"d{idx}", "<Button-1>",
                       lambda e, i=idx: self.delete(i))
            c.tag_bind(f"d{idx}", "<Enter>",
                       lambda e: c.config(cursor="hand2"))
            c.tag_bind(f"d{idx}", "<Leave>",
                       lambda e: c.config(cursor=""))

        # Kaydırma ipucu
        if len(self.todos) > self.rows:
            c.create_text(self.px1 - 20, self.py0 + 14,
                          text=f"{self.offset + 1}-{min(self.offset + self.rows, len(self.todos))}"
                               f" / {len(self.todos)}",
                          anchor="e", fill=INK_DONE, tags=("todo",))

    # ------------------------------------------------------------------
    def add(self):
        text = self.var.get().strip()
        if not text:
            return
        self.todos.append({"text": text, "done": False})
        self.var.set("")
        # Yeni eklenen görünsün diye sona kaydır
        self.offset = max(0, len(self.todos) - self.rows)
        self._save()
        self.render()

    def toggle(self, i):
        self.todos[i]["done"] = not self.todos[i]["done"]
        self._save()
        self.render()

    def delete(self, i):
        del self.todos[i]
        self.offset = max(0, min(self.offset, len(self.todos) - self.rows))
        self._save()
        self.render()

    def _limit(self, *_):
        s = self.var.get()
        if len(s) > MAX_CHARS:
            self.var.set(s[:MAX_CHARS])

    def _on_wheel(self, e):
        self._scroll(-1 if e.delta > 0 else 1)

    def _scroll(self, step):
        max_off = max(0, len(self.todos) - self.rows)
        self.offset = max(0, min(self.offset + step, max_off))
        self.render()

    # ------------------------------------------------------------------
    def _load(self):
        try:
            return json.loads(DATA_PATH.read_text(encoding="utf-8"))
        except Exception:
            return []

    def _save(self):
        try:
            DATA_PATH.write_text(json.dumps(self.todos, ensure_ascii=False,
                                            indent=2), encoding="utf-8")
        except Exception as ex:
            print("Kaydedilemedi:", ex)


if __name__ == "__main__":
    root = tk.Tk()
    TodoApp(root)
    root.mainloop()