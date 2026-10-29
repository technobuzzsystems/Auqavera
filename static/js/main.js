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

  // 4. Initialize Hero Video with reduced motion & fallback handling
  initHeroVideo();

  // 5. Initialize Product Quick View / Preview Modal
  initProductQuickView();
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

/**
 * Hero Video Manager
 * Handles responsive video playback, prefers-reduced-motion compliance,
 * accessibility controls, and fallback state if loading fails.
 */
function initHeroVideo() {
  const video = document.getElementById('heroVideo');
  const card = document.getElementById('heroVideoCard');
  const toggleBtn = document.getElementById('heroVideoToggleBtn');
  const toggleIcon = document.getElementById('heroVideoToggleIcon');
  const toggleText = document.getElementById('heroVideoToggleText');

  if (!video) return;

  // Check user prefers-reduced-motion preference
  const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');

  function applyReducedMotion(isReduced) {
    if (isReduced) {
      video.removeAttribute('autoplay');
      video.pause();
      if (toggleIcon && toggleText) {
        toggleIcon.className = 'bi bi-play-fill';
        toggleText.textContent = 'Play';
      }
    } else {
      // If allowed to play, attempt autoplay
      video.play().catch(function () {
        // Autoplay policy fallback (browser requires user interaction)
        if (toggleIcon && toggleText) {
          toggleIcon.className = 'bi bi-play-fill';
          toggleText.textContent = 'Play';
        }
      });
      if (toggleIcon && toggleText) {
        toggleIcon.className = 'bi bi-pause-fill';
        toggleText.textContent = 'Pause';
      }
    }
  }

  // Apply on load
  if (motionQuery.matches) {
    applyReducedMotion(true);
  }

  // Listen for preference changes
  if (motionQuery.addEventListener) {
    motionQuery.addEventListener('change', function (e) {
      applyReducedMotion(e.matches);
    });
  }

  // Play/Pause button interaction
  if (toggleBtn) {
    toggleBtn.addEventListener('click', function () {
      if (video.paused) {
        video.play().then(function () {
          if (toggleIcon) toggleIcon.className = 'bi bi-pause-fill';
          if (toggleText) toggleText.textContent = 'Pause';
        }).catch(function (err) {
          console.warn('Playback error:', err);
        });
      } else {
        video.pause();
        if (toggleIcon) toggleIcon.className = 'bi bi-play-fill';
        if (toggleText) toggleText.textContent = 'Play';
      }
    });
  }

  // Error handling: gracefully reveal fallback if media fails to load
  video.addEventListener('error', function () {
    if (card) {
      card.classList.add('video-failed');
    }
  }, true);

  const source = video.querySelector('source');
  if (source) {
    source.addEventListener('error', function () {
      if (card) {
        card.classList.add('video-failed');
      }
    });
  }
}

/**
 * Product Quick View / Preview Modal Controller
 */
