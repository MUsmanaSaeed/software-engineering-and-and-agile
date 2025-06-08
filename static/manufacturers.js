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

// Manufacturer auto-selection and URL sync for manufacturers page

document.addEventListener('DOMContentLoaded', function() {
    const rows = document.querySelectorAll('.manufacturer-row');
    const panel = document.getElementById('manufacturer-detail-panel');
    const actions = document.getElementById('detail-m-actions');
    const editLink = document.getElementById('edit-m-link');
    const deleteLink = document.getElementById('delete-m-link');

    // --- Auto-select manufacturer if /manufacturers/(id) is in URL ---
    const pathMatch = window.location.pathname.match(/^\/manufacturers\/(\d+)/);
    const selectedId = pathMatch ? pathMatch[1] : null;
    if (selectedId) {
        const row = Array.from(rows).find(r => r.dataset.id === selectedId);
        if (row) row.click();
    }
    // --- End auto-select ---

    rows.forEach(row => {
        row.addEventListener('click', function() {
            const m = JSON.parse(this.dataset.manufacturer);
            // Update URL to /manufacturers/{id} without reloading
            const newUrl = `/manufacturers/${m.id}`;
            if (!window.location.pathname.startsWith('/manufacturers') || window.location.pathname !== newUrl) {
                window.history.pushState({}, '', newUrl);
            }
            document.getElementById('detail-m-name').textContent = m.name;
            document.getElementById('detail-m-address').textContent = m.address;
            document.getElementById('detail-m-phone').textContent = m.phoneNo || '';
            document.getElementById('detail-m-email').textContent = m.email || '';
            // Bricks list
            const brickList = document.getElementById('detail-m-bricks');
            brickList.innerHTML = '';
            if (m.bricks && m.bricks.length > 0) {
                m.bricks.forEach(function(b) {
                    const li = document.createElement('li');
                    li.className = 'list-group-item';
                    li.textContent = b.name;
                    brickList.appendChild(li);
                });
            } else {
                const li = document.createElement('li');
                li.className = 'list-group-item';
                li.textContent = 'No bricks.';
                brickList.appendChild(li);
            }
            panel.style.display = 'block';
            if (actions && editLink && deleteLink) {
                editLink.href = `/edit_manufacturer/${m.id}`;
                // Instead of direct link, set up modal trigger
                deleteLink.setAttribute('data-bs-toggle', 'modal');
                deleteLink.setAttribute('data-bs-target', '#deleteModal');
                deleteLink.setAttribute('data-id', m.id);
                deleteLink.setAttribute('data-name', m.name);
                actions.style.display = 'block';
            }
        });
    });
});
