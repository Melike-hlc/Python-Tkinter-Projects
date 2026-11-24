from tkinter import *
from tkinter import ttk
from tkinter import messagebox


def click():
    try:
        number =  float(entry.get())
        if combobox.get() == "km ↔ mile": result = (number * 0.62137 , " mile")
        elif combobox.get() == "mile ↔ km": result = (number * 1.609344, " km")
        elif combobox.get() == "◦C ↔ ◦F": result = (number * 1.8 +32, " ◦F")
        elif combobox.get() == "◦F ↔ ◦C": result = ((number-32) / 1.8 , " ◦C")
        elif combobox.get() == "kg ↔ lb": result = (number* 2.2046226218, " lb")
        else: result = (number* 0.45359237, " kg")

    except:
        messagebox.showwarning(title='WARNING!',message='You have to enter a valid number!!!')
    else:
        lb_result.config(text=f"Result: {result[0]} {result[1]}")
        lb_result.pack()


window = Tk()
window.title("Unit Converter")
icon= PhotoImage(file='converter_image.png')
window.iconphoto(True, icon)
window.config(background="#f6decd")

# Label
Label(window,
          text = "Select the conversion type:",
          font=('Ink Free',25,'bold'),
          fg='#DAC4D0',
          bg='#A75364',
          relief=RAISED,
          bd=10,
          padx=20,
          pady=20,).pack()

# Combobox
conversion_types = ('km ↔ mile',
          'mile ↔ km',
          '◦C ↔ ◦F',
          '◦F ↔ ◦C',
          'kg ↔ lb',
          'lb ↔ kg'
          )
combobox= ttk.Combobox(window, width = 20,
                            font=('Ink Free',25,'bold'),
                            values = conversion_types,
                            state="readonly"
                            )
combobox.pack()
combobox.current(0)

# Entry
entry= Entry(window,
                    font=('Ink Free',25,'bold')
       )
entry.pack()

# Button
Button(window,
            text='Convert',
            command=click,
            font=('Ink Free',20,'bold'),
            relief=RAISED,
            bd=10,
            bg='#A75364',
            fg='#DAC4D0',
            activebackground='#036264',
            activeforeground='#75e1e3'
            ).pack()
# Result Label
lb_result = Label(window,
           font=('Ink Free', 25, 'bold'))



window.mainloop()