from datetime import datetime

def validate_data(data):
    errors = []

    # Name validation
    if not data.get('name'):
        errors.append("Missing name")

    # Amount validation
    try:
        amount = int(data.get('amount'))
        if amount <= 0:
            errors.append("Amount must be greater than 0")
    except:
        errors.append("Invalid amount")

    # Date validation
    try:
        datetime.strptime(data.get('date'), "%d/%m/%Y")
    except:
        errors.append("Invalid date format (DD/MM/YYYY expected)")

    # ID validation
    if not data.get('id'):
        errors.append("Missing ID")

    # Final status
    if len(errors) == 0:
        return {"status": "VALID", "errors": []}
    else:
        return {"status": "INVALID", "errors": errors}