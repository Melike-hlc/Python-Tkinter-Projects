from tkinter import *
last_x, last_y = None, None
color = "black"
brush_size = 10

def clean():
    canvas.delete("all")

def start(event):
    global last_x, last_y
    last_x, last_y = event.x, event.y

def draw(event):
    global last_x, last_y
    canvas.create_line( last_x, last_y, event.x, event.y,
                        fill=color, width= brush_size,
                        capstyle=ROUND,
                        smooth=True
                        )
    last_x, last_y = event.x, event.y

def color_change(c):
    global color
    color = c

def brush_size_changer(value):
    global brush_size
    brush_size= int(float(value))

window = Tk()
window.resizable(False, False)

canvas = Canvas(window, height=500, width=500)
canvas.pack()

canvas.bind("<Button-1>", start)      # tıklayınca başlangıç noktası
canvas.bind("<B1-Motion>", draw)      # basılı tutup sürükleyince çiz

frame = Frame(window)
frame.pack()

# Fırça boyutu değiştirme
scale = Scale(frame, from_=1, to=20, length=150, orient=HORIZONTAL,
              command=brush_size_changer)
scale.set(10)

scale.grid(row=0, column=2)

# Silme tuşu
Button(frame, text="Clean", command=clean).grid(row=0, column=4)

colors_frame = Frame(frame, bd=2, relief=GROOVE, padx=5, pady=5)
colors_frame.grid(row=1, column=0, columnspan=7, pady=5)

# Renk değiştirme
Button(colors_frame, text="blue",command=lambda:color_change("blue"),bg="blue", fg="white" ).pack(side=LEFT, padx=2)
Button(colors_frame, text="red",command=lambda:color_change("red"),bg="red", fg="white" ).pack(side=LEFT, padx=2)
Button(colors_frame, text="yellow",command=lambda:color_change("yellow"),bg="yellow" ).pack(side=LEFT, padx=2)
Button(colors_frame, text="green",command=lambda:color_change("green"),bg="green", fg="white" ).pack(side=LEFT, padx=2)
Button(colors_frame, text="purple",command=lambda:color_change("purple"),bg="purple", fg="white" ).pack(side=LEFT, padx=2)
Button(colors_frame, text="pink",command=lambda:color_change("pink"),bg="pink", fg="white" ).pack(side=LEFT, padx=2)
Button(colors_frame, text="black",command=lambda:color_change("black"),bg="black", fg="white" ).pack(side=LEFT, padx=2)



window.mainloop()