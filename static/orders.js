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
                    attachEditOrderButtonLogic();
                    attachDeleteOrderButtonLogic(); // Ensure delete logic is attached after AJAX load
                }
            });
        });
    });

    function showOrderFlash(message, category = 'success') {
        var flashContainer = document.querySelector('.floating-flash-container');
        if (flashContainer) {
            var alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${category} alert-dismissible fade show`;
            alertDiv.role = 'alert';
            alertDiv.style.animation = 'flash-in 0.4s';
            alertDiv.innerHTML = message + '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>';
            flashContainer.appendChild(alertDiv);
            setTimeout(function() {
                alertDiv.classList.remove('show');
                alertDiv.classList.add('hide');
                setTimeout(function() { alertDiv.remove(); }, 500);
            }, 4000);
        }
    }

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
                        if (form) {
                            form.submit();
                            showOrderFlash('Order canceled!');
                        }
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
                        showOrderFlash('Order marked as received!');
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
                                    attachEditOrderButtonLogic(); // Re-attach edit logic after refresh
                                }
                            });
                        }
                    } else {
                        modal.classList.remove('active');
                        showOrderFlash(data.error || 'Failed to mark as received', 'danger');
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

    // Attach edit order button logic
    function attachEditOrderButtonLogic() {
        document.querySelectorAll('.btn-order-edit').forEach(function(button) {
            button.onclick = function() {
                var orderId = this.getAttribute('data-order-id');
                var orderNo = this.getAttribute('data-order-no');
                var brick = this.getAttribute('data-brick');
                var bricksOrdered = this.getAttribute('data-bricks-ordered');
                var orderedDate = this.getAttribute('data-ordered-date');
                var expectedDate = this.getAttribute('data-expected-date');
                var receivedDate = this.getAttribute('data-received-date');
                var bricksReceived = this.getAttribute('data-bricks-received');
                var isReceived = false;
                var parent = button.closest('.order-list-item');
                if (parent && parent.classList.contains('order-received-bg')) {
                    isReceived = true;
                }
                document.getElementById('editOrderId').value = orderId;
                document.getElementById('editOrderNo').value = orderNo;
                document.getElementById('editBrick').value = brick;
                document.getElementById('editBricksOrdered').value = bricksOrdered;
                document.getElementById('editOrderedDate').value = orderedDate;
                document.getElementById('editExpectedDate').value = expectedDate;
                var isReceivedInput = document.getElementById('editIsReceived');
                if (isReceivedInput) isReceivedInput.value = isReceived ? '1' : '';
                var adminFields = document.getElementById('editAdminFields');
                if (adminFields) adminFields.style.display = isReceived ? '' : 'none';
                var receivedDateGroup = document.getElementById('editReceivedDateGroup');
                var bricksReceivedGroup = document.getElementById('editBricksReceivedGroup');
                var setUnreceivedCheckbox = document.getElementById('editSetUnreceived');
                var receivedDateInput = document.getElementById('editReceivedDate');
                var bricksReceivedInput = document.getElementById('editBricksReceived');
                // Autofill received date and bricks received if received
                if (isReceived) {
                    if (receivedDateInput) {
                        receivedDateInput.value = receivedDate || '';
                        var today = new Date();
                        var yyyy = today.getFullYear();
                        var mm = String(today.getMonth() + 1).padStart(2, '0');
                        var dd = String(today.getDate()).padStart(2, '0');
                        var todayStr = `${yyyy}-${mm}-${dd}`;
                        receivedDateInput.setAttribute('min', orderedDate);
                        receivedDateInput.setAttribute('max', todayStr);
                        receivedDateInput.disabled = false;
                    }
                    if (bricksReceivedInput) {
                        bricksReceivedInput.value = bricksReceived || bricksOrdered;
                        bricksReceivedInput.disabled = false;
                    }
                } else {
                    if (receivedDateInput) {
                        receivedDateInput.value = '';
                        receivedDateInput.disabled = true;
                    }
                    if (bricksReceivedInput) {
                        bricksReceivedInput.value = '';
                        bricksReceivedInput.disabled = true;
                    }
                }
                // Hide/show received fields based on checkbox (no animation) and disable inputs if unchecked
                function toggleReceivedFields() {
                    var show = !(setUnreceivedCheckbox && setUnreceivedCheckbox.checked);
                    if (receivedDateGroup) receivedDateGroup.style.display = show ? '' : 'none';
                    if (bricksReceivedGroup) bricksReceivedGroup.style.display = show ? '' : 'none';
                    if (receivedDateInput) receivedDateInput.disabled = !show;
                    if (bricksReceivedInput) bricksReceivedInput.disabled = !show;
                }
                if (setUnreceivedCheckbox) {
                    setUnreceivedCheckbox.checked = false;
                    setUnreceivedCheckbox.onchange = toggleReceivedFields;
                }
                toggleReceivedFields();
                var modal = new bootstrap.Modal(document.getElementById('editOrderModal'));
                modal.show();
            };
        });
    }

    // --- Delete Order Modal Logic ---
    var currentOrderId = null;
    function attachDeleteOrderButtonLogic() {
        var modalEl = document.getElementById('deleteOrderModal');
        var confirmBtn = document.getElementById('confirmDeleteOrderBtn');
        // Remove any previous event handler
        if (confirmBtn) {
            confirmBtn.replaceWith(confirmBtn.cloneNode(true));
            confirmBtn = document.getElementById('confirmDeleteOrderBtn');
        }
        // Attach click handler to all delete buttons to set currentOrderId and show modal
        document.querySelectorAll('.btn-order-delete').forEach(function(button) {
            button.onclick = function() {
                currentOrderId = this.getAttribute('data-order-id');
                var modal = new bootstrap.Modal(modalEl);
                modal.show();
                // Re-bind confirm button handler for this order
                if (confirmBtn) {
                    confirmBtn.onclick = function() {
                        if (!currentOrderId) return;
                        fetch('/orders/delete/' + currentOrderId, {
                            method: 'POST',
                            headers: { 'X-Requested-With': 'XMLHttpRequest' }
                        })
                        .then(response => response.json())
                        .then(data => {
                            var modal = bootstrap.Modal.getInstance(modalEl);
                            if (modal) modal.hide();
                            if (data.success) {
                                showOrderFlash('Order deleted!');
                                if (typeof selectedOrderNo !== 'undefined') {
                                    fetch(ORDER_DETAIL_URL.replace('ORDER_NO_PLACEHOLDER', selectedOrderNo), {
                                        headers: { 'X-Requested-With': 'XMLHttpRequest' }
                                    })
                                    .then(response => response.text())
                                    .then(html => {
                                        const parser = new DOMParser();
                                        const detailPanel = parser.parseFromString(html, 'text/html').body.firstElementChild;
                                        if (detailPanel) {
                                            document.querySelector('.col-lg-8').innerHTML = '';
                                            document.querySelector('.col-lg-8').appendChild(detailPanel);
                                            reloadDetailPanel();
                                        }
                                    });
                                }
                            } else {
                                showOrderFlash(data.error || 'Failed to delete order', 'danger');
                            }
                        });
                    };
                }
            };
        });
    }

    // After loading detail panel, re-attach edit logic
    function reloadDetailPanel() {
        attachCancelButtonLogic();
        attachAddOrderButtonLogic();
        attachMarkReceivedLogic();
        attachEditOrderButtonLogic();
        attachDeleteOrderButtonLogic();
    }

    attachCancelButtonLogic();
    attachAddOrderButtonLogic();
    attachMarkReceivedLogic();
    attachEditOrderButtonLogic();
    attachDeleteOrderButtonLogic(); // Initial attach

    // Set min/max for ordered_date and disable other dates
    const addOrderModal = document.getElementById('addOrderModal');
    if (addOrderModal) {
        addOrderModal.addEventListener('show.bs.modal', function () {
            // Reset brick search and select
            if (brickSearchBox && brickSelect && allOptions) {
                brickSearchBox.value = '';
                brickSelect.innerHTML = '';
                allOptions.forEach(function(opt) {
                    var option = document.createElement('option');
                    option.value = opt.value;
                    option.textContent = opt.text;
                    brickSelect.appendChild(option);
                });
            }
            // Date logic
            const orderedDateInput = document.getElementById('ordered_date');
            const expectedDateInput = document.getElementById('expected_date');
            if (orderedDateInput && expectedDateInput) {
                // Set expected date min to ordered date on modal open
                expectedDateInput.setAttribute('min', orderedDateInput.value);
                // Update expected date min whenever ordered date changes
                orderedDateInput.addEventListener('input', function() {
                    expectedDateInput.setAttribute('min', this.value);
                    if (expectedDateInput.value < this.value) {
                        expectedDateInput.value = this.value;
                    }
                });
            }
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
                // Always set value to today when modal opens
                orderedDateInput.value = todayStr;
                // Set initial min for expected date
                if (expectedDateInput) {
                    expectedDateInput.setAttribute('min', todayStr);
                    if (expectedDateInput.value < todayStr) {
                        expectedDateInput.value = todayStr;
                    }
                }
            }
        });
    }

    // --- Edit Order Modal Date Logic ---
    const editOrderModal = document.getElementById('editOrderModal');
    if (editOrderModal) {
        editOrderModal.addEventListener('show.bs.modal', function () {
            const orderedDateInput = document.getElementById('editOrderedDate');
            const expectedDateInput = document.getElementById('editExpectedDate');
            if (orderedDateInput && expectedDateInput) {
                // Set expected date min to ordered date on modal open
                expectedDateInput.setAttribute('min', orderedDateInput.value);
                // Update expected date min whenever ordered date changes (should not change, but for consistency)
                orderedDateInput.addEventListener('input', function() {
                    expectedDateInput.setAttribute('min', this.value);
                    if (expectedDateInput.value < this.value) {
                        expectedDateInput.value = this.value;
                    }
                });
                // If expected date is before ordered date, set it to ordered date
                if (expectedDateInput.value < orderedDateInput.value) {
                    expectedDateInput.value = orderedDateInput.value;
                }
            }
        });
    }

    // --- Custom Brick Combobox Logic ---
    var brickInput = document.getElementById('brick-combobox-input');
    var brickList = document.getElementById('brick-combobox-list');
    var brickIdHidden = document.getElementById('brickId');
    var brickComboboxWrapper = document.getElementById('brick-combobox-wrapper');
    var brickOptions = [];
    var brickOptionsData = document.getElementById('brickOptionsData');
    if (brickOptionsData) {
        try {
            var raw = JSON.parse(brickOptionsData.textContent);
            brickOptions = raw.map(function(b) {
                return {
                    id: b.id,
                    text: b.name + ' (' + (b.manufacturer ? b.manufacturer.name : '') + ')'
                };
            });
        } catch (e) { brickOptions = []; }
    }
    if (brickInput && brickList && brickIdHidden) {
        function showBrickList(filtered) {
            brickList.innerHTML = '';
            if (!filtered.length) {
                brickList.style.display = 'none';
                brickComboboxWrapper.classList.remove('active');
                return;
            }
            filtered.forEach(function(opt) {
                var item = document.createElement('button');
                item.type = 'button';
                item.className = 'list-group-item list-group-item-action';
                item.textContent = opt.text;
                item.dataset.id = opt.id;
                item.onclick = function() {
                    brickInput.value = opt.text;
                    brickIdHidden.value = opt.id;
                    brickList.style.display = 'none';
                    brickComboboxWrapper.classList.remove('active');
                };
                brickList.appendChild(item);
            });
            brickList.style.display = 'block';
            brickComboboxWrapper.classList.add('active');
        }
        brickInput.addEventListener('input', function() {
            var filter = brickInput.value.trim().toLowerCase();
            var filtered = brickOptions.filter(function(opt) {
                return opt.text.toLowerCase().includes(filter);
            });
            showBrickList(filtered);
            brickIdHidden.value = '';
        });
        brickInput.addEventListener('focus', function() {
            var filter = brickInput.value.trim().toLowerCase();
            var filtered = brickOptions.filter(function(opt) {
                return opt.text.toLowerCase().includes(filter);
            });
            showBrickList(filtered);
        });
        document.addEventListener('click', function(e) {
            if (!brickComboboxWrapper.contains(e.target)) {
                brickList.style.display = 'none';
                brickComboboxWrapper.classList.remove('active');
            }
        });
        // Clear hidden input if user types
        brickInput.addEventListener('keydown', function(e) {
            if (e.key !== 'Tab' && e.key !== 'Enter') {
                brickIdHidden.value = '';
            }
        });
        // On modal open, reset combobox
        if (addOrderModal) {
            addOrderModal.addEventListener('show.bs.modal', function () {
                brickInput.value = '';
                brickIdHidden.value = '';
                brickList.style.display = 'none';
                brickComboboxWrapper.classList.remove('active');
            });
        }
    }

    // --- Edit Order Modal Form Submission ---
    var editOrderForm = document.getElementById('editOrderForm');
    if (editOrderForm) {
        editOrderForm.onsubmit = function(e) {
            e.preventDefault();
            var orderId = document.getElementById('editOrderId').value;
            var bricksOrdered = document.getElementById('editBricksOrdered').value;
            var expectedDate = document.getElementById('editExpectedDate').value;
            var formData = new FormData();
            formData.append('bricks_ordered', bricksOrdered);
            formData.append('expected_date', expectedDate);
            // Admin fields
            var receivedDateInput = document.getElementById('editReceivedDate');
            var bricksReceivedInput = document.getElementById('editBricksReceived');
            var setUnreceivedCheckbox = document.getElementById('editSetUnreceived');
            if (setUnreceivedCheckbox && setUnreceivedCheckbox.checked) {
                formData.append('set_unreceived', '1');
            }
            if (receivedDateInput && receivedDateInput.value) {
                formData.append('received_date', receivedDateInput.value);
            }
            if (bricksReceivedInput && bricksReceivedInput.value) {
                formData.append('bricks_received', bricksReceivedInput.value);
            }
            fetch('/orders/edit/' + orderId, {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => response.text())
            .then(html => {
                var modal = bootstrap.Modal.getInstance(document.getElementById('editOrderModal'));
                if (modal) modal.hide();
                showOrderFlash('Order updated!');
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
                            reloadDetailPanel();
                        }
                    });
                }
            });
        };
    }

    // --- Add Order Modal Form Submission ---
    var addOrderForm = document.querySelector('#addOrderModal form');
    if (addOrderForm) {
        addOrderForm.onsubmit = function(e) {
            var brickIdHidden = document.getElementById('brickId');
            if (!brickIdHidden || !brickIdHidden.value) {
                showOrderFlash('Please select a brick before adding the order.', 'danger');
                var brickInput = document.getElementById('brick-combobox-input');
                if (brickInput) {
                    brickInput.classList.add('is-invalid');
                    brickInput.focus();
                    setTimeout(function() {
                        brickInput.classList.remove('is-invalid');
                    }, 1200);
                }
                return false;
            }
            e.preventDefault();
            var formData = new FormData(addOrderForm);
            fetch(addOrderForm.action, {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    var modal = bootstrap.Modal.getInstance(document.getElementById('addOrderModal'));
                    if (modal) modal.hide();
                    showOrderFlash('Order added!');
                    if (data.orderNo) {
                        var currentOrderNo = typeof selectedOrderNo !== 'undefined' ? selectedOrderNo : null;
                        if (!currentOrderNo || currentOrderNo !== data.orderNo) {
                            window.location.href = `/orders/${encodeURIComponent(data.orderNo)}`;
                            return;
                        } else {
                            // If already selected, refresh the detail panel
                            fetch(ORDER_DETAIL_URL.replace('ORDER_NO_PLACEHOLDER', data.orderNo), {
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
                                    reloadDetailPanel();
                                }
                            });
                        }
                    }
                } else {
                    // Show error from mediator (e.g. brick not selected)
                    showOrderFlash(data.error || 'Failed to add order', 'danger');
                    if (data.error && data.error.toLowerCase().includes('brick')) {
                        var brickInput = document.getElementById('brick-combobox-input');
                        if (brickInput) {
                            brickInput.classList.add('is-invalid');
                            brickInput.focus();
                            setTimeout(function() {
                                brickInput.classList.remove('is-invalid');
                            }, 1200);
                        }
                    }
                }
            })
            .catch(() => {
                showOrderFlash('Failed to add order', 'danger');
            });
        };
    }

    // --- Add Order Modal: Reset Form on Close ---
    const addOrderModalEl = document.getElementById('addOrderModal');
    if (addOrderModalEl) {
        addOrderModalEl.addEventListener('hidden.bs.modal', function () {
            var form = addOrderModalEl.querySelector('form');
            if (form) form.reset();
            // Explicitly clear custom combobox fields
            var brickInput = document.getElementById('brick-combobox-input');
            var brickIdHidden = document.getElementById('brickId');
            var brickList = document.getElementById('brick-combobox-list');
            var brickComboboxWrapper = document.getElementById('brick-combobox-wrapper');
            if (brickInput) brickInput.value = '';
            if (brickIdHidden) brickIdHidden.value = '';
            if (brickList) brickList.style.display = 'none';
            if (brickComboboxWrapper) brickComboboxWrapper.classList.remove('active');
            // Reset ordered date to today (if present)
            var orderedDateInput = document.getElementById('ordered_date');
            if (orderedDateInput) {
                const today = new Date();
                const yyyy = today.getFullYear();
                const mm = String(today.getMonth() + 1).padStart(2, '0');
                const dd = String(today.getDate()).padStart(2, '0');
                const todayStr = `${yyyy}-${mm}-${dd}`;
                orderedDateInput.value = todayStr;
                orderedDateInput.setAttribute('max', todayStr);
                const minDate = new Date(today);
                minDate.setDate(today.getDate() - 3);
                const minY = minDate.getFullYear();
                const minM = String(minDate.getMonth() + 1).padStart(2, '0');
                const minD = String(minDate.getDate()).padStart(2, '0');
                const minStr = `${minY}-${minM}-${minD}`;
                orderedDateInput.setAttribute('min', minStr);
            }
            // Set expected date to null (empty string)
            var expectedDateInput = document.getElementById('expected_date');
            if (expectedDateInput) {
                expectedDateInput.value = '';
                if (orderedDateInput) expectedDateInput.setAttribute('min', orderedDateInput.value);
            }
        });
    }
});
