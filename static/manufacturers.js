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
