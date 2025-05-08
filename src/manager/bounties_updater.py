import requests

def bounties(bounty_path="data/bounties.csv"):
    url = "https://docs.google.com/spreadsheets/d/1WKHbT-7KOgjEawq5h5Ic1qUWzpfAzuD_J06N1JwOCGs/export?format=csv&gid=0"
    response = requests.get(url)
    if response.status_code == 200: 
        with open(bounty_path, "wb") as f:
            f.write(response.content)
        return True
    return False