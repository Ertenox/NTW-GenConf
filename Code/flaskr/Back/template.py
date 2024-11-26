import re

class Template:

    def __init__(self, title, content = ""):
        self.title = title.split('\\')[-1]
        self.content = content
        self.__outContent = ""
        self.__dict = {}

    @staticmethod
    def fromJson(title, content, dict):
        template = Template(title, content)
        template.__dict = dict
        return template

    def findAllVar(self):
        temp = re.findall(r"\$\{([^}]+)\}", self.content)
        temp.sort()
        print("appelle de findAllVar pour le template", self.title, "les variables sont", temp)
        for var in temp:
            if var != "_MODE_CLI_":
                self.__dict[var] = ""
        
    
    def setVar(self, var, value):
        print("appelle de setVar pour le template", self.title, "la variable est", var, "la valeur est", value)
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
        print("appelle de getDict pour ", self.title, "les variables sont", self.__dict)    
        return self.__dict

    def getOutContent(self) -> str:
        return self.__outContent
    
  
    

    

