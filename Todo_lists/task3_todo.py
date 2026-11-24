from tkinter import *
import pickle
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "todo.txt"

def add():
    task = entry.get().strip()
    if task:
        listbox.insert(END, task)
        listbox.config(height=listbox.size())
    entry.delete(0, END)

def delete():
    for index in reversed(listbox.curselection()):
        listbox.delete(index)
    listbox.config(height=listbox.size())

def on_closing():
    tasks = listbox.get(0, END)
    with DATA_PATH.open("wb") as file:
        pickle.dump(tasks, file, protocol=pickle.HIGHEST_PROTOCOL)
    window.destroy()

def done():
    for index in listbox.curselection():
        text = listbox.get(index)
        listbox.delete(index)
        listbox.insert(index, text[2:] if text.startswith("✔ ") else "✔ " + text)

window = Tk()
window.title("TO-DO List")

listbox = Listbox(window,
                   bg="#f7ffde",
                   font=("Constantia", 20),
                   width=20,
                   selectmode=MULTIPLE)
listbox.pack()

frame = Frame(window)
frame.pack()

entry = Entry(window)
entry.pack()

Button(frame, text="Add", command=add).pack(side=LEFT)
Button(frame, text="Delete", command=delete).pack(side=LEFT)
Button(frame, text="Done", command=done).pack(side=LEFT)
# Önceki görevleri yükle
try:
    with DATA_PATH.open("rb") as file:
        tasks = pickle.load(file)
        for task in tasks:
            listbox.insert(END, task)
except (FileNotFoundError,pickle.UnpicklingError):
    pass

window.protocol("WM_DELETE_WINDOW", on_closing)
window.mainloop()