function initProductQuickView() {
  const modalEl = document.getElementById('productPreviewModal');
  if (!modalEl) return;

  let bsModal = null;
  if (window.bootstrap && bootstrap.Modal) {
    bsModal = bootstrap.Modal.getOrCreateInstance(modalEl);
  }

  const cache = new Map();
  let currentProductData = null;
  let currentImageIndex = 0;

  // DOM elements
  const loadingEl = document.getElementById('quickViewLoading');
  const errorEl = document.getElementById('quickViewError');
  const contentEl = document.getElementById('quickViewContent');

  const categoryEl = document.getElementById('quickViewCategory');
  const skuEl = document.getElementById('quickViewSku');
  const titleEl = document.getElementById('quickViewTitle');
  const descEl = document.getElementById('quickViewDescription');
  const priceEl = document.getElementById('quickViewPrice');
  const originalPriceEl = document.getElementById('quickViewOriginalPrice');
  const savingsBadgeEl = document.getElementById('quickViewSavingsBadge');
  const discountBadgeEl = document.getElementById('quickViewDiscountBadge');
  const stockBadgeEl = document.getElementById('quickViewStockBadge');

  const mainImg = document.getElementById('quickViewMainImg');
  const placeholderEl = document.getElementById('quickViewPlaceholder');
  const thumbnailsContainer = document.getElementById('quickViewThumbnails');
  const prevBtn = document.getElementById('quickViewPrevBtn');
  const nextBtn = document.getElementById('quickViewNextBtn');

  const techCol = document.getElementById('quickViewTechCol');
  const techEl = document.getElementById('quickViewTech');
  const capacityCol = document.getElementById('quickViewCapacityCol');
  const capacityEl = document.getElementById('quickViewCapacity');
  const stagesCol = document.getElementById('quickViewStagesCol');
  const stagesEl = document.getElementById('quickViewStages');
  const useCol = document.getElementById('quickViewUseCol');
  const useEl = document.getElementById('quickViewUse');
  const warrantyCol = document.getElementById('quickViewWarrantyCol');
  const warrantyEl = document.getElementById('quickViewWarranty');

  const featuresBox = document.getElementById('quickViewFeaturesBox');
  const featuresList = document.getElementById('quickViewFeaturesList');

  const detailBtn = document.getElementById('quickViewDetailBtn');
  const enquiryBtn = document.getElementById('quickViewEnquiryBtn');
  const compareBtn = document.getElementById('quickViewCompareBtn');

  function renderImage(index) {
    if (!currentProductData || !currentProductData.images || currentProductData.images.length === 0) {
      if (mainImg) mainImg.style.display = 'none';
      if (placeholderEl) placeholderEl.style.display = 'flex';
      if (prevBtn) prevBtn.style.display = 'none';
      if (nextBtn) nextBtn.style.display = 'none';
      if (thumbnailsContainer) thumbnailsContainer.style.display = 'none';
      return;
    }

    const images = currentProductData.images;
    if (index < 0) index = images.length - 1;
    if (index >= images.length) index = 0;
    currentImageIndex = index;

    const img = images[currentImageIndex];
    if (mainImg) {
      mainImg.src = img.url;
      mainImg.alt = img.alt || currentProductData.name;
      mainImg.style.display = 'block';
    }
    if (placeholderEl) placeholderEl.style.display = 'none';

    // Show/hide gallery arrows
    if (images.length > 1) {
      if (prevBtn) prevBtn.style.display = 'flex';
      if (nextBtn) nextBtn.style.display = 'flex';
      if (thumbnailsContainer) thumbnailsContainer.style.display = 'flex';
    } else {
      if (prevBtn) prevBtn.style.display = 'none';
      if (nextBtn) nextBtn.style.display = 'none';
      if (thumbnailsContainer) thumbnailsContainer.style.display = 'none';
    }

    // Highlight active thumbnail
    if (thumbnailsContainer) {
      const thumbs = thumbnailsContainer.querySelectorAll('.quickview-thumb-item');
      thumbs.forEach((th, i) => {
        if (i === currentImageIndex) {
          th.classList.add('active');
          th.setAttribute('aria-selected', 'true');
        } else {
          th.classList.remove('active');
          th.setAttribute('aria-selected', 'false');
        }
      });
    }
  }

  function displayProduct(product) {
    currentProductData = product;
    currentImageIndex = 0;

    // Title & Category
    if (titleEl) titleEl.textContent = product.name;
    if (categoryEl) categoryEl.textContent = product.category || 'Water Purifier';
    if (skuEl) {
      if (product.sku) {
        skuEl.textContent = `SKU: ${product.sku}`;
        skuEl.style.display = 'inline-block';
      } else {
        skuEl.style.display = 'none';
      }
    }

    // Description
    if (descEl) descEl.textContent = product.short_description || '';

    // Price
    if (priceEl) priceEl.textContent = product.formatted_price;
    if (originalPriceEl) {
      if (product.original_price && product.original_price > product.price) {
        originalPriceEl.textContent = product.formatted_original_price;
        originalPriceEl.style.display = 'inline';
      } else {
        originalPriceEl.style.display = 'none';
      }
    }

    // Discount badges
    if (product.discount_percentage && product.discount_percentage > 0) {
      if (discountBadgeEl) {
        discountBadgeEl.textContent = `${product.discount_percentage}% OFF`;
        discountBadgeEl.style.display = 'inline-block';
      }
      if (savingsBadgeEl) {
        savingsBadgeEl.textContent = `${product.discount_percentage}% Savings`;
        savingsBadgeEl.style.display = 'inline-block';
      }
    } else {
      if (discountBadgeEl) discountBadgeEl.style.display = 'none';
      if (savingsBadgeEl) savingsBadgeEl.style.display = 'none';
    }

    // Stock badge
    if (stockBadgeEl) {
      stockBadgeEl.className = `badge ${product.stock_badge_class || 'bg-success'}`;
      stockBadgeEl.textContent = product.stock_status_display;
      stockBadgeEl.style.display = 'inline-block';
    }

    // Specs helper (hides if empty)
    function setSpec(col, el, val) {
      if (col && el) {
        if (val && String(val).trim()) {
          el.textContent = val;
          col.style.display = 'block';
        } else {
          col.style.display = 'none';
        }
      }
    }
    setSpec(techCol, techEl, product.technology);
    setSpec(capacityCol, capacityEl, product.storage_capacity_liters ? `${product.storage_capacity_liters} Liters` : '');
    setSpec(stagesCol, stagesEl, product.purification_stages);
    setSpec(useCol, useEl, product.intended_use);
    setSpec(warrantyCol, warrantyEl, product.warranty_info);

    // Features
    if (featuresBox && featuresList) {
      featuresList.innerHTML = '';
      if (product.features && product.features.length > 0) {
        product.features.forEach(feat => {
          const li = document.createElement('li');
          li.className = 'd-flex align-items-baseline gap-2 text-dark';
          li.innerHTML = `<i class="bi bi-check-circle-fill text-info" style="font-size: 0.8rem;"></i> <span>${feat}</span>`;
          featuresList.appendChild(li);
        });
        featuresBox.style.display = 'block';
      } else {
        featuresBox.style.display = 'none';
      }
    }

    // Buttons
    if (detailBtn) detailBtn.href = product.detail_url;
    if (enquiryBtn) enquiryBtn.href = product.enquiry_url;

    // Thumbnails
    if (thumbnailsContainer) {
      thumbnailsContainer.innerHTML = '';
      if (product.images && product.images.length > 1) {
        product.images.forEach((img, idx) => {
          const thumb = document.createElement('div');
          thumb.className = `quickview-thumb-item ${idx === 0 ? 'active' : ''}`;
          thumb.setAttribute('role', 'button');
          thumb.setAttribute('tabindex', '0');
          thumb.setAttribute('aria-label', `Thumbnail image ${idx + 1}`);
          thumb.innerHTML = `<img src="${img.url}" alt="${img.alt || product.name}">`;
          thumb.addEventListener('click', () => renderImage(idx));
          thumb.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              renderImage(idx);
            }
          });
          thumbnailsContainer.appendChild(thumb);
        });
      }
    }

    // Render active image
    renderImage(0);

    // Switch view
    if (loadingEl) loadingEl.style.display = 'none';
    if (errorEl) errorEl.style.display = 'none';
    if (contentEl) contentEl.style.display = 'flex';
  }

  function openPreview(productId, previewUrl) {
    if (!previewUrl) {
      previewUrl = `/products/${productId}/preview/`;
    }

    // Reset view to loading
    if (loadingEl) loadingEl.style.display = 'block';
    if (errorEl) errorEl.style.display = 'none';
    if (contentEl) contentEl.style.display = 'none';

    if (bsModal) {
      bsModal.show();
    }

    // Check cache
    if (cache.has(productId)) {
      displayProduct(cache.get(productId));
      return;
    }

    fetch(previewUrl, { credentials: 'same-origin' })
      .then(res => {
        if (!res.ok) throw new Error('Network response not ok');
        return res.json();
      })
      .then(data => {
        cache.set(productId, data);
        displayProduct(data);
      })
      .catch(err => {
        console.error('Quick view error:', err);
        if (loadingEl) loadingEl.style.display = 'none';
        if (errorEl) errorEl.style.display = 'block';
        if (contentEl) contentEl.style.display = 'none';
      });
  }

  // Previous & Next button handlers
  if (prevBtn) {
    prevBtn.addEventListener('click', () => renderImage(currentImageIndex - 1));
  }
  if (nextBtn) {
    nextBtn.addEventListener('click', () => renderImage(currentImageIndex + 1));
  }

  // Keyboard navigation inside modal (left/right arrows)
  modalEl.addEventListener('keydown', (e) => {
    if (currentProductData && currentProductData.images && currentProductData.images.length > 1) {
      if (e.key === 'ArrowLeft') {
        e.preventDefault();
        renderImage(currentImageIndex - 1);
      } else if (e.key === 'ArrowRight') {
        e.preventDefault();
        renderImage(currentImageIndex + 1);
      }
    }
  });

  // Compare button in modal
  if (compareBtn) {
    compareBtn.addEventListener('click', () => {
      if (currentProductData) {
        addToCompare(currentProductData.id, currentProductData.name);
      }
    });
  }

  // Event delegation on product image triggers
  document.addEventListener('click', (e) => {
    const trigger = e.target.closest('.product-preview-trigger');
    if (trigger) {
      e.preventDefault();
      const productId = trigger.getAttribute('data-product-id');
      const previewUrl = trigger.getAttribute('data-preview-url');
      if (productId) {
        openPreview(productId, previewUrl);
      }
    }
  });

  // Keyboard activation on trigger (Enter/Space)
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      const trigger = document.activeElement ? document.activeElement.closest('.product-preview-trigger') : null;
      if (trigger) {
        e.preventDefault();
        const productId = trigger.getAttribute('data-product-id');
        const previewUrl = trigger.getAttribute('data-preview-url');
        if (productId) {
          openPreview(productId, previewUrl);
        }
      }
    }
  });
}
