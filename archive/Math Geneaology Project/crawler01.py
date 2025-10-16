import requests
from bs4 import BeautifulSoup
import csv

def check_math_genealogy_id(id):
    url = f"https://genealogy.math.ndsu.nodak.edu/id.php?id={id}"
    try:
        response = requests.get(url, timeout=10)  # Timeout to prevent hanging on slow responses
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.title.string if soup.title else ""
        if " - The Mathematics Genealogy Project" in title:
            name = title.split(' - The Mathematics Genealogy Project')[0].strip()
            return name, url, True  # Valid entry
        else:
            return None, url, False  # Invalid or not a person entry
    except requests.RequestException:
        return None, url, False  # Treat connection errors as invalid

def generate_spreadsheet():
    with open('math_genealogy_all.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Link', 'Name', 'Status'])  # Header
        
        invalid_count = 0
        for id in range(1, 50001):  # Check IDs from 1 to 50,000
            name, link, valid = check_math_genealogy_id(id)
            if valid:
                writer.writerow([link, name, 'Valid'])
            else:
                writer.writerow([link, '', 'Invalid'])
                invalid_count += 1
            
            if invalid_count > 100:
                print(f"Stopped at ID {id} after finding {invalid_count} invalid links.")
                break

if __name__ == "__main__":
    generate_spreadsheet()