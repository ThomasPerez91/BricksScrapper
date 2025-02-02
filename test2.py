from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--remote-debugging-port=9222')
options.add_argument('--headless=new')  # Nouveau mode headless plus stable
options.add_argument('--window-size=1920,1080')  # Résolution d'écran pour éviter les soucis d'affichage
options.add_argument('--disable-blink-features=AutomationControlled')  # Camouflage Selenium
options.add_argument('--enable-javascript')  # Activer JavaScript
options.add_argument('--disable-extensions')  # Désactiver les extensions
options.add_argument('--disable-infobars')  # Supprimer les barres d'infos
options.add_argument('--disable-software-rasterizer')  # Désactiver le rasteriseur logiciel
options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36')

prefs = {"profile.managed_default_content_settings.images": 2}
options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=options)
driver.get("https://app.bricks.co/login")

try:
    wait = WebDriverWait(driver, 20)  # Augmentation du délai d'attente
    email_input = wait.until(EC.presence_of_element_located((By.NAME, "email")))
    password_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))

    email_input.clear()
    email_input.send_keys("dialldialldiall@gmail.com")

    password_input.clear()
    password_input.send_keys("Karerucl56")

    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@title='Se connecter']")))
    login_button.click()

    print("Connexion tentée.")

    wait.until(EC.title_is("Accueil"))
    print("Page d'accueil chargée.")

    properties_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[span[text()='Propriétés']]")))
    properties_link.click()
    print("Clic sur 'Propriétés' effectué.")

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)  # Temps d'attente plus long pour le chargement

    properties = driver.find_elements(By.CSS_SELECTOR, "div.w-\\[320px\\]")
    data = []

    for index, property_card in enumerate(properties):
        try:
            url = property_card.find_element(By.TAG_NAME, "a").get_attribute("href")
            name = property_card.find_element(By.CSS_SELECTOR, "div.w-full.truncate").text
            price_text = property_card.find_element(By.XPATH, ".//div[contains(text(),'€')]").text
            price = ''.join(filter(str.isdigit, price_text))
            duration_elements = property_card.find_elements(By.XPATH, ".//span[(contains(text(),'ans') or contains(text(),'mois') or contains(text(),'1 an')) and not(contains(text(),'Financé'))]")
            duration = duration_elements[0].text if duration_elements else "Durée non spécifiée"

            data.append({
                "URL": url,
                "Nom": name,
                "Prix": price,
                "Durée": duration
            })

            if (index + 1) % 6 == 0:
                driver.execute_script("window.scrollBy(0, window.innerHeight);")
                time.sleep(2)

        except Exception as e:
            print(f"Erreur lors de l'extraction des données : {e}")


    # print data length
    print(f"Nombre de propriétés : {len(data)}")

except Exception as e:
    print(f"Erreur lors de la connexion : {e}")

print(driver.title)

time.sleep(10)

# driver.quit()
