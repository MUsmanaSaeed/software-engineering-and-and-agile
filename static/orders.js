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
                    attachCancelButtonLogic();
                    attachAddOrderButtonLogic();
                    attachMarkReceivedLogic();
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

    function attachMarkReceivedLogic() {
        document.querySelectorAll('.btn-order-received').forEach(function(button) {
            button.onclick = function () {
                var orderId = this.getAttribute('data-order-id');
                var bricksOrdered = this.getAttribute('data-bricks-ordered');
                var modal = document.getElementById('receivedBricksModal');
                document.getElementById('receivedOrderIdInput').value = orderId;
                var input = document.getElementById('bricksReceivedInput');
                input.value = bricksOrdered;
                input.max = bricksOrdered;
                modal.classList.add('active');
                setTimeout(function() { input.focus(); }, 200);
            };
        });
        var form = document.getElementById('receivedBricksForm');
        if (form) {
            form.onsubmit = function(e) {
                e.preventDefault();
                var orderId = document.getElementById('receivedOrderIdInput').value;
                var bricksReceived = document.getElementById('bricksReceivedInput').value;
                var modal = document.getElementById('receivedBricksModal');
                var formData = new FormData();
                formData.append('bricks_received', bricksReceived);
                fetch('/orders/received/' + orderId, {
                    method: 'POST',
                    body: formData,
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        modal.classList.remove('active');
                        // Refresh order detail panel only
                        if (typeof selectedOrderNo !== 'undefined') {
                            fetch(ORDER_DETAIL_URL.replace('ORDER_NO_PLACEHOLDER', selectedOrderNo), {
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
                                    attachCancelButtonLogic();
                                    attachAddOrderButtonLogic();
                                    attachMarkReceivedLogic();
                                }
                            });
                        }
                    } else {
                        // Show flash message dynamically
                        modal.classList.remove('active');
                        var flashContainer = document.querySelector('.floating-flash-container');
                        if (flashContainer) {
                            var alertDiv = document.createElement('div');
                            alertDiv.className = 'alert alert-danger alert-dismissible fade show';
                            alertDiv.role = 'alert';
                            alertDiv.style.animation = 'flash-in 0.4s';
                            alertDiv.innerHTML = data.error + '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>';
                            flashContainer.appendChild(alertDiv);
                            setTimeout(function() {
                                alertDiv.classList.remove('show');
                                alertDiv.classList.add('hide');
                                setTimeout(function() { alertDiv.remove(); }, 500);
                            }, 4000);
                        } else {
                            alert(data.error);
                        }
                    }
                });
            };
        }
        var modal = document.getElementById('receivedBricksModal');
        var cancelBtn = document.getElementById('receivedModalNo');
        if (cancelBtn) {
            cancelBtn.onclick = function() {
                modal.classList.remove('active');
            };
        }
        // Close modal when clicking outside dialog
        if (modal) {
            modal.onclick = function(e) {
                if (e.target === modal) {
                    modal.classList.remove('active');
                }
            };
        }
    }
    attachCancelButtonLogic();
    attachAddOrderButtonLogic();
    attachMarkReceivedLogic();

    // Set min/max for ordered_date and disable other dates
    const addOrderModal = document.getElementById('addOrderModal');
    if (addOrderModal) {
        addOrderModal.addEventListener('show.bs.modal', function () {
            const orderedDateInput = document.getElementById('ordered_date');
            const expectedDateInput = document.getElementById('expected_date');
            if (orderedDateInput) {
                const today = new Date();
                const yyyy = today.getFullYear();
                const mm = String(today.getMonth() + 1).padStart(2, '0');
                const dd = String(today.getDate()).padStart(2, '0');
                const todayStr = `${yyyy}-${mm}-${dd}`;
                const minDate = new Date(today);
                minDate.setDate(today.getDate() - 3);
                const minY = minDate.getFullYear();
                const minM = String(minDate.getMonth() + 1).padStart(2, '0');
                const minD = String(minDate.getDate()).padStart(2, '0');
                const minStr = `${minY}-${minM}-${minD}`;
                orderedDateInput.setAttribute('max', todayStr);
                orderedDateInput.setAttribute('min', minStr);
                orderedDateInput.value = todayStr;
                // Disable all other dates
                orderedDateInput.addEventListener('input', function() {
                    if (this.value < minStr || this.value > todayStr) {
                        this.setCustomValidity('Order date must be within the last 3 days and not in the future.');
                    } else {
                        this.setCustomValidity('');
                    }
                    // Update expected date min when ordered date changes
                    if (expectedDateInput) {
                        expectedDateInput.setAttribute('min', this.value);
                        if (expectedDateInput.value < this.value) {
                            expectedDateInput.value = this.value;
                        }
                    }
                });
                // Set initial min for expected date
                if (expectedDateInput) {
                    expectedDateInput.setAttribute('min', orderedDateInput.value);
                    if (expectedDateInput.value < orderedDateInput.value) {
                        expectedDateInput.value = orderedDateInput.value;
                    }
                }
            }
        });
    }
});
