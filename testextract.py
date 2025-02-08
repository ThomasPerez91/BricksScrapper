import json
import os
import re
from bs4 import BeautifulSoup

def clean_text(text):
    """Nettoie le texte en supprimant les retours à la ligne et les espaces inutiles."""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)  # Remplace tous les espaces multiples par un seul espace
    return text.strip()  # Supprime les espaces en début et fin de chaîne

def extract_general_datas(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

        extracted_data = {}

        # Charger la balise <main>
        baseDom = soup.find('main', class_='grow bg-gray-thin')
        if baseDom:
            # Trouver la première div enfant avec direction=row
            first_column_div = baseDom.find('div', attrs={'direction': 'column'})
            if first_column_div:
                first_row_div = first_column_div.find('div', attrs={'direction': 'row'})
                if first_row_div:
                    second_column_div = first_row_div.find('div', attrs={'direction': 'column'})
                    if second_column_div:
                       spans = second_column_div.find_all('span', {'color': 'black'})
                       if len(spans) > 1:
                            extracted_data['adresse'] = clean_text(spans[1].get_text())
                    
            child_divs = first_column_div.find_all('div', recursive=False)
            third_div_child = child_divs[3] if len(child_divs) > 3 else None
            if third_div_child:
                first_w_full_div = third_div_child.find('div', class_='w-full')
                if first_w_full_div:
                    nested_column_div = first_w_full_div.find('div', class_='w-full', attrs={'direction': 'column'})
                    if nested_column_div:
                        second_child_div = nested_column_div.find_all('div', recursive=False)
                        second_child_div = second_child_div[1] if len(second_child_div) > 1 else None
                        if second_child_div:
                            column_div = second_child_div.find('div', attrs={'direction': 'column'})
                            if column_div:
                                first_child_div = column_div.find('div')
                                if first_child_div:
                                    inner_child_div = first_child_div.find_all('div', recursive=False)
                                    first_child_div = inner_child_div[0] if len(inner_child_div) > 0 else None
                                    second_child_div = inner_child_div[1] if len(inner_child_div) > 1 else None
                                    if first_child_div:
                                        next_inner_div = first_child_div.find('div', attrs={'direction': 'column'})
                                        if next_inner_div:
                                            inner_div = next_inner_div.find_all('div', recursive=False)
                                            first_inner_div = inner_div[0] if len(inner_div) > 0 else None
                                            second_inner_div = inner_div[1] if len(inner_div) > 1 else None
                                            if first_inner_div:
                                                inner_child_div = first_inner_div.find_all('div', recursive=False)
                                                inner_child_div = inner_child_div[1] if len(inner_child_div) > 1 else None
                                                if inner_child_div:
                                                    inner_span = inner_child_div.find_all('span', recursive=False)
                                                    first_inner_span = inner_span[0] if len(inner_span) > 0 else None
                                                    extracted_data['type_taux'] = clean_text(first_inner_span.get_text())
                                            if second_inner_div:
                                                remboursement_span = second_inner_div.find('span', {'color': 'black'})
                                                if remboursement_span:
                                                    extracted_data['type_remboursement_interet'] = clean_text(remboursement_span.get_text())
                                    if second_child_div:
                                        next_inner_div = second_child_div.find('div', attrs={'direction': 'column'})
                                        if next_inner_div:
                                            inner_div = next_inner_div.find_all('div', recursive=False)
                                            second_inner_div = inner_div[1] if len(inner_div) > 1 else None
                                            if second_inner_div:
                                                remboursement_span = second_inner_div.find('span', {'color': 'black'})
                                                if remboursement_span:
                                                    extracted_data['type_remboursement_capital'] = clean_text(remboursement_span.get_text())
                                        
        cles_div = baseDom.find('div', {'color': 'black'}, string=lambda text: text and "Les points clés" in text)
        if cles_div:
            parent_div = cles_div.find_parent()
            if parent_div:
                link = parent_div.find('a')
                if link:
                    extracted_data['lien_points_cles'] = link.get('href')
                all_spans = parent_div.find_all('span')
                titles = []
                descriptions = []
                    
                for span in all_spans:
                    if span.get('color') == 'black':
                        titles.append(span.get_text(strip=True))
                    elif span.get('color') == 'gray-primary':
                        descriptions.append(span.get_text(strip=True))
                
                for i, (title, description) in enumerate(zip(titles, descriptions), start=1):
                    extracted_data[f'point_cle_titre_{i}'] = clean_text(title)
                    extracted_data[f'point_cle_description_{i}'] = clean_text(description)

        presentation_div = baseDom.find('div', {'color': 'black'}, string=lambda text: text and "Présentation" in text)
        if presentation_div:
            parent_div = presentation_div.find_parent()
            if parent_div:
                all_spans = parent_div.find_all('span')
                lot_span = all_spans[0] if len(all_spans) > 0 else None
                surface_span = all_spans[2] if len(all_spans) > 2 else None
                presentation_span = all_spans[3] if len(all_spans) > 3 else None
                if lot_span:
                    extracted_data['lot'] = clean_text(lot_span.get_text())
                if surface_span:
                    extracted_data['surface'] = clean_text(surface_span.get_text()).replace("m 2", "m²")
                if presentation_span:
                    presentation_div = presentation_span.find('div')
                    if presentation_div:
                        elements = presentation_div.find_all(['p', 'ul'], recursive=False)  # Récupérer les <p> et <ul>
                        current_title = None
                        title_count = 0
                        description_text = []

                        for element in elements:
                            # Si élément est un <p> contenant <strong><u>, c'est un titre
                            strong_u_tag = element.find('strong')
                            if strong_u_tag and strong_u_tag.find('u'):
                                # Sauvegarde l'ancien titre et ses descriptions avant de passer au suivant
                                if current_title and description_text:
                                    extracted_data[f'presentation_titre_{title_count}'] = current_title
                                    extracted_data[f'presentation_description_{title_count}'] = ' '.join(description_text)
                                    description_text = []

                                # Définir le nouveau titre
                                title_count += 1
                                current_title = clean_text(strong_u_tag.find('u').get_text())

                            # Si l'élément est un <p> contenant du texte brut et ce n'est pas un titre, c'est une description
                            elif element.text.strip() and not element.find('br'):
                                description_text.append(clean_text(element.text.strip()))

                            # Si l'élément est une liste <ul>, ajouter chaque <li> comme description
                            elif element.name == 'ul':
                                for li in element.find_all('li'):
                                    description_text.append(clean_text(li.get_text()))

                        # Sauvegarde de la dernière section
                        if current_title and description_text:
                            extracted_data[f'presentation_titre_{title_count}'] = current_title
                            extracted_data[f'presentation_description_{title_count}'] = ' '.join(description_text)

        analyse_div = baseDom.find('div', {'color': 'black'}, string=lambda text: text and "Éléments clés de l'analyse" in text)
        if analyse_div:
            parent_div = analyse_div
            for _ in range(3):
                if parent_div:
                    parent_div = parent_div.find_parent()
                    if parent_div:
                        ul_element = parent_div.find('ul', class_='css-i6zvb9')
                        if ul_element:
                            li_elements = ul_element.find_all('li', class_='css-1y34dmg')
                            for i, li in enumerate(li_elements, start=1):
                                title_div = li.find('div', class_='mb-2 css-1tt8cjm')  # Récupérer la div contenant le titre
                                description_span = li.find('span', class_='css-nw50hi')  # Récupérer le span contenant la description
                                if title_div:
                                    extracted_data[f'analyse_titre_{i}'] = clean_text(title_div.get_text())
                                if description_span:
                                    extracted_data[f'analyse_description_{i}'] = clean_text(description_span.get_text())

        document_div = baseDom.find('div', {'color': 'black'}, string=lambda text: text and "Documents" in text)
        if document_div:
            parent_div = document_div.find_parent()
            if parent_div:
                document_anchors = parent_div.find_all('a', href=True)
                print(document_anchors)

                for index, anchor in enumerate(document_anchors, start=1):
                    title = anchor.get_text(strip=True)
                    href = anchor['href']

                    if title and href:
                        extracted_data[f"document_titre_{index}"] = title
                        extracted_data[f"document_lien_{index}"] = href

        return extracted_data
    except Exception as e:
        print(f"Erreur lors de l'extraction des données : {e}")
        return None

# Répertoire contenant les fichiers nettoyés
CDOM_DIR = "CDOM"

datas = extract_general_datas('CDOM/0cabe831-37c4-45cf-9956-06f28eb260f2/general.html')
print(json.dumps(datas, indent=4, ensure_ascii=False))
