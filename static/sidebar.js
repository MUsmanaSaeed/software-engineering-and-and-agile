// Handles sidebar toggle, mobile collapse, and flash message auto-dismiss

document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    const content = document.getElementById('content');
    const toggler = document.getElementById('sidebarCollapse');
    if (toggler) {
        toggler.addEventListener('click', function () {
            sidebar.classList.toggle('collapsed');
            content.classList.toggle('collapsed');
        });
    }
    // For mobile: show/hide sidebar
    if (window.innerWidth < 769) {
        sidebar.classList.add('collapsed');
        content.classList.add('collapsed');
    }
    // Auto-dismiss flash messages after 10 seconds
    setTimeout(function() {
        document.querySelectorAll('.floating-flash-container .alert').forEach(function(alert) {
            var bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        });
    }, 10000); // 10 seconds
});
