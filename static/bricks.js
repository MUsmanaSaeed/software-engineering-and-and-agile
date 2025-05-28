// bricks.js - Handles brick detail panel logic

document.addEventListener('DOMContentLoaded', () => {
  // Show brick details when a row is clicked
  const rows = document.querySelectorAll('.brick-row');
  const panel = document.getElementById('brick-detail-panel');
  const actions = document.getElementById('detail-actions');
  const editLink = document.getElementById('edit-link');
  const deleteLink = document.getElementById('delete-link');
  rows.forEach(row => {
    row.addEventListener('click', function() {
      const brick = JSON.parse(this.dataset.brick);
      document.getElementById('detail-name').textContent = brick.name;
      document.getElementById('detail-manufacturer').textContent = brick.manufacturer.name;
      document.getElementById('detail-colour').textContent = brick.colour;
      document.getElementById('detail-material').textContent = brick.material;
      document.getElementById('detail-strength').textContent = brick.strength;
      document.getElementById('detail-width').textContent = brick.width;
      document.getElementById('detail-depth').textContent = brick.depth;
      document.getElementById('detail-height').textContent = brick.height;
      document.getElementById('detail-type').textContent = brick.type;
      document.getElementById('detail-voids').textContent = brick.voids;
      panel.style.display = 'block';
      if (actions && editLink && deleteLink) {
        editLink.href = `/edit_brick/${brick.id}`;
        deleteLink.href = `/delete_brick/${brick.id}`;
        actions.style.display = 'block';
      }
      // Update the URL with the selected brick ID
      const newUrl = `${window.location.pathname.replace(/\/(\d+)?$/, '')}/${brick.id}`;
      window.history.pushState({ brickId: brick.id }, '', newUrl);
      // Remove row highlighting (no-op)
    });
  });

  // On page load, if URL ends with a brick ID, show that brick's details
  // Use selected_brick_id from Flask if available
  const selectedBrickId = window.selectedBrickId !== undefined ? window.selectedBrickId : null;
  let brickId = null;
  if (selectedBrickId !== null && selectedBrickId !== 'null') {
    brickId = selectedBrickId;
  } else {
    const match = window.location.pathname.match(/\/(\d+)$/);
    if (match) {
      brickId = match[1];
    }
  }
  if (brickId) {
    const row = document.querySelector(`.brick-row[data-id='${brickId}']`);
    if (row) {
      row.click();
      panel.scrollIntoView({ behavior: 'smooth', block: 'center' });
    } else {
      panel.style.display = 'none';
      if (actions) actions.style.display = 'none';
    }
  } else {
    panel.style.display = 'none';
    if (actions) actions.style.display = 'none';
  }
});

// Handle browser back/forward navigation
window.addEventListener('popstate', (event) => {
  const panel = document.getElementById('brick-detail-panel');
  const actions = document.getElementById('detail-actions');
  const match = window.location.pathname.match(/\/(\d+)$/);
  if (match) {
    const brickId = match[1];
    const row = document.querySelector(`.brick-row[data-id='${brickId}']`);
    if (row) {
      row.click();
    }
  } else {
    panel.style.display = 'none';
    if (actions) actions.style.display = 'none';
  }
});
