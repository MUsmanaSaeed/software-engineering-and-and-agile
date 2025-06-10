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
            populateBricksList(m.id);
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

    // --- Helper: Populate Bricks List for Manufacturer ---
    function populateBricksList(manufacturerId) {
        const bricksList = document.getElementById('manufacturer-bricks-list');
        const bricksDataScript = document.getElementById('manufacturerBricksData');
        if (!bricksList || !bricksDataScript) return;
        const bricksData = JSON.parse(bricksDataScript.textContent);
        let manufacturerRow = document.querySelector(`.manufacturer-row[data-id='${manufacturerId}']`);
        let brickObjs = [];
        if (manufacturerRow) {
            let m = JSON.parse(manufacturerRow.dataset.manufacturer);
            // m.bricks is an array of brick objects (if available)
            brickObjs = m.bricks || [];
        }
        const searchValue = (document.getElementById('brick-search-box')?.value || '').trim().toLowerCase();
        bricksList.innerHTML = '';
        let filtered = brickObjs.filter(b => b.name.toLowerCase().includes(searchValue));
        if (filtered.length === 0) {
            const li = document.createElement('li');
            li.className = 'list-group-item text-center text-muted py-4 border-0';
            li.innerHTML = `
                <div class="d-flex flex-column align-items-center justify-content-center">
                  <i class="bi bi-box" style="font-size: 2rem; opacity: 0.5;"></i>
                  <div class="mt-2 fw-semibold">No bricks found</div>
                </div>
            `;
            bricksList.appendChild(li);
        } else {
            filtered.forEach(brick => {
                const li = document.createElement('li');
                li.className = 'list-group-item p-0 border-0';
                const btn = document.createElement('a');
                btn.className = 'btn btn-outline-primary btn-sm w-100 text-start bricks-outline-btn my-1';
                btn.href = `/bricks/${brick.id}`;
                btn.textContent = brick.name;
                li.appendChild(btn);
                bricksList.appendChild(li);
            });
        }
    }

    // --- Update bricks list on manufacturer select ---
    function handleManufacturerSelect(m) {
        document.getElementById('detail-m-name').textContent = m.name;
        document.getElementById('detail-m-address').textContent = m.address;
        document.getElementById('detail-m-phone').textContent = m.phoneNo || '';
        document.getElementById('detail-m-email').textContent = m.email || '';
        if (editLink) {
            editLink.href = `/edit_manufacturer/${m.id}`;
        }
        panel.style.display = 'block';
        if (document.getElementById('manufacturer-placeholder-panel')) {
            document.getElementById('manufacturer-placeholder-panel').classList.add('d-none');
        }
        populateBricksList(m.id);
    }

    // --- Patch auto-select logic to update bricks list ---
    if (manufacturerId) {
        const row = document.querySelector(`.manufacturer-row[data-id='${manufacturerId}']`);
        if (row) {
            rows.forEach(r => r.classList.remove('active'));
            row.classList.add('active');
            const m = JSON.parse(row.dataset.manufacturer);
            const newUrl = `/manufacturers/${m.id}`;
            if (!window.location.pathname.startsWith('/manufacturers') || window.location.pathname !== newUrl) {
                window.history.pushState({}, '', newUrl);
            }
            handleManufacturerSelect(m);
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

    // --- Patch row click logic to update bricks list ---
    rows.forEach(row => {
        row.addEventListener('click', function() {
            rows.forEach(r => r.classList.remove('active'));
            this.classList.add('active');
            const m = JSON.parse(this.dataset.manufacturer);
            const newUrl = `/manufacturers/${m.id}`;
            if (!window.location.pathname.startsWith('/manufacturers') || window.location.pathname !== newUrl) {
                window.history.pushState({}, '', newUrl);
            }
            handleManufacturerSelect(m);
            // Instead of direct link, set up modal trigger
            deleteLink.setAttribute('data-bs-toggle', 'modal');
            deleteLink.setAttribute('data-bs-target', '#deleteModal');
            deleteLink.setAttribute('data-id', m.id);
            deleteLink.setAttribute('data-name', m.name);
            actions.style.display = 'block';
        });
    });

    // --- Bricks search box logic ---
    const brickSearchBox = document.getElementById('brick-search-box');
    if (brickSearchBox) {
        brickSearchBox.addEventListener('input', function() {
            // Find selected manufacturer id
            let selectedRow = document.querySelector('.manufacturer-row.active');
            let mId = selectedRow ? selectedRow.getAttribute('data-id') : manufacturerId;
            if (mId) populateBricksList(mId);
        });
    }
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
