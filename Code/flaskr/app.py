import io
import os
from openpyxl import load_workbook
import uuid
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from .Back.file import File
from .Back.gestion import getChild
from .Back.adapter import Adapter
import json

# Configurations
UPLOAD_FOLDER = 'DATA/Uploads'


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
folders = getChild("Data/Networks")

# Vérification de l'extension du fichier
def allowed_file(filename, ext):
    """ Vérifie que l'extension du fichier correspond à celle attendue """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == ext
   
file_manager = File()
@app.route("/", methods=["GET", "POST"])
def upload_file():
    """ Affiche le formulaire et le fichier téléchargé """
    if request.method == "POST":
        uploaded_file = request.files.get("file")
        numberTemplates = request.form.get("templates")
        if uploaded_file:
            if allowed_file(uploaded_file.filename, "txt"): # On vérifie qu'il s'agit d'un fichier txt
                file_content = uploaded_file.read().decode("utf-8")
                for _ in range(int(numberTemplates)):
                    file_manager.addTemplate(file_content, uploaded_file.filename) # On ajoute le fichier au gestionnaire de fichiers
                file_manager.sort() # On trie les fichiers dans l'ordre alphabétique
            else:
                print("Le fichier doit être au format .txt")
        return render_template("load.html", templates=file_manager.templates, folders=folders)
    file_manager.clear() # On vide le gestionnaire de fichiers
    return render_template("base.html")

@app.route("/update",methods=["POST"])
def update_file():
    """ Met à jour un fichier """
    key = uuid.UUID(request.form.get("key"))
    uploaded_file = request.files.get("file")
    file_manager.importVar(key, uploaded_file.read().decode("utf-8"))
    return render_template("load.html", templates=file_manager.templates, folders=folders)

@app.route("/delete", methods=["POST"])
def delete_file():
    """ Supprime un fichier """
    print("Fichier supprimé")
    key = uuid.UUID(request.args.get("key"))
    if file_manager.checkInTemplate(key):
        file_manager.removeTemplate(key)
    if file_manager.templates == {}:
        return render_template("base.html", folders=folders)
    else :
        return render_template("load.html", templates=file_manager.templates, folders=folders)
    
@app.route("/generate", methods=["POST", "GET"])
def complete_file():
    """ Génère le fichier de sortie """
    if file_manager.templates == {}:
        return render_template("base.html")
    if request.method == "POST":
        for key in file_manager.templates.keys(): # Pour chaque clé dans le dictionnaire de templates
            template = file_manager.templates[key] # On recupère le template associé
            allVar = template.getDict()
            for var in allVar:
                value = request.form.get(str(key)+"_"+var) # On récupère la valeur associée à la clé et à la variable
                template.setVar(var, value) # On stocke la valeur saisie
        file_manager.replaceVars() # On remplace les variables par leur valeur saisie
        return render_template("generate.html", text=file_manager.getAllOutContentFile(), folders=folders)
    elif request.method == "GET":
        type = request.args.get("type")
        if type == "Cli":
            return render_template("generate.html", text=file_manager.getAllOutContentCli(), folders=folders)
        if type == "File":
            return render_template("generate.html", text=file_manager.getAllOutContentFile(), folders=folders)
    else:
        return render_template("base.html")

def download(content, name):
    return send_file(io.BytesIO(content.encode()), 
                     mimetype='text/plain', 
                     as_attachment=True, 
                     download_name=name)

@app.route('/downloadFile')
def download_File(file_manager):
    text_content = file_manager.getAllOutContentFile()
    return download(text_content, 'confFile.txt')

@app.route('/downloadCli')
def download_Cli():
    text_content = file_manager.getAllOutContentCli()
    return download(text_content, 'confCli.txt')

@app.route('/export')
def export():
    text_content = file_manager.dictToJson()
    return send_file(io.BytesIO(text_content.encode()), 
                     mimetype='text/plain', 
                     as_attachment=True, 
                     download_name='conf.ske')

@app.route('/import', methods=["POST"])
def import_file():
    """ Importe un fichier de configuration """
    uploaded_file = request.files.get("file")
    if uploaded_file:
        if allowed_file(uploaded_file.filename, "ske"):
            #appelle la fonction de file.py qui transforme le contenu du fichier en dictionnaire
            file_manager.jsonToDict(json.loads(uploaded_file.read().decode()), folder="Networks/R1")
            return render_template("load.html", templates=file_manager.templates, folders=folders)
    return render_template("base.html", folders=folders)

@app.route('/patch', methods=["POST"])
def generate_patch():
    """genere un fichier de patch pour les vlan d'acces à partir du plan vlan"""
    listTemp = []
    temp = File()
    if request.method == "POST":
        uploaded_file = request.files.get("file")
        if uploaded_file: #On verifie si un fichier a été uploadé
            print("Fichier uploadé")
            filename = secure_filename(uploaded_file.filename)
            if allowed_file(filename, "xlsm"):
                uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'temp.xlsm')) #On a besoin de sauvegarder temporairement le fichier pour openpyxl
        wb = load_workbook(os.path.join(app.config['UPLOAD_FOLDER'], 'temp.xlsm')) #On charge le fichier
        Excl = Adapter(wb) 
        distribution_list = Excl.getDistributionList() #On recupere la liste de la colonne A(Distribution)
        dist = request.form.get("Distribution") #On recupere la distribution selectionné
        if dist is None: #Si aucune distribution n'est selectionné on prend la premiere de la liste
            dist = distribution_list[0]
        switchType = request.form.get("SwitchType") #On recupere le type de switch selectionné
        if switchType == "Distrib": #Si le switch est de type distribution on recupere les variables correspondantes
            for row in Excl.getRowByDistribution(dist): #On recupere les numéros de ligne qui possede le bon A (distribution)
                listTemp.append(Excl.getDistributionVlanVarInet(row))
        else : 
            for row in Excl.getRowByDistribution(dist): 
                listTemp.append(Excl.getAccessVlanVar(row))
        print("listTemp : ", listTemp)
        temp.jsonToDict(listTemp,folder="Uploads")
        temp.replaceVars()
        typeOut = request.form.get("type")
        if typeOut == "Cli":
            textOut = temp.getAllOutContentCli()
        else:
            textOut = temp.getAllOutContentFile()
        return render_template("patch.html", distribution_list = distribution_list, text=textOut) 
    

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER) #permer de créer le dossier Uploads s'il n'existe pas encore
    app.run(debug=True)


""" 
listTemp = []
temp = File()
for row in Excl.getRowByDistribution('Ouest-1'): #On recupere les lignes qui contiennent la distribution Ouest-1
    listTemp.append(Excl.getAccessVlanVar(row))
temp.jsonToDict(listTemp,folder="Uploads")
temp.replaceVars()
return download(temp.getAllOutContentFile(), 'PatchVlanAccess.txt') """