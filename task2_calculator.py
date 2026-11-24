from tkinter import *

def button_press(num):

    global equation_text

    equation_text = equation_text + str(num)

    equation_label.set(equation_text)

def equals():

    global equation_text

    try:

        total = str(eval(equation_text))

        equation_label.set(total)

        equation_text = total

    except SyntaxError:

        equation_label.set("syntax error")

        equation_text = ""

    except ZeroDivisionError:

        equation_label.set("arithmetic error")

        equation_text = ""

def clear():

    global equation_text

    equation_label.set("")

    equation_text = ""

def back():
    global equation_text
    equation_text = equation_text[:len(equation_text)-1]
    equation_label.set(equation_text)


window = Tk()
window.title("Calculator")
window.geometry("500x500")
icon= PhotoImage(file='calculator_image.png')
window.iconphoto(True, icon)
window.config(background="black")

# Label
equation_text = ""

equation_label = StringVar()

Label(window,bg="#a69d8c",width=20,bd=10, height=2,relief=SUNKEN, textvariable=equation_label,
     font=("Courier New", 24, "bold")).pack()

# Frame
frame = Frame(window,bg="#404040",bd=5,relief=SUNKEN)
frame.pack()

# Buttons
Button(frame,text="C/CE",font=("Consolas",25),width=5, command=clear,
       bg="#f29c4d", fg="#fce8c1").grid(row=0, column=1)

Button(frame,text="⌫",font=("Consolas",25),width=5, command=back,
       bg="#f29c4d", fg="#fce8c1").grid(row=0, column=2)

Button(frame,text="=",font=("Consolas",25),width=5,
       bg="#212122", fg="white", command=equals).grid(row=4, column=2)

button1 = Button(frame, text=1, font=("Consolas",25),width=5,
       bg="#212122", fg="white", command=lambda: button_press(1))
button1.grid(row=3, column=0)

button2 = Button(frame, text=2,  font=("Consolas",25),width=5,
       bg="#212122", fg="white",command=lambda: button_press(2))
button2.grid(row=3, column=1)

button3 = Button(frame, text=3,  font=("Consolas",25),width=5,
       bg="#212122", fg="white",command=lambda: button_press(3))
button3.grid(row=3, column=2)

button4 = Button(frame, text=4, font=("Consolas",25),width=5,
       bg="#212122", fg="white",command=lambda: button_press(4))
button4.grid(row=2, column=0)

button5 = Button(frame, text=5,  font=("Consolas",25),width=5,
       bg="#212122", fg="white",command=lambda: button_press(5))
button5.grid(row=2, column=1)

button6 = Button(frame, text=6, font=("Consolas",25),width=5,
       bg="#212122", fg="white",command=lambda: button_press(6))
button6.grid(row=2, column=2)

button7 = Button(frame, text=7,  font=("Consolas",25),width=5,
       bg="#212122", fg="white", command=lambda: button_press(7))
button7.grid(row=1, column=0)

button8 = Button(frame, text=8,  font=("Consolas",25),width=5,
       bg="#212122", fg="white",command=lambda: button_press(8))
button8.grid(row=1, column=1)

button9 = Button(frame, text=9,  font=("Consolas",25),width=5,
       bg="#212122", fg="white",command=lambda: button_press(9))
button9.grid(row=1, column=2)

button0 = Button(frame, text=0,  font=("Consolas",25),width=5,
       bg="#212122", fg="white",command=lambda: button_press(0))
button0.grid(row=4, column=0)

plus = Button(frame, text='+',  font=("Consolas",25),width=5,
       bg="#212122", fg="white", command=lambda: button_press('+'))
plus.grid(row=4, column=3)

minus = Button(frame, text='-',  font=("Consolas",25),width=5,
       bg="#212122", fg="white",command=lambda: button_press('-'))
minus.grid(row=3, column=3)

multiply = Button(frame, text='x',  font=("Consolas",25),width=5,
       bg="#212122", fg="white",command=lambda: button_press('*'))
multiply.grid(row=2, column=3)

divide = Button(frame, text='÷',  font=("Consolas",25),width=5,
       bg="#212122", fg="white",command=lambda: button_press('/'))
divide.grid(row=1, column=3)

decimal = Button(frame, text='.',  font=("Consolas",25),width=5,
       bg="#212122", fg="white",command=lambda: button_press('.'))
decimal.grid(row=4, column=1)


window.mainloop()