__author__ = 'Delporte sebastien'
__version__ = '0.1'
__license__ = 'MIT'

import logging
import json
from pymongo import MongoClient,ASCENDING
from pymongo.errors import ConnectionFailure,InvalidName
from re import compile
import datetime


# Python.
class DataObjectImplementException(Exception) : 
    def __str__(self):
        return "l'objet fils doit implémenter getKeys,getData,toString,toJson"

class DataObject() : 

    creationDate = datetime.datetime.now()
    modificationDate =  datetime.datetime.now()    
    
    def getKeys() : 
        raise dataObjectImplementException()
    def getData() : 
        raise dataObjectImplementException()
    def toString() : 
        raise dataObjectImplementException()
    def toJson() :
        raise dataObjectImplementException()


class Utilisateur(DataObject) : 
    
    logger = logging.getLogger('dataClass')

    def __init__(self,userName="",cardId="",email=None,firstName="",lastName="",activate=True):
        self.userName = userName
        self.cardId = cardId
        self.firstName = firstName
        self.lastName = lastName 
        self.activate = activate


        if email != None : 
            self.setEmail(email)
        else : 
            self.email = email
        
    def setEmail(self,value) : 
        if self.emailValide(value) : 
            self.email = value
        else : 
             self.logger.warning("Utilisateur - bad email : " + value)
             raise Exception
                
    def emailValide(self, value) : 
        email_re = compile(r'^[\S]+@[\S]+\.[\S]+$')
        return email_re.match(value)
    
    def toString(self) :
        return "userName : " + self.userName + " cardId : " + self.cardId + " email : " + self.email + " lastName : " + self.lastName +" firstName : " + self.firstName + " activate : " + str(self.activate) 
    
    def getData(self) : 
        return {"userName" : self.userName,"cardId" : self.cardId,"email":self.email,"lastName": self.lastName,"firstName":self.firstName,"activate":self.activate,
                "creationDate":self.creationDate,"modificationDate":self.modificationDate}
        
    def toJson(self) :
        return json.dumps(self.getData(),sort_keys=True, indent=4)
    def getKeys(self) : 
        return {"userName" : self.userName}

    
class BaseHelper : 
    
    def __init__(self,dbStore) : 
        self.collecName = None
        self.dbStore = dbStore

    def store(self,dataObject) : 
            dataObject.creationDate = datetime.datetime.now()
            dataObject.modificationDate = datetime.datetime.now() 
            self.dbStore.store(self.collecName,dataObject)
        
    def secureStore(self,dataObject) : 
            dataObject.modificationDate = datetime.datetime.now() 
            self.dbStore.secureStore(self.collecName,dataObject)

    def updateField(self,dataObject,fieldsToUpd) : 
            fieldsToUpd[modificationDate]= datetime.datetime.now()
            self.dbStore.updateField(self.collecName,dataObject.getKeys(),fieldsToUpd)

    def lenght(self) :
        self.dbStore.lenght(self.collecName)

    def cleanAll(self) :
        self.dbStore.cleanAll(self.collecName)


class UtilisateurHelper(BaseHelper) : 
    
    def __init__(self,dbStore) : 
        super().__init__(dbStore)
        self.collecName = "utilisateur"        
    
    def getAll(self) : 
        retour = []
        for doc in self.dbStore.getAll(self.collecName).sort('userName', ASCENDING) : 
            retour.append(self.createFromDic(doc))
        return retour

    def getOneByName(self,userName) :
        retour = None
        data = self.dbStore.requestGetOne(self.collecName,{"userName": userName})
        if data != None : 
            retour = self.createFromDic(data)
        return retour

    def createFromDic(self,values) : 
        ret = Utilisateur(values["userName"],values["cardId"],values["email"],values["firstName"],values["lastName"],values["activate"])
        ret.creationDate = values["creationDate"]
        ret.modificationDate = values["modificationDate"]
        return ret

    def updateAllField(self,utilisateur) :
        self.updateField(utilisateur,utilisateur.getData())

    def delete(self,utilisateur) :
        return self.dbStore.delete(self.collecName,utilisateur.getKeys())

