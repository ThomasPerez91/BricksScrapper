from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# Configuration de ChromeOptions
chrome_options = Options()
chrome_options.add_argument("--headless")  # Exécution en mode sans interface graphique
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Initialisation du WebDriver
service = ChromeService(executable_path="/usr/local/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # Accès à une page de test
    driver.get("https://www.google.com")
    time.sleep(2)  # Pause pour s'assurer que la page est bien chargée

    # Recherche du champ de recherche et envoi d'une requête
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys("Selenium Python")
    search_box.submit()

    time.sleep(2)  # Pause pour observer les résultats

    # Vérification des résultats
    results = driver.find_elements(By.CSS_SELECTOR, 'h3')
    if results:
        print(f"Test réussi : {len(results)} résultats trouvés.")
    else:
        print("Test échoué : Aucun résultat trouvé.")

except Exception as e:
    print(f"Erreur lors du test Selenium : {e}")

finally:
    driver.quit()