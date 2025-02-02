from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import os

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--remote-debugging-port=9222')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")
options.add_argument("--disable-features=SameSiteByDefaultCookies,CookiesWithoutSameSiteMustBeSecure")
options.add_argument("--enable-javascript")

driver = webdriver.Chrome(options=options)

def extract_projects():
    driver.get("https://app.bricks.co/login")

    try:
        # Attendre que le champ email soit présent
        wait = WebDriverWait(driver, 10)
        email_input = wait.until(EC.presence_of_element_located((By.NAME, "email")))
        password_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))

        # Remplir les champs email et mot de passe
        email_input.clear()
        email_input.send_keys("dialldialldiall@gmail.com")

        password_input.clear()
        password_input.send_keys("Karerucl56")

        # Cliquer sur le bouton avec title="Se connecter"
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@title='Se connecter']")))
        login_button.click()

        # Attendre que la page d'accueil soit chargée (titre = "Accueil")
        wait.until(EC.title_is("Accueil"))

        # Cliquer sur le lien contenant le span avec le texte "Propriétés"
        properties_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[span[text()='Propriétés']]")))
        properties_link.click()

        # Charger les propriétés
        time.sleep(5)
        properties = driver.find_elements(By.CSS_SELECTOR, "div.w-\\[320px\\]")

        # Charger les données existantes du CSV
        data = []
        csv_file = "properties.csv"
        if os.path.exists(csv_file):
            try:
                data = pd.read_csv(csv_file).to_dict(orient="records")
            except Exception as e:
                print(f"Erreur lors de la lecture du fichier CSV : {e}")

        # Scraper les propriétés
        for index, property_card in enumerate(properties):
            try:
                url = property_card.find_element(By.TAG_NAME, "a").get_attribute("href")
                if any(d["url"] == url for d in data):
                    continue

                name = property_card.find_element(By.CSS_SELECTOR, "div.w-full.truncate").text
                price_text = property_card.find_element(By.XPATH, ".//div[contains(text(),'€')]").text
                price = ''.join(filter(str.isdigit, price_text))
                duration = property_card.find_element(By.XPATH, ".//span[(contains(text(),'ans') or contains(text(),'mois') or contains(text(),'1 an'))]").text
                taux_rentabilite = property_card.find_element(By.XPATH, ".//span[contains(text(), '% /an')]").text
                status = property_card.find_element(By.XPATH, ".//span[contains(@color, 'black')]").text

                data.append({
                    "url": url,
                    "nom": name,
                    "prix": price,
                    "duree": duration,
                    "taux_rentabilite": taux_rentabilite,
                    "status": status
                })

                # Scroll progressif
                if (index + 1) % 9 == 0:
                    driver.execute_script("window.scrollBy(0, window.innerHeight * 1.2);")
                    time.sleep(2)

            except Exception as e:
                print(f"Erreur lors de l'extraction des données : {e}")

        # Exporter les données consolidées
        if data:
            print(data)
            df = pd.DataFrame(data)
            df.to_csv(csv_file, index=False)
            print(f"Données exportées dans {csv_file}")
        return data

    except Exception as e:
        print(f"Erreur lors de la connexion : {e}")
        driver.quit()
        return []

def navigate_to_projects(projects):
    try:
        wait = WebDriverWait(driver, 10)

        # Créer le dossier DOM s'il n'existe pas
        if not os.path.exists('DOM'):
            os.makedirs('DOM')

        # Parcourir chaque projet
        for project in projects:
            time.sleep(5)
            # Chercher la carte avec le href correspondant au projet
            project_id = project['url'].split('/')[-1]
            print(f"ID du projet : {project_id}")
            project_card = wait.until(EC.presence_of_element_located((By.XPATH, f"//a[contains(@href, '/properties/{project_id}')]")))

            # Récupérer la position Y de la carte
            location_y = project_card.location['y']

            # Scroll jusqu'à la position de la carte
            driver.execute_script(f"window.scrollTo(0, {location_y - 100});")
            time.sleep(2)

            # Cliquer sur la carte
            project_card.click()
            time.sleep(2)

            print(f"URI actuel : {driver.current_url}")

            # Créer un dossier pour le projet
            project_dir = f"DOM/{project_id}"
            if not os.path.exists(project_dir):
                os.makedirs(project_dir)

            # Sauvegarder le DOM général
            general_dom_path = f"{project_dir}/general.html"
            with open(general_dom_path, 'w', encoding='utf-8') as file:
                file.write(driver.page_source)
                print(f"DOM général sauvegardé dans {general_dom_path}")

            # Chercher et cliquer sur l'onglet "Finance"
            try:
                time.sleep(3)
                finance_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Finance')]")))
                finance_tab.click()
                time.sleep(2)

                # Sauvegarder le DOM de l'onglet finance
                finance_dom_path = f"{project_dir}/finance.html"
                with open(finance_dom_path, 'w', encoding='utf-8') as file:
                    file.write(driver.page_source)
                    print(f"DOM de finance sauvegardé dans {finance_dom_path}")
            except Exception as e:
                print(f"Erreur lors de la navigation vers l'onglet finance : {e}")

            # Chercher et cliquer sur l'onglet "Lieu"
            try:
                time.sleep(3)
                location_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Lieu')]")))
                location_tab.click()
                time.sleep(2)

                # Sauvegarder le DOM de l'onglet lieu
                location_dom_path = f"{project_dir}/lieu.html"
                with open(location_dom_path, 'w', encoding='utf-8') as file:
                    file.write(driver.page_source)
                    print(f"DOM de lieu sauvegardé dans {location_dom_path}")
            except Exception as e:
                print(f"Erreur lors de la navigation vers l'onglet lieu : {e}")

            # Vérification des fichiers
            saved_files = os.listdir(project_dir)
            if len(saved_files) == 3:
                print(f"Tous les fichiers sont présents pour {project_id} : {saved_files}")
            else:
                print(f"Fichiers manquants pour {project_id}, trouvés : {saved_files}")

            # Revenir à la page des projets
            back_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[span[contains(text(), 'Retour')]]")))
            back_button.click()
            time.sleep(2)

    except Exception as e:
        print(f"Erreur lors de la navigation vers les projets : {e}")

# Utilisation de la fonction
projects_data = extract_projects()
if projects_data:
    navigate_to_projects(projects_data)

# Attente pour vérifier l'affichage
time.sleep(10)