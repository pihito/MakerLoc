__author__ = 'Delporte sebastien'
__version__ = '0.1'
__license__ = 'MIT'

import tkinter as tk
from tkinter import ttk
import logging
import logging.config
from dataObject import Utilisateur,UtilisateurHelper,DbStore
from PIL import ImageTk, Image
import os,sys

class IconLoader :
    icon = {} 
    logger = logging.getLogger('iconLoader')
    def load(self,path) : 
        dirs = os.listdir(path)
        self.logger.debug("debut du chagement de " + path)
        for file in dirs : 
            name = file.split('.')[0]
            fullPath = path + "/" + file
            self.icon[name] = ImageTk.PhotoImage(Image.open(fullPath))
            self.logger.debug("chagement de " + fullPath + " sous " + name)



class UserWidget(ttk.Frame) : 
    def __init__(self, parent):
        self.__parent__ = parent
        
        self.tkUserName = tk.StringVar()
        self.tkNom =  tk.StringVar()
        self.tkEmail =  tk.StringVar()
        self.tkPrenom =  tk.StringVar()
        self.tkCarte = tk.StringVar()
        self.tkRetour = tk.StringVar()

        self.loadUser()
        
        self.initialize()
    
    def loadUser(self) : 
        helper = UtilisateurHelper(dbStore)
        self.utilisateurs = helper.getAll()
        self.curIndex = -1
        
    def refreshListBox(self):
        self.loadUser()
        self.listBoxUser.delete(0, tk.END) 
        i = 0
        for u in self.utilisateurs : 
            self.listBoxUser.insert(i, u.userName)
            i=i+1

    def showUser(self,e) : 
         idxs = self.listBoxUser.curselection()
         if len(idxs) == 1 : 
            idx = int(idxs[0])
            self.curIndex = idx
            u  = self.utilisateurs[idx]
            self.tkUserName.set(u.userName)
            self.tkNom.set(u.firstName)
            self.tkEmail.set(u.email)
            self.tkPrenom.set(u.lastName)
            self.tkCarte.set(u.cardId)

    def saveUser(self,u) : 
        try : 
            u.setEmail(self.tkEmail.get())
            u.userName = self.tkUserName.get()
            u.firstName = self.tkNom.get()
            u.lastName = self.tkPrenom.get()
            u.cardId = self.tkCarte.get()
            helper = UtilisateurHelper(dbStore)
            helper.secureStore(u)
        except Exception as e : 
            self.tkRetour.set("addresse email invalide")
           
    def createCommand(self) : 
        self.tkRetour.set("")
        self.listBoxUser.selection_clear(self.curIndex)
        self.curIndex = -1 
        self.entryUserUserName.config(state=tk.NORMAL)

        self.tkUserName.set("")
        self.tkNom.set("")
        self.tkEmail.set("")
        self.tkPrenom.set("")
        self.tkCarte.set("")




    def deleteCommand(self) : 
        self.tkRetour.set("")
        helper = UtilisateurHelper(dbStore)
        u  = self.utilisateurs[self.curIndex]
        ret = helper.delete(u)
        if ret == 1 : 
            self.refreshListBox()
            self.tkRetour.set("utilisateur " + u.userName + " supprimé")
        else : 
            self.tkRetour.set("impossible de supprimer " + u.userName)

        

    def saveCommand(self) : 
        self.tkRetour.set("")
        u  = self.utilisateurs[self.curIndex]
        self.saveUser(u)
        self.refreshListBox()

    def refreshNFC(self) : 
        self.tkCarte.set("100")

    def initialize(self):
        tk.Frame.__init__(self)
        self.grid()

        self.listBoxUser =  tk.Listbox(self)
        self.tkScroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.listBoxUser.yview)
        self.listBoxUser['yscrollcommand'] = self.tkScroll.set
        #ttk.Sizegrip().grid(column=1, row=1, sticky=(tk.S,tk.E))
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        i = 0
        for u in self.utilisateurs : 
            self.listBoxUser.insert(i, u.userName)
            i=i+1

        self.listBoxUser.bind('<<ListboxSelect>>', self.showUser)


        self.lbRetour = ttk.Label(self)
        self.lbRetour['textvariable'] = self.tkRetour
        self.lbUserName = ttk.Label(self, text="Nom d utilisateur")
        self.lbLastName = ttk.Label(self, text="Nom")
        self.lbFirstName = ttk.Label(self, text="Prenom")
        self.lbEmail = ttk.Label(self, text="email")
        self.lbCard = ttk.Label(self, text="carte")
        self.lbUserName = ttk.Label(self, text="Nom d utilisateur")

        self.entryUserUserName =  ttk.Entry(self,textvariable=self.tkUserName, state=tk.DISABLED,width=30)
        self.entryLastName =  ttk.Entry(self,textvariable=self.tkNom, width=30)
        self.entryFirstName =  ttk.Entry(self,textvariable=self.tkPrenom, width=30)
        self.entryEmail =  ttk.Entry(self,textvariable=self.tkEmail, width=30)
        self.entryCard = ttk.Entry(self,textvariable=self.tkCarte, width=30)

        self.btcreate = ttk.Button(self, image = iconLoader.icon["add"], command=self.createCommand)
        self.btsave = ttk.Button(self, image = iconLoader.icon["save"], command=self.saveCommand)
        self.btdelete = ttk.Button(self, image = iconLoader.icon["delete"], command=self.deleteCommand)
        self.btRefreshCard = ttk.Button(self, image = iconLoader.icon["refresh_card"], command=self.refreshNFC)

        self.listBoxUser.grid(column=0,row=0,rowspan=7, sticky=(tk.N,tk.W,tk.E,tk.S))
        self.tkScroll.grid(column=1, row=0, rowspan=7,sticky=(tk.N,tk.S))

        self.lbRetour.grid(column=2,row=5,columnspan=2) 
        self.lbUserName.grid(column=2,row=0,sticky=tk.E)
        self.lbLastName.grid(column=2,row=1,sticky=tk.E)
        self.lbFirstName.grid(column=2,row=2,sticky=tk.E)
        self.lbEmail.grid(column=2,row=3,sticky=tk.E)
        self.lbCard.grid(column=2,row=4,sticky=tk.E)

        self.entryUserUserName.grid(column=3,row=0,sticky=tk.W)
        self.entryLastName.grid(column=3,row=1,sticky=tk.W)    
        self.entryFirstName.grid(column=3,row=2,sticky=tk.W)       
        self.entryEmail.grid(column=3,row=3,sticky=tk.W)      
        self.entryCard.grid(column=3,row=4,sticky=tk.W)    

        self.btsave.grid(column = 3,row=7)
        self.btcreate.grid(column = 0,row=7)
        self.btdelete.grid(column = 2,row=7)
        self.btRefreshCard.grid(column=4,row=4)

class MainWindow (tk.Frame) :

    def __init__(self, parent):
        self.__parent__ = parent
        self.initWidget()

    def initWidget(self):
        tk.Frame.__init__(self)
        #self.config(width=800,height=600)
        self.grid()
        self.userWidget = UserWidget(self)
        self.userWidget.grid(column=0, row=0)


logging.config.fileConfig('logger.conf')
dbStore = DbStore("192.168.1.27:27017","MakerLoc")
iconLoader = IconLoader()

if __name__ == '__main__':    
    top = tk.Tk()
    iconLoader.load("./img")
    top.title("Maker location")
    main = MainWindow(top);
    top.grid()
    main.grid(column=0, row=0)
    top.mainloop()
