import tkinter as tk
import logging
import logging.config

class MainWindow (tk.Frame) :

	def __init__(self, parent):
	    self.__parent__ = parent
	    self.__initialize__()

	def __initialize__(self):
		tk.Frame.__init__(self) 
               
if __name__ == '__main__':
    
    logging.config.fileConfig('logger.conf')
    
    top = tk.Tk()
    top.title("Maker location")
    main = MainWindow(top);
    top.grid()
    main.grid(column=0, row=0)
    top.mainloop()