import io
import os
import uuid
from flask import Flask, render_template, request, redirect, send_file, url_for, flash
from .Back.file import File
from .Back.gestion import getChild
from werkzeug.utils import secure_filename

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
    current_directory = os.getcwd()
    print(current_directory)
    print(folders)
    """ Affiche le formulaire et le fichier téléchargé """
    if request.method == "POST":
        uploaded_file = request.files.get("file")
        numberTemplates = request.form.get("templates")
        if uploaded_file:
            if allowed_file(uploaded_file.filename, "txt"): # On vérifie qu'il s'agit d'un fichier txt
                uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)) # On sauvegarde le fichier
                for i in range(int(numberTemplates)):
                    file_manager.addTemplate(os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)) # On ajoute le fichier au gestionnaire de fichiers
                file_manager.sort() # On trie les fichiers dans l'ordre alphabétique
                print("Fichier ajouté")
            else:
                print("Le fichier doit être au format .txt")
        return render_template("load.html", templates=file_manager.templates, folders=folders)
    file_manager.clear() # On vide le gestionnaire de fichiers
    return render_template("base.html")

@app.route("/delete", methods=["POST"])
def delete_file():
    """ Supprime un fichier """
    print("Fichier supprimé")
    key = uuid.UUID(request.args.get("key"))
    if file_manager.checkIntemplate(key):
        file_manager.removeTemplate(key)
    if file_manager.templates == {}:
        return render_template("base.html", folders=folders)
    else :
        return render_template("load.html", templates=file_manager.templates, folders=folders)
    
@app.route("/generate", methods=["POST"])
def complete_file():
    """ Génère le fichier de sortie """
    if file_manager.templates == {}:
        return render_template("base.html")
    for key in file_manager.templates.keys(): # Pour chaque clé dans le dictionnaire de templates
        template = file_manager.templates[key] # On recupère le template associé
        allVar = template.getAllVar()
        for var in allVar:
            value = request.form.get(str(key)+"_"+var) # On récupère la valeur associée à la clé et à la variable
            template.setVar(var, value) # On stocke la valeur saisie
    file_manager.replaceVars() # On remplace les variables par leur valeur saisie
    return render_template("generate.html", text=file_manager.getAllOutContent(), folders=folders)

@app.route('/download')
def download():
    text_content = file_manager.getAllOutContent()
    return send_file(io.BytesIO(text_content.encode()), 
                     mimetype='text/plain', 
                     as_attachment=True, 
                     download_name='conf.ske')

@app.route('/export')
def export():
    text_content = file_manager.dictToJson()
    return send_file(io.BytesIO(text_content.encode()), 
                     mimetype='text/plain', 
                     as_attachment=True, 
                     download_name='conf.txt')

@app.route('/import', methods=["POST"])
def import_file():
    """ Importe un fichier de configuration """
    uploaded_file = request.files.get("file")
    if uploaded_file:
        if allowed_file(uploaded_file.filename, "ske"):
            #appelle la fonction de file.py qui transforme le contenu du fichier en dictionnaire
            file_manager.jsonToDict(uploaded_file.read().decode(), folder="R1")
            return render_template("import.html", templates=file_manager.templates, folders=folders)
    return render_template("base.html", folders=folders)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER) #permer de créer le dossier Uploads s'il n'existe pas encore

    app.run(debug=True)
