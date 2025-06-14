// bricks.js - Handles brick detail panel logic

document.addEventListener('DOMContentLoaded', () => {
    // Show brick details when a row is clicked
    const rows = document.querySelectorAll('.brick-row');
    const panel = document.getElementById('brick-detail-panel');
    const actions = document.getElementById('detail-actions');
    const editLink = document.getElementById('edit-link');
    const deleteLink = document.getElementById('delete-link');
    const backBtn = document.getElementById('back-to-brick-btn');
    let previousBrickId = null;

    // Add a global variable for admin status
    const isAdmin = window.isAdmin === true || window.isAdmin === 'true';

    // Add event listener for Back to Brick button
    if (backBtn) {
        backBtn.addEventListener('click', function() {
            if (previousBrickId) {
                const row = document.querySelector(`.brick-row[data-id='${previousBrickId}']`);
                if (row) {
                    row.click();
                }
            }
        });
    }

    rows.forEach(row => {
        row.addEventListener('click', function() {
            const brick = JSON.parse(this.dataset.brick);
            document.getElementById('detail-name').textContent = brick.name;
            document.getElementById('detail-manufacturer').textContent = brick.manufacturer.name;
            // Show and update manufacturer details button
            var manufacturerBtn = document.getElementById('detail-manufacturer-btn');
            if (manufacturerBtn) {
                manufacturerBtn.style.display = 'inline-block';
                manufacturerBtn.href = `/manufacturers/${brick.manufacturer.id}`;
            }
            document.getElementById('detail-colour').textContent = brick.colour;
            document.getElementById('detail-material').textContent = brick.material;
            document.getElementById('detail-strength').textContent = brick.strength;
            document.getElementById('detail-width').textContent = brick.width;
            document.getElementById('detail-depth').textContent = brick.depth;
            document.getElementById('detail-height').textContent = brick.height;
            document.getElementById('detail-type').textContent = brick.type;
            document.getElementById('detail-voids').textContent = brick.voids;
            const priceSpan = document.getElementById('detail-price');
            if (priceSpan) {
                let price = Number(brick.price);
                priceSpan.textContent = isNaN(price) ? '' : price.toLocaleString('en-GB', { style: 'currency', currency: 'GBP' });
            }
            panel.style.display = 'block';
            if (document.getElementById('brick-placeholder-panel')) {
                document.getElementById('brick-placeholder-panel').classList.add('d-none');
            }
            if (actions && editLink) {
                editLink.href = `/edit_brick/${brick.id}`;
                if (deleteLink) {
                    if (isAdmin) {
                        deleteLink.href = `/delete_brick/${brick.id}`;
                        deleteLink.style.display = '';
                    } else {
                        deleteLink.style.display = 'none';
                    }
                }
                actions.style.display = 'block';
            }
            // Update the URL with the selected brick ID
            const newUrl = `${window.location.pathname.replace(/\/(\d+)?$/, '')}/${brick.id}`;
            window.history.pushState({ brickId: brick.id }, '', newUrl);
            // Store previous brick id
            const currentId = window.location.pathname.match(/\/(\d+)$/);
            if (currentId && brick.id != currentId[1]) {
                previousBrickId = currentId[1];

            }
            // Show/hide back button
            if (previousBrickId && previousBrickId != brick.id) {
                if (backBtn) backBtn.style.display = 'inline-block';

            } else {
                if (backBtn) backBtn.style.display = 'none';
            }
            // Remove row highlighting (no-op)
        });
    });

    // On page load, if URL ends with a brick ID, show that brick's details
    const selectedBrickId = window.selectedBrickId !== undefined ? window.selectedBrickId : null;
    let brickId = null;
    if (selectedBrickId !== null && selectedBrickId !== 'null') {
        brickId = selectedBrickId;
    } else {
        // Only match /bricks/{id} for brick page
        const match = window.location.pathname.match(/\/bricks\/(\d+)$/);
        if (match) {
            brickId = match[1];
        }
    }
    if (brickId) {
        const row = document.querySelector(`.brick-row[data-id='${brickId}']`);
        if (row) {
            row.click();
            panel.scrollIntoView({ behavior: 'smooth', block: 'center' });
            if (document.getElementById('brick-placeholder-panel')) {
                document.getElementById('brick-placeholder-panel').classList.add('d-none');
            }

        } else {
            panel.style.display = 'none';
            if (actions) actions.style.display = 'none';
            if (document.getElementById('brick-placeholder-panel')) {
                document.getElementById('brick-placeholder-panel').classList.remove('d-none');
            }
        }
    } else {
        panel.style.display = 'none';
        if (actions) actions.style.display = 'none';
        if (document.getElementById('brick-placeholder-panel')) {
            document.getElementById('brick-placeholder-panel').classList.remove('d-none');
        }   
    }

    // Search/filter functionality for bricks table
    const searchBox = document.getElementById('brick-search-box');
    if (searchBox) {
        searchBox.addEventListener('input', function() {
            const filter = this.value.trim().toLowerCase();
            document.querySelectorAll('.brick-row').forEach(row => {
                const name = row.querySelector('td:nth-child(1)').textContent.toLowerCase();
                if (name.includes(filter)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }

    // --- Filter Dropdown Logic ---
    const filterBtn = document.getElementById('brick-filter-btn');
    const filterDropdown = document.getElementById('brick-filter-dropdown');
    const closeFilterDropdown = document.getElementById('close-filter-dropdown');
    const applyFilterBtn = document.getElementById('apply-filter-btn');
    const clearFilterBtn = document.getElementById('clear-filter-btn');
    const manufacturerSelect = document.getElementById('manufacturer-filter-select');

    function showFilterDropdown() {
        if (filterDropdown) filterDropdown.style.display = 'block';
    }
    function hideFilterDropdown() {
        if (filterDropdown) filterDropdown.style.display = 'none';
    }

    if (filterBtn && filterDropdown) {
        filterBtn.addEventListener('click', function(e) {
            e.stopPropagation();
                if (filterDropdown.style.display === 'block') {
                    hideFilterDropdown();
                } else {
                    showFilterDropdown();
                }
        });
    }
    if (closeFilterDropdown) {
        closeFilterDropdown.addEventListener('click', hideFilterDropdown);
    }
    // Hide dropdown if clicking outside
    document.addEventListener('click', function(e) {
        if (filterDropdown && filterDropdown.style.display === 'block') {
            if (!filterDropdown.contains(e.target) && e.target !== filterBtn) {
                hideFilterDropdown();
            }
        }
    });

    function updateFilterBadge() {
        const badge = document.getElementById('brick-filter-badge');
        const rows = document.querySelectorAll('.brick-row');
        let hiddenCount = 0;
        rows.forEach(row => {
            if (row.style.display === 'none') hiddenCount++;
        });
        if (badge) {
            if (hiddenCount > 0) {
                badge.textContent = '1'; // Only show indicator, not count
                badge.style.display = 'inline-block';
            } else {
                badge.style.display = 'none';
            }
        }
    }

    function filterRows() {
        const searchValue = searchBox ? searchBox.value.trim().toLowerCase() : '';
        let selectedManufacturer = '';
        if (manufacturerSelect) {
            selectedManufacturer = manufacturerSelect.value;
        }
        // Get price range values
        const minPriceInput = document.getElementById('price-min-filter');
        const maxPriceInput = document.getElementById('price-max-filter');
        const minPrice = minPriceInput && minPriceInput.value !== '' ? parseFloat(minPriceInput.value) : null;
        const maxPrice = maxPriceInput && maxPriceInput.value !== '' ? parseFloat(maxPriceInput.value) : null;
        document.querySelectorAll('.brick-row').forEach(row => {
            const name = row.querySelector('td:nth-child(1)').textContent.toLowerCase();
            const manufacturer = row.querySelector('td:nth-child(2)').textContent;
            // Price cell is always the third column
            let priceText = row.querySelector('td:nth-child(3)').textContent.replace(/[^\d.]/g, '');
            let price = parseFloat(priceText);
            const matchesName = name.includes(searchValue);
            const matchesManufacturer = !selectedManufacturer || manufacturer === selectedManufacturer;
            const matchesMin = minPrice === null || (!isNaN(price) && price >= minPrice);
            const matchesMax = maxPrice === null || (!isNaN(price) && price <= maxPrice);
            row.style.display = (matchesName && matchesManufacturer && matchesMin && matchesMax) ? '' : 'none';
        });
        updateFilterBadge();
    }

    if (applyFilterBtn && manufacturerSelect) {
        applyFilterBtn.addEventListener('click', function() {
          filterRows();
          hideFilterDropdown();
        });
    }
    if (clearFilterBtn && manufacturerSelect) {
        clearFilterBtn.addEventListener('click', function() {
            manufacturerSelect.value = '';
            // Reset price range inputs
            const minPriceInput = document.getElementById('price-min-filter');
            const maxPriceInput = document.getElementById('price-max-filter');
            if (minPriceInput) minPriceInput.value = '';
            if (maxPriceInput) maxPriceInput.value = '';
            filterRows();
            hideFilterDropdown();
        });
    }
    if (manufacturerSelect) {
        manufacturerSelect.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                applyFilterBtn.click();
            }
        });
        manufacturerSelect.addEventListener('change', updateFilterBadge);
    }

    // Update filterRows to also run on search
    if (searchBox) {
        searchBox.addEventListener('input', filterRows);
    }

    // Initialize badge on page load
    updateFilterBadge();
});

// Handle browser back/forward navigation
window.addEventListener('popstate', (event) => {
    const panel = document.getElementById('brick-detail-panel');
    const actions = document.getElementById('detail-actions');
    const backBtn = document.getElementById('back-to-brick-btn');
    const match = window.location.pathname.match(/\/(\d+)$/);
    if (match) {
        const brickId = match[1];
        const row = document.querySelector(`.brick-row[data-id='${brickId}']`);
        if (row) {
            row.click();
            if (document.getElementById('brick-placeholder-panel')) {
                document.getElementById('brick-placeholder-panel').classList.add('d-none');
            }
        }
    } else {
        panel.style.display = 'none';
        if (actions) actions.style.display = 'none';
        if (document.getElementById('brick-placeholder-panel')) {
            document.getElementById('brick-placeholder-panel').classList.remove('d-none');
        }
    }
    previousBrickId = null;
    if (backBtn) backBtn.style.display = 'none';
});
