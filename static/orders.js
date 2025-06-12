document.addEventListener('DOMContentLoaded', function() {
    var detailTitle = document.querySelector('.order-detail-title');
    if (detailTitle) {
        var match = detailTitle.textContent.match(/Order No:\s*(\S+)/);
        if (match) {
            selectedOrderNo = match[1];
        }
    }

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
            selectedOrderNo = orderNo; // Set selected order number
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
                    // Re-attach Add Order button logic
                    attachAddOrderButtonLogic();
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

    function attachAddOrderButtonLogic() {
        // Only attach to Add Order button in the detail panel
        document.querySelectorAll('.order-detail-add-btn').forEach(function(btn) {
            btn.addEventListener('click', function() {
                var orderNoInput = document.getElementById('orderNo');
                if (orderNoInput) {
                    orderNoInput.value = selectedOrderNo;
                }
            });
        });
        // Also clear orderNo when main Add Order button is clicked
        var mainAddOrderBtn = document.querySelector('.btn-primary[data-bs-target="#addOrderModal"]');
        if (mainAddOrderBtn) {
            mainAddOrderBtn.addEventListener('click', function() {
                var orderNoInput = document.getElementById('orderNo');
                if (orderNoInput) {
                    orderNoInput.value = '';
                }
            });
        }
    }

    // At the end of DOMContentLoaded, also call it for initial load
    attachCancelButtonLogic();
    attachAddOrderButtonLogic();

    // Set default ordered_date to today when Add Order modal is shown
    const addOrderModal = document.getElementById('addOrderModal');
    if (addOrderModal) {
        addOrderModal.addEventListener('show.bs.modal', function () {
            const orderedDateInput = document.getElementById('ordered_date');
            if (orderedDateInput) {
                const today = new Date();
                const yyyy = today.getFullYear();
                const mm = String(today.getMonth() + 1).padStart(2, '0');
                const dd = String(today.getDate()).padStart(2, '0');
                orderedDateInput.value = `${yyyy}-${mm}-${dd}`;
            }
        });
    }
});
