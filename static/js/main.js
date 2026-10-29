/**
 * AQUAVERA Premium Water Purifiers
 * Main JavaScript Interactions & Compare Manager
 */

document.addEventListener('DOMContentLoaded', function () {
  // 1. Sticky Navbar shadow on scroll
  const navbar = document.querySelector('.aquavera-navbar');
  if (navbar) {
    window.addEventListener('scroll', function () {
      if (window.scrollY > 20) {
        navbar.classList.add('scrolled');
      } else {
        navbar.classList.remove('scrolled');
      }
    });
  }

  // 2. Initialize Comparison Drawer
  initCompareManager();

  // 3. Initialize Tooltips
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  if (window.bootstrap && bootstrap.Tooltip) {
    tooltipTriggerList.map(function (tooltipTriggerEl) {
      return new bootstrap.Tooltip(tooltipTriggerEl);
    });
  }
});

/**
 * Compare Manager
 * Handles up to 3 products in localStorage and syncs with bottom drawer.
 */
function getCompareList() {
  try {
    const list = localStorage.getItem('aquavera_compare_list');
    return list ? JSON.parse(list) : [];
  } catch (e) {
    return [];
  }
}

function saveCompareList(list) {
  try {
    localStorage.setItem('aquavera_compare_list', JSON.stringify(list));
  } catch (e) {}
}

function addToCompare(productId, productName) {
  let list = getCompareList();
  
  // Check if already in list
  const exists = list.some(item => item.id == productId);
  if (exists) {
    showToastNotification(`"${productName}" is already in your comparison tray.`);
    return;
  }

  if (list.length >= 3) {
    showToastNotification('You can compare a maximum of 3 water purifiers at once. Remove one to add another.', 'warning');
    return;
  }

  list.push({ id: productId, name: productName });
  saveCompareList(list);
  updateCompareDrawer();
  showToastNotification(`Added "${productName}" to comparison!`);
}

function removeFromCompare(productId) {
  let list = getCompareList();
  list = list.filter(item => item.id != productId);
  saveCompareList(list);
  updateCompareDrawer();
}

function clearCompareList() {
  saveCompareList([]);
  updateCompareDrawer();
  showToastNotification('Comparison tray cleared.');
}

function updateCompareDrawer() {
  const drawer = document.getElementById('compareStickyBar');
  const itemsContainer = document.getElementById('compareItemsList');
  const compareCountBadge = document.getElementById('compareCountBadge');
  const compareActionBtn = document.getElementById('compareActionBtn');

  if (!drawer || !itemsContainer) return;

  const list = getCompareList();

  if (compareCountBadge) {
    compareCountBadge.textContent = list.length;
  }

  if (list.length === 0) {
    drawer.classList.remove('visible');
    itemsContainer.innerHTML = '';
    return;
  }

  drawer.classList.add('visible');
  itemsContainer.innerHTML = '';

  list.forEach(item => {
    const pill = document.createElement('div');
    pill.className = 'compare-thumb-pill me-2 mb-1';
    pill.innerHTML = `
      <span class="text-truncate" style="max-width: 140px;">${item.name}</span>
      <button type="button" class="btn-close btn-close-sm" aria-label="Remove" onclick="removeFromCompare(${item.id})"></button>
    `;
    itemsContainer.appendChild(pill);
  });

  if (compareActionBtn) {
    const ids = list.map(item => item.id).join(',');
    compareActionBtn.href = `/compare/?ids=${ids}`;
  }
}

function initCompareManager() {
  updateCompareDrawer();

  // Attach event delegation for "Add to Compare" buttons
  document.addEventListener('click', function (e) {
    const btn = e.target.closest('.btn-add-compare');
    if (btn) {
      e.preventDefault();
      const id = btn.getAttribute('data-product-id');
      const name = btn.getAttribute('data-product-name');
      if (id && name) {
        addToCompare(id, name);
      }
    }
  });
}

function showToastNotification(message, type = 'info') {
  const toastContainer = document.getElementById('aquaveraToastContainer');
  if (!toastContainer) {
    alert(message);
    return;
  }

  const toastEl = document.createElement('div');
  toastEl.className = 'toast align-items-center text-white bg-dark border-0 mb-2';
  toastEl.setAttribute('role', 'alert');
  toastEl.setAttribute('aria-live', 'assertive');
  toastEl.setAttribute('aria-atomic', 'true');
  toastEl.innerHTML = `
    <div class="d-flex">
      <div class="toast-body">
        <i class="bi bi-info-circle-fill text-info me-2"></i> ${message}
      </div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
    </div>
  `;

  toastContainer.appendChild(toastEl);
  if (window.bootstrap && bootstrap.Toast) {
    const toast = new bootstrap.Toast(toastEl, { delay: 4000 });
    toast.show();
    toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());
  } else {
    setTimeout(() => toastEl.remove(), 4000);
  }
}
