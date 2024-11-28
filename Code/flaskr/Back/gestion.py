import os

def getChild(parent_directory):
    """ fonction retourne la liste des sous-dossiers d'un répertoire d'entrée """
    # Vérifier si le répertoire parent existe
    if not os.path.isdir(parent_directory):
        print(f"Le répertoire spécifié n'existe pas : {parent_directory}")
    childs = []
    for child in os.listdir(parent_directory):
        if os.path.isdir(os.path.join(parent_directory, child)):
            childs.append(child)
    return childs
    