class DbStoreException(Exception) : 
    errorCode = { 0x01 : "impossible de ce connecté" ,
                  0x02 : "insertion/mise à jour impossible"}
    logger = logging.getLogger('db')

    def __init__(nbr,e = None) : 
        self.logger.error("DbStore Error : " + str(nbr) +'-'+ self.errorCode[nbr])
        self.rootExp = e
        self.nbr = nbr
        if e != None :
            self.logger.error(e)
    
    def getMessage() : 
        return str(self.nbr) + ":" + self.errorCode[self.nbr]
      
    def __str__(self):
        return getMessage()

class DbStore : 
    
    logger = logging.getLogger('db')
    
    def __init__(self,server='localhost:27017',dbName = "test") : 
        try : 
            self.dbName = dbName
            self.client = MongoClient(server)
            self.logger.info("db connnection ok")
            self.db = self.getDb(self.dbName)
        except ConnectionFailure as e:
            raise DbStoreException(0x01)

    def getDb(self,dbName) : 
        try :
            db = self.client[dbName]
            return db
        except InvalidName as e: 
            self.logger.error("impossible d'ouvrir la db :" + dbName)

    def updateField(self,collecName,Keys,fieldsToUpd) : 
        self.logger.debug("tentative maj - clès :  "+json.dumps(Keys,sort_keys=True, indent=4) + " valeurs : "+json.dumps(fieldsToUpd,sort_keys=True, indent=4))
        collec = self.db[collecName]
        updResult = collec.update_one(Keys,{"$set": fieldsToUpd},False)
        if updResult.acknowledged == False :
            self.logger.error("Erreur maj- collection : " +collecName +" objet : "+ dataObject.toString())
            raise DbStoreException(0x02)
        else : 
            self.logger.debug("maj ok")

    def secureStore(self,collecName,dataObject) : 
        self.logger.debug("tentative maj/insertion : " + dataObject.toString())
        collec = self.db[collecName]
        updResult = collec.update_one(dataObject.getKeys(),{"$set":dataObject.getData()},True)
        if updResult.acknowledged == False :
            self.logger.error("Erreur maj/insertion -- collection : " +collecName +" objet : "+ dataObject.toString())
            raise DbStoreException(0x02)
        else : 
            if updResult.upserted_id : 
                self.logger.debug("maj/insertion ok - numéro d'insertion : " + str(updResult.upserted_id) )
            else :
                self.logger.debug("maj/insertion ok")

    def store(self,collecName,dataObject) :
        self.logger.debug("tentative insertion : " + dataObject.toString())
        collec = self.db[collecName]
        sgId = collec.insert_one(dataObject.getData()).inserted_id
        self.logger.info("data insert : " + str(sgId))
        return sgId

    def requestGetOne(self,collecName,request) : 
        retour = None
        collec = self.db[collecName]
        data = collec.find_one(request)
        self.logger.debug("resquest : collection : " + collecName + " requete : " + json.dumps(request,sort_keys=True, indent=4) + " data : " + json.dumps([str(v) for v in data.values()],sort_keys=True, indent=4))
        return data


    def lenght(self,collecName) :
        collec = self.db[collecName]
        collec.count()

    def cleanAll(self,collecName) :
        collec = self.db[collecName]
        collec.drop()        

    def getAll(self,collecName) : 
        collec = self.db[collecName]
        self.logger.debug("Get all data on " + collecName) 
        return collec.find()

    def delete(self,collecName,keys) : 
       collec = self.db[collecName]
       self.logger.debug("requete de suppression - collection : " + collecName + "clès : " + json.dumps([str(v) for v in keys.values()],sort_keys=True, indent=4))
       result = collec.delete_one(keys)
       self.logger.debug("nombre d'objet supprimé : " + str(result.deleted_count)) 
       return result.deleted_count
