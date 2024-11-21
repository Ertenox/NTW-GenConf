import re

class Template:

    def __init__(self, title, content = "", dict = {}):
        self.title = title.split('\\')[-1]
        self.content = content
        self.__dict = dict
        self.__outContent = ""

    def findAllVar(self):
        temp = re.findall(r"\$\{([^}]+)\}", self.content)
        temp.sort()
        for var in temp:
            if var != "_MODE_CLI_":
                self.__dict[var] = ""
        
    
    def getAllVar(self) -> dict:
        self.findAllVar()
        return self.__dict 
    
    def setVar(self, var, value):
        if var in self.__dict:
            self.__dict[var] = value
        else:
            print("Error: variable not found")

    def replaceVar(self):
        """ fonction pour remplacer les variables par leur valeur saisie """
        self.__outContent = self.content
        for i in self.__dict:
            if self.__dict[i] != "":
                self.__outContent = re.sub(r"\$\{"+i+r"\}", self.__dict[i], self.__outContent)

    def getDict(self) -> dict:
        return self.__dict

    def getOutContent(self) -> str:
        return self.__outContent
    

    

