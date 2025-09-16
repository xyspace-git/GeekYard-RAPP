document.addEventListener('DOMContentLoaded', function () {
    const itemList = document.getElementById('item-list');
    const addItemBtn = document.getElementById('add-item-btn');

    function createItemRow() {
        const itemRow = document.createElement('div');
        itemRow.classList.add('item-row');
        
        
        itemRow.innerHTML = `
            <select name="item_type" class="item-type-select">
                <option value="service" selected>Service</option>
                <option value="item">Item</option>
            </select>
            <input type="text" name="item_desc" placeholder="Description" required>
            <div class="input-wrapper hours-input">
                <input type="number" name="item_hours" class="small-input" placeholder="Hours" step="0.1">
            </div>
            <div class="input-wrapper qty-input" style="display: none;">
                <input type="number" name="item_quantity" class="small-input" placeholder="Qty" step="1">
            </div>
            <input type="number" name="item_price" class="small-input" placeholder="Price" step="0.01" required>
            <button type="button" class="remove-item-btn">×</button>
        `;
        
        itemList.appendChild(itemRow);

        const typeSelect = itemRow.querySelector('.item-type-select');
        const hoursInputDiv = itemRow.querySelector('.hours-input');
        const qtyInputDiv = itemRow.querySelector('.qty-input');
        const hoursInput = hoursInputDiv.querySelector('input');
        const qtyInput = qtyInputDiv.querySelector('input');

        typeSelect.addEventListener('change', function() {
            if (this.value === 'service') {
                hoursInputDiv.style.display = 'block';
                qtyInputDiv.style.display = 'none';
                hoursInput.required = true; 
                qtyInput.required = false; 
                qtyInput.value = '';       
            } else {
                hoursInputDiv.style.display = 'none';
                qtyInputDiv.style.display = 'block';
                hoursInput.required = false; 
                qtyInput.required = true;   
                hoursInput.value = '';     
            }
        });

      
        typeSelect.dispatchEvent(new Event('change'));

        itemRow.querySelector('.remove-item-btn').addEventListener('click', function() {
            itemRow.remove();
        });
    }

    
    createItemRow();

    addItemBtn.addEventListener('click', createItemRow);
});
