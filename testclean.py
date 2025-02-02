import os
from bs4 import BeautifulSoup

def clean_html(file_path, output_file, project_id):
    try:
        # Lire le contenu du fichier HTML
        with open(file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

        # Conserver uniquement <div id="root">
        root_div = soup.find('div', {'id': 'root'})

        # Créer un nouveau BeautifulSoup pour ne conserver que <div id="root">
        new_soup = BeautifulSoup("", 'html.parser')
        if root_div:
            new_soup.append(root_div.extract())

        # Supprimer les balises <script>, <svg>, <path>, <header>
        for tag in new_soup.find_all(['script', 'svg', 'path', 'header']):
            tag.decompose()
        
        # Supprimer la première div contenant le texte ciblé
        baseDom = new_soup.find('main', class_='grow bg-gray-thin')
        if baseDom:
            target_div = baseDom.find('div', {'color': 'black', 'size': '14'})
            if target_div:
                target_div.decompose()
        
        # Vérifier la présence de la div "Actualités" et supprimer son 3ème parent
        actualites_div = new_soup.find('div', {'color': 'black'}, string='Actualités')
        if actualites_div:
            parent = actualites_div
            for _ in range(4):
                if parent:
                    parent = parent.find_parent()
            if parent:
                parent.decompose()
                print("Actualités et sa section parente supprimées !")

        # Vérifier si le span avec "Contrat" existe
        contrat_span = new_soup.find('span', {'color': 'black'}, string="Contrat")
        if contrat_span:
            output_file = os.path.join("CCDOM", project_id, "general.html")

        # Vérifier si le dossier de sortie existe, sinon le créer
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # Écrire le HTML nettoyé dans un nouveau fichier
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(new_soup.prettify())

        print(f"✅ HTML nettoyé et sauvegardé dans {output_file}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage du fichier HTML {file_path} : {e}")
        return None

# Répertoire source et destination
DOM_DIR = "DOM"
CLEANED_DOM_DIR = "CDOM"

# Vérifier si DOM existe
if not os.path.exists(DOM_DIR):
    print(f"❌ Le dossier {DOM_DIR} n'existe pas !")
else:
    # Boucler sur les sous-dossiers (ID des biens)
    for property_id in os.listdir(DOM_DIR):
        property_path = os.path.join(DOM_DIR, property_id)
        
        # Vérifier si c'est bien un dossier
        if os.path.isdir(property_path):
            general_html_path = os.path.join(property_path, "general.html")
            
            # Vérifier si le fichier general.html existe dans le dossier du bien
            if os.path.exists(general_html_path):
                cleaned_path = os.path.join(CLEANED_DOM_DIR, property_id, "general.html")
                
                # Lancer le nettoyage du fichier HTML
                clean_html(general_html_path, cleaned_path, property_id)
            else:
                print(f"⚠️ Aucun fichier general.html trouvé pour {property_id}")
