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
                    attachCancelButtonLogic(); // Re-attach cancel logic after panel update
                }
            });
        });
    });

    function attachCancelButtonLogic() {
        var modal = document.getElementById('cancelConfirmModal');
        if (!modal) return;
        var newModal = modal.cloneNode(true);
        modal.parentNode.replaceChild(newModal, modal);
        document.querySelectorAll('.btn-order-cancel').forEach(function (button) {
            button.onclick = function () {
                var orderId = this.getAttribute('data-order-id');
                var modal = document.getElementById('cancelConfirmModal');
                if (modal) modal.classList.add('active');
                var modalYes = document.getElementById('cancelModalYes');
                var modalNo = document.getElementById('cancelModalNo');
                if (modalYes) {
                    modalYes.onclick = function() {
                        var form = document.querySelector('.cancel-order-form [data-order-id="'+orderId+'"]')?.closest('form');
                        modal.classList.remove('active');
                        if (form) form.submit();
                    };
                }
                if (modalNo) {
                    modalNo.onclick = function() {
                        modal.classList.remove('active');
                    };
                }
                newModal.onclick = function(e) {
                    if (e.target === newModal) {
                        newModal.classList.remove('active');
                    }
                };
            };
        });
    }

    // At the end of DOMContentLoaded, also call it for initial load
    attachCancelButtonLogic();
});
