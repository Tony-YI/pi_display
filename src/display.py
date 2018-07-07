from lib import *


# create a window
window = tkinter.Tk()

# add title to the window
window.title('pi_display')

window.attributes('-fullscreen', True)
window.bind('<Escape>',lambda e: window.destroy())

# run the window loop
window.mainloop()