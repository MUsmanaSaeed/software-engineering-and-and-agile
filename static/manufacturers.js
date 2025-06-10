let deleteId = null;
const deleteModal = document.getElementById('deleteModal');
const manufacturerBricks = JSON.parse(document.getElementById('manufacturerBricksData').textContent);
deleteModal.addEventListener('show.bs.modal', function (event) {
  const button = event.relatedTarget;
  deleteId = button.getAttribute('data-id');
  const name = button.getAttribute('data-name');
  document.getElementById('manufacturerName').textContent = name;
  const bricksList = document.getElementById('bricksList');
  bricksList.innerHTML = '';
  if (manufacturerBricks[deleteId] && manufacturerBricks[deleteId].length > 0) {
    manufacturerBricks[deleteId].forEach(function(brickName) {
      const li = document.createElement('li');
      li.className = 'list-group-item list-group-item-danger py-1';
      li.textContent = brickName;
      bricksList.appendChild(li);
    });
  } else {
    const li = document.createElement('li');
    li.className = 'list-group-item';
    li.textContent = 'No bricks.';
    bricksList.appendChild(li);
  }
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
            // Bricks list
            const brickList = document.getElementById('detail-m-bricks');
            brickList.innerHTML = '';
            if (m.bricks && m.bricks.length > 0) {
                m.bricks.forEach(function(b) {
                    const btn = document.createElement('a');
                    btn.className = 'btn btn-outline-primary btn-sm shadow-sm d-flex align-items-center justify-content-between brick-link-btn';
                    btn.textContent = b.name;
                    btn.href = `/bricks/${b.id}`;
                    btn.style.width = '100%';
                    btn.style.textAlign = 'left';
                    btn.style.borderRadius = '0.5rem';
                    btn.style.fontWeight = '500';
                    btn.style.letterSpacing = '0.02em';
                    btn.style.transition = 'background 0.2s, color 0.2s, box-shadow 0.2s';
                    btn.style.padding = '0.4rem 0.75rem';
                    // Add a right arrow icon
                    const icon = document.createElement('i');
                    icon.className = 'bi bi-arrow-right ms-auto';
                    btn.appendChild(icon);
                    // Add hover effect
                    btn.onmouseover = function() {
                        btn.classList.add('btn-primary');
                        btn.classList.remove('btn-outline-primary');
                        btn.style.color = '#fff';
                        btn.style.boxShadow = '0 2px 8px rgba(0,123,255,0.15)';
                    };
                    btn.onmouseout = function() {
                        btn.classList.remove('btn-primary');
                        btn.classList.add('btn-outline-primary');
                        btn.style.color = '';
                        btn.style.boxShadow = '';
                    };
                    brickList.appendChild(btn);
                });
            } else {
                const span = document.createElement('span');
                span.className = 'text-muted';
                span.textContent = 'No bricks.';
                brickList.appendChild(span);
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
            // Bricks list
            const brickList = document.getElementById('detail-m-bricks');
            brickList.innerHTML = '';
            if (m.bricks && m.bricks.length > 0) {
                m.bricks.forEach(function(b) {
                    const btn = document.createElement('a');
                    btn.className = 'btn btn-outline-primary btn-sm shadow-sm d-flex align-items-center justify-content-between brick-link-btn';
                    btn.textContent = b.name;
                    btn.href = `/bricks/${b.id}`;
                    btn.style.width = '100%';
                    btn.style.textAlign = 'left';
                    btn.style.borderRadius = '0.5rem';
                    btn.style.fontWeight = '500';
                    btn.style.letterSpacing = '0.02em';
                    btn.style.transition = 'background 0.2s, color 0.2s, box-shadow 0.2s';
                    btn.style.padding = '0.4rem 0.75rem';
                    btn.style.marginBottom = '0.10rem'; // Even less spacing
                    // Add a right arrow icon
                    const icon = document.createElement('i');
                    icon.className = 'bi bi-arrow-right ms-auto';
                    btn.appendChild(icon);
                    // Add hover effect
                    btn.onmouseover = function() {
                        btn.classList.add('btn-primary');
                        btn.classList.remove('btn-outline-primary');
                        btn.style.color = '#fff';
                        btn.style.boxShadow = '0 2px 8px rgba(0,123,255,0.15)';
                    };
                    btn.onmouseout = function() {
                        btn.classList.remove('btn-primary');
                        btn.classList.add('btn-outline-primary');
                        btn.style.color = '';
                        btn.style.boxShadow = '';
                    };
                    brickList.appendChild(btn);
                });
            } else {
                const span = document.createElement('span');
                span.className = 'text-muted';
                span.textContent = 'No bricks.';
                brickList.appendChild(span);
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

// --- Brick search for manufacturer detail panel ---
const brickSearchBox = document.getElementById('brick-search-box');
if (brickSearchBox) {
    brickSearchBox.addEventListener('input', function() {
        const filter = this.value.trim().toLowerCase();
        const brickList = document.getElementById('detail-m-bricks');
        if (!brickList) return;
        // Use the bricks from the currently selected manufacturer row
        // Find the selected manufacturer row (active)
        const activeRow = document.querySelector('.manufacturer-row.active');
        let bricks = [];
        if (activeRow) {
            const m = JSON.parse(activeRow.dataset.manufacturer);
            bricks = m.bricks || [];
        }
        // Save all bricks for future filtering
        brickList._allBricks = bricks;
        // Filter bricks
        const filtered = bricks.filter(b => b.name.toLowerCase().includes(filter));
        brickList.innerHTML = '';
        if (filtered.length > 0) {
            filtered.forEach(function(b) {
                const btn = document.createElement('a');
                btn.className = 'btn btn-outline-primary btn-sm shadow-sm d-flex align-items-center justify-content-between brick-link-btn';
                btn.textContent = b.name;
                btn.href = `/bricks/${b.id}`;
                btn.style.width = '100%';
                btn.style.textAlign = 'left';
                btn.style.borderRadius = '0.5rem';
                btn.style.fontWeight = '500';
                btn.style.letterSpacing = '0.02em';
                btn.style.transition = 'background 0.2s, color 0.2s, box-shadow 0.2s';
                btn.style.padding = '0.4rem 0.75rem';
                // Add a right arrow icon
                const icon = document.createElement('i');
                icon.className = 'bi bi-arrow-right ms-auto';
                btn.appendChild(icon);
                // Add hover effect
                btn.onmouseover = function() {
                    btn.classList.add('btn-primary');
                    btn.classList.remove('btn-outline-primary');
                    btn.style.color = '#fff';
                    btn.style.boxShadow = '0 2px 8px rgba(0,123,255,0.15)';
                };
                btn.onmouseout = function() {
                    btn.classList.remove('btn-primary');
                    btn.classList.add('btn-outline-primary');
                    btn.style.color = '';
                    btn.style.boxShadow = '';
                };
                brickList.appendChild(btn);
            });
        } else {
            const div = document.createElement('div');
            div.className = 'w-100 d-flex flex-column align-items-center justify-content-center py-3';
            div.innerHTML = `
                <i class="bi bi-box text-secondary mb-2" style="font-size: 2rem;"></i>
                <span class="text-muted fw-semibold" style="font-size: 1.08rem;">No bricks found</span>
            `;
            brickList.appendChild(div);
        }
    });
}
