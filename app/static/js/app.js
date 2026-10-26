// Hospital Management System - Frontend helpers

document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        document.querySelectorAll('.alert-dismissible').forEach(function(alert) {
            var bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        });
    }, 5000);

    // Confirm dangerous actions
    document.querySelectorAll('[data-confirm]').forEach(function(el) {
        el.addEventListener('click', function(e) {
            if (!confirm(this.getAttribute('data-confirm'))) {
                e.preventDefault();
            }
        });
    });

    // Dynamic bill item rows
    var addItemBtn = document.getElementById('add-bill-item');
    if (addItemBtn) {
        addItemBtn.addEventListener('click', function() {
            var container = document.getElementById('bill-items');
            var row = document.createElement('div');
            row.className = 'row g-2 mb-2 bill-item-row';
            row.innerHTML = `
                <div class="col-md-4"><input type="text" name="item_desc[]" class="form-control form-control-sm" placeholder="Description" required></div>
                <div class="col-md-2">
                    <select name="item_type[]" class="form-select form-select-sm">
                        <option>Consultation</option><option>Lab</option><option>Medicine</option>
                        <option>Procedure</option><option>Room</option><option>Other</option>
                    </select>
                </div>
                <div class="col-md-2"><input type="number" name="item_qty[]" class="form-control form-control-sm" value="1" min="1"></div>
                <div class="col-md-2"><input type="number" name="item_price[]" class="form-control form-control-sm" placeholder="Price" step="0.01" required></div>
                <div class="col-md-2"><button type="button" class="btn btn-sm btn-outline-danger remove-item"><i class="bi bi-trash"></i></button></div>
            `;
            container.appendChild(row);
            row.querySelector('.remove-item').addEventListener('click', function() {
                row.remove();
            });
        });
    }

    // Prescription med rows
    var addMedBtn = document.getElementById('add-med-item');
    if (addMedBtn) {
        addMedBtn.addEventListener('click', function() {
            var container = document.getElementById('med-items');
            var row = document.createElement('div');
            row.className = 'row g-2 mb-2';
            row.innerHTML = `
                <div class="col-md-3"><input type="text" name="med_name[]" class="form-control form-control-sm" placeholder="Medicine"></div>
                <div class="col-md-2"><input type="text" name="med_dosage[]" class="form-control form-control-sm" placeholder="Dosage"></div>
                <div class="col-md-2"><input type="text" name="med_freq[]" class="form-control form-control-sm" placeholder="1-0-1"></div>
                <div class="col-md-2"><input type="text" name="med_duration[]" class="form-control form-control-sm" placeholder="5 days"></div>
                <div class="col-md-1"><input type="number" name="med_qty[]" class="form-control form-control-sm" value="1"></div>
                <div class="col-md-2"><button type="button" class="btn btn-sm btn-outline-danger remove-med"><i class="bi bi-trash"></i></button></div>
            `;
            container.appendChild(row);
            row.querySelector('.remove-med').addEventListener('click', function() {
                row.remove();
            });
        });
    }
});
