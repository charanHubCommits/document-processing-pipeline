import re

def extract_fields(text):
    data = {}

    # Name
    name_match = re.search(r"(Name|Narne):\s*(.*)", text)
    data['name'] = name_match.group(1).strip() if name_match else None

    # Amount
    amount_match = re.search(r"Amount:\s*(\d+)", text)
    data['amount'] = amount_match.group(1) if amount_match else None

    # Date
    date_match = re.search(r"Date:\s*([\d/]+)", text)
    data['date'] = date_match.group(1) if date_match else None

    # ID
    id_match = re.search(r"ID:\s*(\w+)", text)
    data['id'] = id_match.group(1) if id_match else None

    return data