document.addEventListener('DOMContentLoaded', function() {
    // Search filter for orders table
    const searchBox = document.getElementById('order-search-box');
    if (searchBox) {
        searchBox.addEventListener('input', function() {
            const filter = searchBox.value.trim().toLowerCase();
            document.querySelectorAll('#orders-table tbody tr').forEach(function(row) {
                const orderNo = row.textContent.trim().toLowerCase();
                row.style.display = orderNo.includes(filter) ? '' : 'none';
            });
        });
    }
    document.querySelectorAll('.order-row').forEach(function(row) {
        row.addEventListener('click', function(e) {
            if (e.target.tagName.toLowerCase() === 'a') return;
            const orderNo = row.getAttribute('data-order-no');
            let basePath = '/orders';
            window.history.pushState({}, '', `${basePath}/${orderNo}`);
            fetch(ORDER_DETAIL_URL.replace('ORDER_NO_PLACEHOLDER', orderNo), {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const detailPanel = doc.body.firstElementChild;
                if (detailPanel) {
                    document.querySelector('.col-lg-8').innerHTML = '';
                    document.querySelector('.col-lg-8').appendChild(detailPanel);
                }
            });
        });
    });

    // Custom Cancel Confirmation Popup Logic
    let cancelFormToSubmit = null;
    const modal = document.getElementById('cancelConfirmModal');
    const modalYes = document.getElementById('cancelModalYes');
    const modalNo = document.getElementById('cancelModalNo');

    document.body.addEventListener('click', function(e) {
        if (e.target.classList.contains('btn-order-cancel')) {
            e.preventDefault();
            cancelFormToSubmit = e.target.closest('form');
            if (modal) modal.style.display = 'flex';
        }
    });
    if (modalNo) {
        modalNo.onclick = function() {
            modal.style.display = 'none';
            cancelFormToSubmit = null;
        };
    }
    if (modalYes) {
        modalYes.onclick = function() {
            if (cancelFormToSubmit) {
                modal.style.display = 'none';
                cancelFormToSubmit.submit();
                cancelFormToSubmit = null;
            }
        };
    }
    // Hide modal if clicking outside content
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                modal.style.display = 'none';
                cancelFormToSubmit = null;
            }
        });
    }
});
