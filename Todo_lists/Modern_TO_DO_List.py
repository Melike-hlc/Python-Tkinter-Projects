import json
import tkinter as tk
import tkinter.font as tkfont
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageTk

try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

BASE_DIR = Path(__file__).parent
IMAGE_PATH = BASE_DIR / "wood_light_background.png"
DATA_PATH = BASE_DIR / "todos_isik.json"

AMBER = (255, 179, 71)
AMBER_HI = (255, 214, 140)
TEXT = "#f2e6d3"
TEXT_DONE = "#ffcf8a"
MUTED = "#8a7860"
TRACK = "#4a3b2b"
MAX_CHARS = 32


def hexc(rgb):
    return "#%02x%02x%02x" % tuple(int(v) for v in rgb)


def blend(base, top, a):
    return tuple(base[i] * (1 - a) + top[i] * a for i in range(3))


def pick_font():
    candidates = ["Segoe UI Light", "Segoe UI", "SF Pro Display",
                  "Helvetica Neue", "Montserrat", "Helvetica", "Arial",
                  "TkDefaultFont"]
    available = set(tkfont.families())
    for name in candidates:
        if name in available:
            return name
    return "TkDefaultFont"


class TodoApp:
    def __init__(self, root):
        self.root = root
        root.title("Yapılacaklar")
        root.resizable(False, False)

        # ---- Resmi pencereye sığacak şekilde ölçekle ----
        img = Image.open(IMAGE_PATH).convert("RGBA")
        iw, ih = img.size
        self.h = int(min(root.winfo_screenheight() * 0.85, 820))
        self.w = int(self.h * iw / ih)
        img = img.resize((self.w, self.h), Image.LANCZOS)

        # ---- Panel ölçüleri ----
        self.pw = int(self.w * 0.46)
        self.ph = int(self.h * 0.86)
        self.px0 = (self.w - self.pw) // 2
        self.py0 = (self.h - self.ph) // 2
        self.px1 = self.px0 + self.pw
        self.py1 = self.py0 + self.ph

        img, self.panel_rgb = self._add_glass_panel(img)
        self.panel_hex = hexc(self.panel_rgb)
        self.bg = ImageTk.PhotoImage(img)

        self.canvas = tk.Canvas(root, width=self.w, height=self.h,
                                highlightthickness=0, bd=0)
        self.canvas.pack()
        self.canvas.create_image(0, 0, image=self.bg, anchor="nw")

        # ---- Fontlar ----
        fam = pick_font()
        size = max(11, int(self.h * 0.019))
        self.font = tkfont.Font(family=fam, size=size)
        self.font_done = tkfont.Font(family=fam, size=size, overstrike=True)
        self.font_small = tkfont.Font(family=fam, size=max(9, size - 3))
        self.font_title = tkfont.Font(family=fam, size=int(size * 1.5),
                                      weight="bold")

        # ---- Yerleşim ----
        self.pad = int(self.pw * 0.09)
        cx = self.w // 2
        self.title_y = self.py0 + int(self.h * 0.07)
        self.sub_y = self.title_y + int(self.h * 0.045)
        self.bar_y = self.sub_y + int(self.h * 0.045)
        self.list_top = self.bar_y + int(self.h * 0.04)
        self.entry_y = self.py1 - int(self.h * 0.07)
        list_bottom = self.entry_y - int(self.h * 0.045)
        self.row_h = int(self.h * 0.072)
        self.rows = max(1, (list_bottom - self.list_top) // self.row_h)

        # Başlık (harf aralıklı, modern görünüm)
        self.canvas.create_text(cx, self.title_y, text="Y A P I L A C A K L A R",
                                font=self.font_title, fill=TEXT)
        self.sub_id = self.canvas.create_text(cx, self.sub_y, text="",
                                              font=self.font_small, fill=MUTED)

        # Giriş alanı
        self.var = tk.StringVar()
        self.var.trace_add("write", self._limit)
        left = self.px0 + self.pad
        right = self.px1 - self.pad
        btn_r = int(self.h * 0.022)
        self.entry = tk.Entry(self.root, textvariable=self.var, font=self.font,
                              bg=self.panel_hex, fg=TEXT, relief="flat",
                              insertbackground=hexc(AMBER), highlightthickness=0,
                              bd=0)
        self.canvas.create_window(left, self.entry_y, window=self.entry,
                                  anchor="w", width=right - left - btn_r * 2 - 14)
        # Entry altındaki ışık çizgisi
        ly = self.entry_y + int(self.h * 0.03)
        self._glow_line(left, right, ly, strength=0.35, tags=("static",))

        # "+" butonu (canvas üzerinde çizilmiş daire)
        bx = right - btn_r
        self.canvas.create_oval(bx - btn_r, self.entry_y - btn_r,
                                bx + btn_r, self.entry_y + btn_r,
                                outline=hexc(AMBER), width=2, tags=("addbtn",))
        self.canvas.create_text(bx, self.entry_y - 1, text="+",
                                fill=hexc(AMBER), font=self.font_title,
                                tags=("addbtn",))
        self.canvas.tag_bind("addbtn", "<Button-1>", lambda e: self.add())
        self.canvas.tag_bind("addbtn", "<Enter>",
                             lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind("addbtn", "<Leave>",
                             lambda e: self.canvas.config(cursor=""))
        self.entry.bind("<Return>", lambda e: self.add())
        self.entry.focus_set()

        # ---- Veri ----
        self.todos = self._load()
        self.offset = 0
        self.canvas.bind_all("<MouseWheel>",
                             lambda e: self._scroll(-1 if e.delta > 0 else 1))
        self.canvas.bind_all("<Button-4>", lambda e: self._scroll(-1))
        self.canvas.bind_all("<Button-5>", lambda e: self._scroll(1))
        self.render()

    # ------------------------------------------------------------------
    def _add_glass_panel(self, img):
        """Buzlu cam efektli, koyu tonlu, yuvarlak köşeli panel."""
        box = (self.px0, self.py0, self.px1, self.py1)
        radius = 26

        # Gölge
        shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(shadow).rounded_rectangle(
            (box[0] + 6, box[1] + 10, box[2] + 6, box[3] + 10),
            radius=radius, fill=(0, 0, 0, 140))
        img = Image.alpha_composite(img, shadow.filter(ImageFilter.GaussianBlur(18)))

        # Bulanık + koyu tint
        region = img.crop(box).filter(ImageFilter.GaussianBlur(16))
        tint = Image.new("RGBA", region.size, (22, 15, 9, 185))
        region = Image.alpha_composite(region, tint)

        mask = Image.new("L", region.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle(
            (0, 0, region.size[0] - 1, region.size[1] - 1),
            radius=radius, fill=255)
        img.paste(region, (box[0], box[1]), mask)

        # İnce amber kenar çizgisi
        outline = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(outline).rounded_rectangle(
            box, radius=radius, outline=AMBER + (90,), width=1)
        img = Image.alpha_composite(img, outline)

        avg = region.convert("RGB").resize((1, 1), Image.BILINEAR).getpixel((0, 0))
        return img, avg

    def _glow_line(self, x0, x1, y, strength=1.0, tags=("todo",)):
        """Çizginin üstüne doğru sönen sıcak LED ışığı çizer."""
        c = self.canvas
        steps = 10
        for k in range(steps, 0, -1):
            a = strength * 0.5 * (1 - k / steps) ** 2
            c.create_line(x0, y - k, x1, y - k,
                          fill=hexc(blend(self.panel_rgb, AMBER, a)), tags=tags)
        c.create_line(x0, y, x1, y,
                      fill=hexc(blend(self.panel_rgb, AMBER_HI, 0.35 + 0.65 * strength)),
                      width=2, tags=tags)

    def _switch(self, x, cy, on, tag):
        """Işık anahtarı: pill şeklinde toggle."""
        c = self.canvas
        w, h = int(self.h * 0.058), int(self.h * 0.03)
        r = h // 2
        x0, y0 = x, cy - r
        col = hexc(AMBER) if on else TRACK
        # Gövde
        c.create_oval(x0, y0, x0 + h, y0 + h, fill=col, outline=col, tags=("todo", tag))
        c.create_oval(x0 + w - h, y0, x0 + w, y0 + h, fill=col, outline=col, tags=("todo", tag))
        c.create_rectangle(x0 + r, y0, x0 + w - r, y0 + h, fill=col, outline=col, tags=("todo", tag))
        # Topuz
        kx = x0 + w - r if on else x0 + r
        kr = r - 3
        c.create_oval(kx - kr, cy - kr, kx + kr, cy + kr,
                      fill="#fff4de" if on else "#8a7860", outline="", tags=("todo", tag))
        c.tag_bind(tag, "<Enter>", lambda e: c.config(cursor="hand2"))
        c.tag_bind(tag, "<Leave>", lambda e: c.config(cursor=""))
        return w

    # ------------------------------------------------------------------
    def render(self):
        c = self.canvas
        c.delete("todo")
        left = self.px0 + self.pad
        right = self.px1 - self.pad

        # İlerleme ışık şeridi
        total = len(self.todos)
        done = sum(1 for t in self.todos if t["done"])
        c.create_line(left, self.bar_y, right, self.bar_y, fill=TRACK, width=2,
                      tags=("todo",))
        if total and done:
            x1 = left + int((right - left) * done / total)
            self._glow_line(left, x1, self.bar_y, strength=1.0)
        c.itemconfig(self.sub_id,
                     text=f"{done} / {total} aydınlatıldı" if total else "ilk görevini ekle")

        visible = self.todos[self.offset:self.offset + self.rows]
        for row, item in enumerate(visible):
            idx = self.offset + row
            top = self.list_top + row * self.row_h
            line_y = top + self.row_h
            cy = top + self.row_h // 2 - 2

            # Satır ayırıcı / yanan LED
            if item["done"]:
                self._glow_line(left, right, line_y, strength=0.9)
            else:
                c.create_line(left, line_y, right, line_y, fill=TRACK,
                              tags=("todo",))

            # Işık anahtarı
            sw = self._switch(left, cy, item["done"], f"s{idx}")
            c.tag_bind(f"s{idx}", "<Button-1>", lambda e, i=idx: self.toggle(i))

            # Metin
            c.create_text(left + sw + 16, cy, text=item["text"], anchor="w",
                          font=self.font_done if item["done"] else self.font,
                          fill=TEXT_DONE if item["done"] else TEXT,
                          tags=("todo",))

            # Silme
            d = c.create_text(right - 4, cy, text="✕", anchor="e",
                              fill=MUTED, font=self.font_small,
                              tags=("todo", f"d{idx}"))
            c.tag_bind(f"d{idx}", "<Button-1>", lambda e, i=idx: self.delete(i))
            c.tag_bind(f"d{idx}", "<Enter>",
                       lambda e, d=d: (c.itemconfig(d, fill="#e07a5f"),
                                       c.config(cursor="hand2")))
            c.tag_bind(f"d{idx}", "<Leave>",
                       lambda e, d=d: (c.itemconfig(d, fill=MUTED),
                                       c.config(cursor="")))

        # Kaydırma göstergesi
        if total > self.rows:
            c.create_text(right, self.list_top - 14,
                          text=f"{self.offset + 1}–{min(self.offset + self.rows, total)}",
                          anchor="e", fill=MUTED, font=self.font_small,
                          tags=("todo",))

    # ------------------------------------------------------------------
    def add(self):
        text = self.var.get().strip()
        if not text:
            return
        self.todos.append({"text": text, "done": False})
        self.var.set("")
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

    def _scroll(self, step):
        max_off = max(0, len(self.todos) - self.rows)
        self.offset = max(0, min(self.offset + step, max_off))
        self.render()

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