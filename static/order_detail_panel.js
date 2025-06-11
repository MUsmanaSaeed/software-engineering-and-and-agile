// Cancel Confirmation Modal Logic

document.addEventListener('DOMContentLoaded', function () {
    // Handle cancel button click
    document.querySelectorAll('.btn-order-cancel').forEach(function (button) {
        button.addEventListener('click', function () {
            var orderId = this.getAttribute('data-order-id');
            // Show the confirmation modal
            var modal = document.getElementById('cancelConfirmModal');
            modal.classList.add('active');

            // Handle confirmation button click
            document.getElementById('cancelModalYes').onclick = function () {
                // Submit the cancel form for the specific order
                var form = document.querySelector('.cancel-order-form [data-order-id="'+orderId+'"]').closest('form');
                form.submit();
            };

            // Handle cancel button click in modal
            document.getElementById('cancelModalNo').onclick = function (e) {
                e.stopPropagation();
                modal.click();
            };

            // Hide modal if clicking outside dialog
            modal.onclick = function(e) {
                if (e.target === modal) {
                    modal.classList.remove('active');
                }
            };
        });
    });
});
