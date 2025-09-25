## photon-main-referenceFiles % git pull origin main


##imported libraries
import tkinter as tk
from PIL import Image, ImageTk

##window tkinter object
window = tk.Tk()

##loads and resizes image
splashfile = Image.open('logo.jpg')
splashfile = splashfile.resize((1000, 800))
splashphoto = ImageTk.PhotoImage(splashfile)

##for some reason this is how tkiner wants a photo, conversion
root = tk.Label(window, image=splashphoto)
root.pack()

##placement on screen
window.geometry(f"{splashfile.width}x{splashfile.height}")
window.update_idletasks()
windowX = (window.winfo_screenwidth() - window.winfo_width()) // 2
windowY = (window.winfo_screenheight() - window.winfo_height()) // 2
window.geometry(f"+{windowX}+{windowY}")

##destroy after 3 seconds, 3000ms
window.after(3000, window.destroy)


window.mainloop()

##need to link