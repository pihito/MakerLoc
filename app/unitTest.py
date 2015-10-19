from dataObject import Utilisateur,UtilisateurHelper,DbStore
import unittest
import logging
import logging.config

class DbData(unittest.TestCase):
        
    def test_utilisateur(self):
        
        self.dbStore = DbStore("192.168.1.27:27017","MakerLoc")
        helper = UtilisateurHelper(self.dbStore)
        helper.cleanAll()
        u1 = Utilisateur("delporte","1234","sdelporte@gmail.com")
        u2 = Utilisateur("pol","1234","pol@gmail.com")
        helper.store(u1)
        helper.secureStore(u2)
        helper.secureStore(u2)
        helper.lenght()
        u3 = helper.getOneByName("delporte")
        assert u3 != None
        print(u3.toString())
        u1.cardId = "789"
        helper.updateAllField(u1)
        u3 = helper.getOneByName("delporte")
        assert u3.cardId == "789" 




if __name__ == "__main__" : 
    logging.config.fileConfig('logger.conf') 
    unittest.main()