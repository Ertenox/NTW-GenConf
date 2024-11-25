from .template import *
import uuid
import json
class File:
    templates = {}
    def __init__(self):
        pass
        
    def addTemplate(self,input):
        """fonction pour ouvrir un fichier en mode lecture et retourner son contenu"""
        try:
            file = open(input, "r")
            content = file.read()
            title = file.name
            file.close()
            tmpId = uuid.uuid4()
            self.templates[tmpId] = Template(title, content=content)
            self.templates[tmpId].findAllVar()
        except:
            return "Error: File not found"
        
    def removeTemplate(self, key):
        """supprime un template du dictionnaire"""
        self.templates.pop(key)
        

    def clear(self):
        """vide le dictionnaire de templates"""
        self.templates = {}

    def getTemplate(self, key) -> str:
        """retourne le titre et le contenu du template"""
        return self.templates[key].title, self.templates[key].content
        
    def getAllTemplates(self):
        for key in self.templates:
            print(key, self.getTemplate(key))
  
    def replaceVars(self):
        """remplace les variables par leur valeur saisie"""
        for key in self.templates.keys():
            self.templates[key].replaceVar()
        
    def getAllOutContent(self) -> str:
        """retourne le contenu de tous les templates modifiés"""
        str = ""
        for key in self.templates.keys():
            str += self.templates[key].getOutContent() +'\n'
        return str

    def getAllOutContentCli(self) -> str:
        str = self.getAllOutContent()
        str = str.replace("${_MODE_CLI_}", "")
        return str
    
    def getAllOutContentFile(self) -> str:
        str_content = self.getAllOutContent()
        lines = str_content.splitlines()
        filtered_lines = [line for line in lines if "MODE_CLI" not in line] #On parcourt toutes les lignes et si "MODE_CLI" est present on ne la garde pas
        strOut = "\n".join(filtered_lines)
        return strOut

    def sort(self):
        """trie le dictionnaire de templates en fonctions du nom du fichier"""
        self.templates = dict(sorted(self.templates.items(), key=lambda x: x[1].title))

    def checkInTemplate(self, key) -> bool:
        """vérifie si une variable est présente dans le template"""
        if key in self.templates:
            return True
        else:   
            return False
        
    def dictToJson(self) -> str:
        """Assemble les différents templates dans un seul fichier .ske au format JSON"""
        data = []        
        for key in self.templates.keys():            
            template_data = {
                "name": self.templates[key].title
            }            
            if self.templates[key].getDict() != {}: # Si le template contient des variables
                template_data["sub_templates"] = True
                template_data["variables"] = {}
                dict_data = self.templates[key].getDict()
                for var, value in dict_data.items():
                    template_data["variables"][f"${{{var}}}"] = value        
            else:
                template_data["sub_templates"] = False
                template_data["variables"] = None
            data.append(template_data)
        return json.dumps(data, indent=4)
    
    def jsonToDict(self, data, folder):
        """Transforme un fichier .ske au format JSON en dictionnaire de templates"""
        templates = json.loads(data)
        for template in templates:
            title = template["name"]
            imported = True
            #Ouvrir le fichier stocke dans /DATA/r1/name.txt
            content_file = open(f"DATA/Networks/{folder}/{title}", "r").read()
            if template["sub_templates"]:
                temp = {}
                for var, value in template["variables"].items():
                    temp[var] = value
            self.templates[uuid.uuid4()] = Template(title,content=content_file, dict=temp, imported=imported)
        return self.templates        

        


    
