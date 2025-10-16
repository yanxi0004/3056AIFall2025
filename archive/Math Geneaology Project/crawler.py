import requests
from bs4 import BeautifulSoup
import csv

def check_math_genealogy_id(id):
    url = f"https://genealogy.math.ndsu.nodak.edu/id.php?id={id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.title.string if soup.title else ""
        if " - The Mathematics Genealogy Project" in title:
            name = title.split(' - The Mathematics Genealogy Project')[0].strip()
            return name, url
        else:
            return None, url
    except requests.RequestException:
        return None, url

def generate_spreadsheet(start_id, end_id, filename='math_genealogy.csv'):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Link', 'Name'])  # Header
        
        for id in range(start_id, end_id + 1):
            name, link = check_math_genealogy_id(id)
            if name:
                writer.writerow([link, name])
            else:
                writer.writerow([link, ''])  # If no name found, leave name column blank

# Example usage
start_id = 16848  # Example starting ID
end_id = 16850    # Example ending ID, adjust as needed
generate_spreadsheet(start_id, end_id)