let deleteId = null;
const deleteModal = document.getElementById('deleteModal');
deleteModal.addEventListener('show.bs.modal', function (event) {
  const button = event.relatedTarget;
  deleteId = button.getAttribute('data-id');
  const name = button.getAttribute('data-name');
  document.getElementById('manufacturerName').textContent = name;
  const bricksList = document.getElementById('bricksList');
  bricksList.innerHTML = '';
  setTimeout(function() {
    document.getElementById('cancelBtn').focus();
  }, 200);
});
document.getElementById('confirmDeleteBtn').onclick = function() {
  if (deleteId) {
    window.location.href = "/delete_manufacturer/" + deleteId;
  }
};

document.addEventListener('DOMContentLoaded', function() {
    const rows = document.querySelectorAll('.manufacturer-row');
    const panel = document.getElementById('manufacturer-detail-panel');
    const actions = document.getElementById('detail-m-actions');
    const editLink = document.getElementById('edit-m-link');
    const deleteLink = document.getElementById('delete-m-link');

    // --- Auto-select manufacturer if selectedManufacturerId or /manufacturers/(id) is in URL ---
    let manufacturerId = null;
    // Use selectedManufacturerId from Flask if available
    const selectedManufacturerId = window.selectedManufacturerId !== undefined ? window.selectedManufacturerId : null;
    if (selectedManufacturerId !== null && selectedManufacturerId !== 'null') {
        manufacturerId = selectedManufacturerId;
    } else {
        // Only match /manufacturers/{id} for manufacturer page
        const match = window.location.pathname.match(/\/manufacturers\/(\d+)$/);
        if (match) {
            manufacturerId = match[1];
        }
    }
    if (manufacturerId) {
        // Find the row and select it without setTimeout
        const row = document.querySelector(`.manufacturer-row[data-id='${manufacturerId}']`);
        if (row) {
            // Remove active class from all rows
            rows.forEach(r => r.classList.remove('active'));
            // Add active class to selected row
            row.classList.add('active');
            // Populate the detail panel as in the click handler
            const m = JSON.parse(row.dataset.manufacturer);
            const newUrl = `/manufacturers/${m.id}`;
            if (!window.location.pathname.startsWith('/manufacturers') || window.location.pathname !== newUrl) {
                window.history.pushState({}, '', newUrl);
            }
            document.getElementById('detail-m-name').textContent = m.name;
            document.getElementById('detail-m-address').textContent = m.address;
            document.getElementById('detail-m-phone').textContent = m.phoneNo || '';
            document.getElementById('detail-m-email').textContent = m.email || '';
            // Set edit link href
            if (editLink) {
                editLink.href = `/edit_manufacturer/${m.id}`;
            }
            panel.style.display = 'block';
            if (document.getElementById('manufacturer-placeholder-panel')) {
                document.getElementById('manufacturer-placeholder-panel').classList.add('d-none');
            }
        } else {
            if (panel) panel.style.display = 'none';
            if (actions) actions.style.display = 'none';
            if (document.getElementById('manufacturer-placeholder-panel')) {
                document.getElementById('manufacturer-placeholder-panel').classList.remove('d-none');
            }
        }
    } else {
        if (panel) panel.style.display = 'none';
        if (actions) actions.style.display = 'none';
        if (document.getElementById('manufacturer-placeholder-panel')) {
            document.getElementById('manufacturer-placeholder-panel').classList.remove('d-none');
        }
    }
    // --- End auto-select ---

    rows.forEach(row => {
        row.addEventListener('click', function() {
            // Remove active class from all rows
            rows.forEach(r => r.classList.remove('active'));
            // Add active class to selected row
            this.classList.add('active');
            const m = JSON.parse(this.dataset.manufacturer);
            const newUrl = `/manufacturers/${m.id}`;
            if (!window.location.pathname.startsWith('/manufacturers') || window.location.pathname !== newUrl) {
                window.history.pushState({}, '', newUrl);
            }
            document.getElementById('detail-m-name').textContent = m.name;
            document.getElementById('detail-m-address').textContent = m.address;
            document.getElementById('detail-m-phone').textContent = m.phoneNo || '';
            document.getElementById('detail-m-email').textContent = m.email || '';
            // Set edit link href
            if (editLink) {
                editLink.href = `/edit_manufacturer/${m.id}`;
            }
            panel.style.display = 'block';
            if (document.getElementById('manufacturer-placeholder-panel')) {
                document.getElementById('manufacturer-placeholder-panel').classList.add('d-none');
            }
            // Instead of direct link, set up modal trigger
            deleteLink.setAttribute('data-bs-toggle', 'modal');
            deleteLink.setAttribute('data-bs-target', '#deleteModal');
            deleteLink.setAttribute('data-id', m.id);
            deleteLink.setAttribute('data-name', m.name);
            actions.style.display = 'block';
        });
    });
});

// Search/filter functionality for manufacturers table
const manufacturerSearchBox = document.getElementById('manufacturer-search-box');
if (manufacturerSearchBox) {
  manufacturerSearchBox.addEventListener('input', function() {
    const filter = this.value.trim().toLowerCase();
    document.querySelectorAll('.manufacturer-row').forEach(row => {
      const name = row.querySelector('td:nth-child(1)').textContent.toLowerCase();
      if (name.includes(filter)) {
        row.style.display = '';
      } else {
        row.style.display = 'none';
      }
    });
  });
}
