from .template import *
import uuid
import json
class File:
    templates = {}
    def __init__(self):
        pass
        
    def addTemplate(self,content, title):
        """fonction pour ouvrir un fichier en mode lecture et retourner son contenu"""
        id = uuid.uuid4()
        self.templates[id] = Template(title, content=content)
        self.templates[id].findAllVar()
        
    def removeTemplate(self, key):
        """supprime un template du dictionnaire"""
        self.templates.pop(key)
        
    def clear(self):
        """vide le dictionnaire de templates"""
        self.templates = {}

    def getTemplate(self, key) -> str:
        """retourne le titre et le contenu du template"""
        return self.templates[key].title, self.templates[key].content
  
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
    
    def jsonToDict(self, templates, folder) -> dict:
        """Transforme une liste de dictionnaire (JSON) en dictionnaire d'objet de type templates"""
        for template in templates:
            temp = {}
            title = template["name"]
            content_file = open(f"DATA/{folder}/{title}", "r").read()
            if template["sub_templates"]:
                for var, value in template["variables"].items():
                    var = re.findall(r"\$\{([^}]+)\}", var)[0]
                    temp[var] = value
            self.templates[uuid.uuid4()] = Template.fromJson(title,content=content_file, dict=temp)
        return self.templates         

    def importVar(self,key,file):
        """fonction pour importer les variables d'un fichier"""
        self.templates[key].imported = True
        json_data = json.loads(file)
        for var in json_data:
            self.templates[key].setVar(var,json_data[var])

    
