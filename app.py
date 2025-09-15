import datetime
import json
from flask import Flask, render_template, request, abort, redirect, url_for

app = Flask(__name__)

# --- CONFIGURATION ---
CURRENCY = "₹" 
COUNTER_FILE = 'receipt_count.txt'
RECEIPTS_FILE = 'receipts.json'

# --- Helper functions ---
def read_counter():
    try:
        with open(COUNTER_FILE, 'r') as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 1

def write_counter(number):
    with open(COUNTER_FILE, 'w') as f:
        f.write(str(number))

def load_receipts():
    try:
        with open(RECEIPTS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_receipts(receipts):
    with open(RECEIPTS_FILE, 'w') as f:
        json.dump(receipts, f, indent=4)

receipt_number_counter = read_counter()


# --- NEW: Reusable function to process form data for both generating and updating receipts ---
def process_form_data(form):
    """Processes form data from a request and returns a dictionary."""
    data = {
        'customer_name': form.get('customer_name'),
        'customer_email': form.get('customer_email'),
        'payment_method': form.get('payment_method'),
        'note': form.get('custom_note'),
        'line_items': [],
        'total': 0.0
    }
    
    item_types = form.getlist('item_type')
    item_descs = form.getlist('item_desc')
    item_hours = form.getlist('item_hours')
    item_quantities = form.getlist('item_quantity')
    item_prices = form.getlist('item_price')
    
    total_amount = 0
    
    for i in range(len(item_descs)):
        try:
            price = float(item_prices[i])
            line_item = {"description": item_descs[i]}
            
            if item_types[i] == 'service' and item_hours[i]:
                hours = float(item_hours[i])
                amount = hours * price
                line_item.update({"hours": hours, "quantity": None, "unit_value": hours})
            elif item_types[i] == 'item' and item_quantities[i]:
                quantity = int(item_quantities[i])
                amount = quantity * price
                line_item.update({"hours": None, "quantity": quantity, "unit_value": quantity})
            else:
                continue

            total_amount += amount
            line_item.update({
                "price": f"{price:,.2f}", 
                "amount": f"{amount:,.2f}"
            })
            data['line_items'].append(line_item)
        except (ValueError, IndexError):
            continue
            
    data['total'] = f"{total_amount:,.2f}"
    return data


# --- Routes ---

@app.route('/')
def home():
    """Renders the main menu page."""
    return render_template('home.html')

@app.route('/new')
def new_receipt_form():
    """Renders the form to create a new receipt."""
    return render_template('index.html')

@app.route('/receipts')
def list_receipts():
    """Displays a list of all saved receipts, with optional search."""
    all_receipts = load_receipts()
    search_query = request.args.get('query', '')
    if search_query:
        filtered_receipts = []
        for receipt in all_receipts:
            if search_query.lower() in receipt['customer_name'].lower() or \
               search_query in receipt['receipt_no']:
                filtered_receipts.append(receipt)
        all_receipts = filtered_receipts
    sorted_receipts = sorted(all_receipts, key=lambda r: r['receipt_no'], reverse=True)
    return render_template('receipt_list.html', receipts=sorted_receipts, query=search_query)

@app.route('/receipt/<receipt_no>')
def view_receipt(receipt_no):
    """Displays a specific receipt from the saved data."""
    all_receipts = load_receipts()
    receipt = next((r for r in all_receipts if r['receipt_no'] == receipt_no), None)
    if receipt is None:
        abort(404)
    return render_template('receipt.html', data=receipt)

# This function now uses the helper function, but its core logic is unchanged.
@app.route('/generate', methods=['POST'])
def generate_receipt():
    """Processes form data, saves the receipt, and displays it."""
    global receipt_number_counter
    
    processed_data = process_form_data(request.form)
    
    current_receipt_number = receipt_number_counter
    receipt_data = {
        "receipt_no": f"{current_receipt_number:06d}",
        "date": datetime.date.today().strftime("%d %B, %Y"),
        "from_name": "Madhavan S",
        "from_extra": "Geek Yard - XSN",
        "from_email": "Network.xyspace@gmail.com",
        "currency": CURRENCY,
        **processed_data  # Unpacks the processed data into this dictionary
    }
    
    all_receipts = load_receipts()
    all_receipts.append(receipt_data)
    save_receipts(all_receipts)
    
    receipt_number_counter += 1
    write_counter(receipt_number_counter)
    
    # Redirect to the view page for the newly created receipt
    return redirect(url_for('view_receipt', receipt_no=receipt_data['receipt_no']))


# --- NEW LOGIC: Route to show the edit form ---
@app.route('/edit/<receipt_no>')
def edit_receipt_form(receipt_no):
    all_receipts = load_receipts()
    receipt = next((r for r in all_receipts if r['receipt_no'] == receipt_no), None)
    if receipt is None:
        abort(404)
    return render_template('edit_receipt.html', receipt=receipt)

# --- NEW LOGIC: Route to process the updated data ---
@app.route('/update/<receipt_no>', methods=['POST'])
def update_receipt(receipt_no):
    all_receipts = load_receipts()
    # Find the index of the receipt we are updating
    receipt_index = next((i for i, r in enumerate(all_receipts) if r['receipt_no'] == receipt_no), None)
    
    if receipt_index is None:
        abort(404)
        
    # Get the original receipt data
    original_receipt = all_receipts[receipt_index]
    # Process the new form data
    processed_data = process_form_data(request.form)
    
    # Update the original receipt dictionary with the new data
    original_receipt.update(processed_data)
    
    # Save the modified list back to the file
    all_receipts[receipt_index] = original_receipt
    save_receipts(all_receipts)
    
    return redirect(url_for('list_receipts'))

# --- NEW LOGIC: Route to delete a receipt ---
@app.route('/delete/<receipt_no>', methods=['POST'])
def delete_receipt(receipt_no):
    all_receipts = load_receipts()
    # Create a new list that excludes the receipt to be deleted
    receipts_to_keep = [r for r in all_receipts if r['receipt_no'] != receipt_no]
    
    if len(all_receipts) == len(receipts_to_keep):
        abort(404) # Abort if the receipt ID was not found
        
    save_receipts(receipts_to_keep)
    return redirect(url_for('list_receipts'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)