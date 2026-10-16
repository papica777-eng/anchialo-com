/**
 * ANCHIALO SOVEREIGN PLATFORM — CORE CLIENT ENGINE
 * Architect: Dimitar Prodromov & Sotir Kichukov | Pomorie HQ
 * High-End Apothecary Balneotherapy Interactive Experience
 */

(function () {
  'use strict';

  // ==================== CONFIGURATION & STATE ====================
  const STATE = {
    currency: localStorage.getItem('anchialo_currency') || 'USD',
    rates: {
      USD: { symbol: '$', rate: 1.0, suffix: ' USD' },
      EUR: { symbol: '€', rate: 0.92, suffix: ' EUR' },
      BGN: { symbol: '', rate: 1.80, suffix: ' лв.' }
    },
    theme: localStorage.getItem('anchialo_theme') || 'light',
    cart: JSON.parse(localStorage.getItem('anchialo_cart') || '[]'),
    activeCategory: 'all',
    searchQuery: '',
    selectedBlend: 'arnica',
    products: [],
    blogPosts: [],
    freeShippingThresholdUSD: 100
  };

  const BLENDS = {
    arnica: {
      id: 'arnica',
      name: 'ARNICA BLEND — DUAL MAGNESIUM COMPLEX',
      accentColor: '#C69214',
      bgGlow: 'rgba(198, 146, 20, 0.25)',
      lidImg: 'labels/production_ready/high_res_png_300dpi/Top_Lid_Arnica_86mm_300dpi.png',
      sideImg: 'labels/production_ready/high_res_png_300dpi/Side_Label_Arnica_280x38mm_300dpi.png',
      sidePdf: 'labels/production_ready/pdf_print_ready_cmyk/Side_Label_Arnica_280x38mm_PRINT_READY.pdf',
      lidPdf: 'labels/production_ready/pdf_print_ready_cmyk/Top_Lid_Arnica_86mm_PRINT_READY.pdf',
      botanical: 'Arnica Montana flower extract (sesquiterpene lactones for micro-circulation)',
      scent: 'Warm herbal & fresh mountain meadow',
      colorName: 'Warm Goldenrod (#C69214)'
    },
    lavender: {
      id: 'lavender',
      name: 'LAVENDER BLEND — DUAL MAGNESIUM COMPLEX',
      accentColor: '#6B5B95',
      bgGlow: 'rgba(107, 91, 149, 0.25)',
      lidImg: 'labels/production_ready/high_res_png_300dpi/Top_Lid_Lavender_86mm_300dpi.png',
      sideImg: 'labels/production_ready/high_res_png_300dpi/Side_Label_Lavender_280x38mm_300dpi.png',
      sidePdf: 'labels/production_ready/pdf_print_ready_cmyk/Side_Label_Lavender_280x38mm_PRINT_READY.pdf',
      lidPdf: 'labels/production_ready/pdf_print_ready_cmyk/Top_Lid_Lavender_86mm_PRINT_READY.pdf',
      botanical: 'Lavandula Angustifolia pure essential oil (linalool & linalyl acetate)',
      scent: 'Calming Mediterranean twilight lavender',
      colorName: 'Royal Lavender (#6B5B95)'
    },
    rosemary: {
      id: 'rosemary',
      name: 'ROSEMARY BLEND — DUAL MAGNESIUM COMPLEX',
      accentColor: '#4B6B38',
      bgGlow: 'rgba(75, 107, 56, 0.25)',
      lidImg: 'labels/production_ready/high_res_png_300dpi/Top_Lid_Rosemary_86mm_300dpi.png',
      sideImg: 'labels/production_ready/high_res_png_300dpi/Side_Label_Rosemary_280x38mm_300dpi.png',
      sidePdf: 'labels/production_ready/pdf_print_ready_cmyk/Side_Label_Rosemary_280x38mm_PRINT_READY.pdf',
      lidPdf: 'labels/production_ready/pdf_print_ready_cmyk/Top_Lid_Rosemary_86mm_PRINT_READY.pdf',
      botanical: 'Rosmarinus Officinalis leaf oil (rosmarinic acid & cineole)',
      scent: 'Invigorating pine-camphor herbal tone',
      colorName: 'Forest Rosemary (#4B6B38)'
    },
    juniper: {
      id: 'juniper',
      name: 'JUNIPER BLEND — DUAL MAGNESIUM COMPLEX',
      accentColor: '#285844',
      bgGlow: 'rgba(40, 88, 68, 0.25)',
      lidImg: 'labels/production_ready/high_res_png_300dpi/Top_Lid_Juniper_86mm_300dpi.png',
      sideImg: 'labels/production_ready/high_res_png_300dpi/Side_Label_Juniper_280x38mm_300dpi.png',
      sidePdf: 'labels/production_ready/pdf_print_ready_cmyk/Side_Label_Juniper_280x38mm_PRINT_READY.pdf',
      lidPdf: 'labels/production_ready/pdf_print_ready_cmyk/Top_Lid_Juniper_86mm_PRINT_READY.pdf',
      botanical: 'Juniperus Communis fruit oil (alpha-pinene warming complex)',
      scent: 'Crisp alpine coniferous wood notes',
      colorName: 'Deep Pine Juniper (#285844)'
    },
    grape: {
      id: 'grape',
      name: 'GRAPE BLEND — DUAL MAGNESIUM COMPLEX',
      accentColor: '#7E2A3C',
      bgGlow: 'rgba(126, 42, 60, 0.25)',
      lidImg: 'labels/production_ready/high_res_png_300dpi/Top_Lid_Grape_86mm_300dpi.png',
      sideImg: 'labels/production_ready/high_res_png_300dpi/Side_Label_Grape_280x38mm_300dpi.png',
      sidePdf: 'labels/production_ready/pdf_print_ready_cmyk/Side_Label_Grape_280x38mm_PRINT_READY.pdf',
      lidPdf: 'labels/production_ready/pdf_print_ready_cmyk/Top_Lid_Grape_86mm_PRINT_READY.pdf',
      botanical: 'Vitis Vinifera (Grape) seed extract (potent proanthocyanidins & resveratrol)',
      scent: 'Sun-drenched Black Sea vineyard bouquet',
      colorName: 'Burgundy Grape (#7E2A3C)'
    }
  };

  // ==================== PRICE & CURRENCY UTILS ====================
  function formatPrice(usdAmount) {
    const cur = STATE.rates[STATE.currency] || STATE.rates.USD;
    const converted = (parseFloat(usdAmount) * cur.rate).toFixed(2);
    if (STATE.currency === 'BGN') {
      return `${converted}${cur.suffix}`;
    }
    return `${cur.symbol}${converted}${cur.suffix}`;
  }

  function setCurrency(newCur) {
    if (!STATE.rates[newCur]) return;
    STATE.currency = newCur;
    localStorage.setItem('anchialo_currency', newCur);
    renderProducts();
    updateCartDrawer();
    showToast(`Currency switched to ${newCur}`, 'Currency Updated');
  }

  // ==================== THEME ENGINE ====================
  function applyTheme(theme) {
    STATE.theme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('anchialo_theme', theme);
    const themeBtn = document.getElementById('themeToggleBtn');
    if (themeBtn) {
      themeBtn.innerHTML = theme === 'dark' ? '☀️ Porcelain' : '🌙 Obsidian';
    }
  }

  function toggleTheme() {
    const next = STATE.theme === 'dark' ? 'light' : 'dark';
    applyTheme(next);
    showToast(`Switched to ${next === 'dark' ? 'Obsidian Mineral' : 'Porcelain Spa'} mode`, 'Theme Mode');
  }

  // ==================== TOAST SYSTEM ====================
  function showToast(message, title = 'Notification') {
    let container = document.querySelector('.toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = 'toast-item';
    toast.innerHTML = `
      <div class="toast-icon">✓</div>
      <div>
        <div style="font-weight: 800; font-family:'Montserrat', sans-serif; font-size:12px; margin-bottom:2px; color:var(--gold-primary); text-transform:uppercase; letter-spacing:1px;">${title}</div>
        <div style="font-size:13px; color:#EAE5DD;">${message}</div>
      </div>
    `;

    container.appendChild(toast);

    setTimeout(() => {
      toast.classList.add('hide');
      setTimeout(() => toast.remove(), 320);
    }, 3200);
  }

  // ==================== 3D INTERACTIVE STUDIO ====================
  function initStudio() {
    const tabs = document.querySelectorAll('.blend-tab');
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        const blendKey = tab.getAttribute('data-blend');
        switchBlend(blendKey);
      });
    });

    switchBlend('arnica');
  }

  function switchBlend(blendKey) {
    const blend = BLENDS[blendKey];
    if (!blend) return;
    STATE.selectedBlend = blendKey;

    // Update active tab styles
    document.querySelectorAll('.blend-tab').forEach(tab => {
      if (tab.getAttribute('data-blend') === blendKey) {
        tab.classList.add('active');
        tab.style.borderColor = blend.accentColor;
        tab.style.boxShadow = `0 4px 18px ${blend.bgGlow}`;
      } else {
        tab.classList.remove('active');
        tab.style.borderColor = '';
        tab.style.boxShadow = '';
      }
    });

    // Update Lid & Side Wrap views
    const lidImg = document.getElementById('studioLidImg');
    const sideImg = document.getElementById('studioSideImg');
    const blendTitle = document.getElementById('studioBlendTitle');
    const botanicalField = document.getElementById('studioBotanicalField');
    const scentField = document.getElementById('studioScentField');
    const colorField = document.getElementById('studioColorField');
    const dlLidPdf = document.getElementById('dlLidPdf');
    const dlSidePdf = document.getElementById('dlSidePdf');
    const dlLidPng = document.getElementById('dlLidPng');
    const dlSidePng = document.getElementById('dlSidePng');

    if (lidImg) lidImg.src = blend.lidImg;
    if (sideImg) sideImg.src = blend.sideImg;
    if (blendTitle) {
      blendTitle.textContent = blend.name;
      blendTitle.style.color = blend.accentColor;
    }
    if (botanicalField) botanicalField.textContent = blend.botanical;
    if (scentField) scentField.textContent = blend.scent;
    if (colorField) colorField.textContent = blend.colorName;

    if (dlLidPdf) dlLidPdf.href = blend.lidPdf;
    if (dlSidePdf) dlSidePdf.href = blend.sidePdf;
    if (dlLidPng) dlLidPng.href = blend.lidImg;
    if (dlSidePng) dlSidePng.href = blend.sideImg;
  }

  // ==================== PRODUCTS ENGINE ====================
  function getProductCategory(prod) {
    const name = (prod.name || '').toLowerCase();
    if (name.includes('combo') || name.includes('offer')) return 'combos';
    if (name.includes('oil')) return 'oils';
    if (name.includes('gel')) return 'gels';
    return 'gels';
  }

  function getProductBadge(prod) {
    const name = (prod.name || '').toLowerCase();
    if (name.includes('arnica')) return 'Bestseller • Muscle Relief';
    if (name.includes('lavender')) return 'Deep Sleep • Relaxing';
    if (name.includes('rosemary')) return 'Joint Mobility • Energizing';
    if (name.includes('juniper')) return 'Warm Relief • Recovery';
    if (name.includes('grape')) return 'Antioxidant • Skin Tone';
    if (name.includes('oil')) return '100% Pure Transdermal';
    if (name.includes('special offer')) return '1+1 Free Value Deal';
    if (name.includes('starter')) return 'Save $9 • 2-Pack';
    if (name.includes('best value')) return 'Maximum Value • 3-Pack';
    return 'Pomorie Black Sea Lye';
  }

  function renderProducts() {
    const grid = document.getElementById('productGrid');
    if (!grid) return;

    let filtered = STATE.products.filter(p => {
      // Category filter
      if (STATE.activeCategory !== 'all') {
        const cat = getProductCategory(p);
        if (cat !== STATE.activeCategory) return false;
      }
      // Search query
      if (STATE.searchQuery.trim() !== '') {
        const q = STATE.searchQuery.toLowerCase();
        const n = (p.name || '').toLowerCase();
        const d = (p.description || '').toLowerCase();
        if (!n.includes(q) && !d.includes(q)) return false;
      }
      return true;
    });

    if (filtered.length === 0) {
      grid.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 60px 20px;">
          <div style="font-family:'Cinzel', serif; font-size:24px; color:var(--text-main); margin-bottom:12px;">No matching formulations found</div>
          <p style="color:var(--text-muted); font-size:14px;">Try searching for "gel", "arnica", "oil", or "combo".</p>
        </div>
      `;
      return;
    }

    grid.innerHTML = filtered.map((prod, idx) => {
      const mainImg = (prod.images && prod.images[0]) || 'assets/mockups/anchialo_luxury_jar_mockup.jpg';
      const cleanDesc = (prod.description || '')
        .replace(/&#010;/g, ' ')
        .replace(/---.*---/g, '')
        .replace(/•/g, '<br>• ')
        .trim();
      const badge = getProductBadge(prod);

      return `
        <div class="product-item-card" data-slug="${prod.slug || ''}">
          <div class="product-thumb-wrap">
            <span class="product-badge-flag">${badge}</span>
            <img src="${mainImg}" alt="${prod.name}" loading="lazy">
          </div>
          <div>
            <div class="card-title">${prod.name}</div>
            <div class="card-price-row">
              <span class="card-price">${formatPrice(prod.price || '49')}</span>
            </div>
            <div class="card-summary">${cleanDesc}</div>
          </div>
          <div>
            <div class="card-cta-row">
              <button class="btn-add-cart" data-idx="${idx}" data-name="${encodeURIComponent(prod.name)}" data-price="${prod.price || '49'}" data-img="${mainImg}">
                Add to Bag
              </button>
              <button class="btn-quick-view" data-slug="${prod.slug || ''}" data-idx="${idx}">
                Quick View
              </button>
            </div>
          </div>
        </div>
      `;
    }).join('');

    // Attach listeners
    grid.querySelectorAll('.btn-add-cart').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const name = decodeURIComponent(btn.getAttribute('data-name'));
        const price = parseFloat(btn.getAttribute('data-price'));
        const img = btn.getAttribute('data-img');
        addToCart(name, price, img);
      });
    });

    grid.querySelectorAll('.btn-quick-view').forEach(btn => {
      btn.addEventListener('click', () => {
        const idx = parseInt(btn.getAttribute('data-idx'));
        openQuickView(filtered[idx]);
      });
    });
  }

  // ==================== QUICK VIEW MODAL ====================
  function openQuickView(prod) {
    if (!prod) return;
    const modal = document.getElementById('quickViewModal');
    if (!modal) return;

    const mainImgEl = document.getElementById('qvMainImg');
    const thumbsContainer = document.getElementById('qvThumbs');
    const titleEl = document.getElementById('qvTitle');
    const priceEl = document.getElementById('qvPrice');
    const badgeEl = document.getElementById('qvBadge');
    const descEl = document.getElementById('qvDesc');
    const addBtn = document.getElementById('qvAddBtn');
    const qtyVal = document.getElementById('qvQtyVal');

    const images = prod.images && prod.images.length > 0 ? prod.images : ['assets/mockups/anchialo_luxury_jar_mockup.jpg'];
    if (mainImgEl) mainImgEl.src = images[0];

    if (thumbsContainer) {
      thumbsContainer.innerHTML = images.map((img, i) => `
        <img src="${img}" class="qv-thumb ${i === 0 ? 'active' : ''}" data-src="${img}" alt="Thumb ${i+1}">
      `).join('');

      thumbsContainer.querySelectorAll('.qv-thumb').forEach(th => {
        th.addEventListener('click', () => {
          thumbsContainer.querySelectorAll('.qv-thumb').forEach(t => t.classList.remove('active'));
          th.classList.add('active');
          if (mainImgEl) mainImgEl.src = th.getAttribute('data-src');
        });
      });
    }

    if (titleEl) titleEl.textContent = prod.name;
    if (priceEl) priceEl.textContent = formatPrice(prod.price || '49');
    if (badgeEl) badgeEl.textContent = getProductBadge(prod);
    if (qtyVal) qtyVal.textContent = '1';

    const cleanDesc = (prod.description || '')
      .replace(/&#010;/g, '<br>')
      .replace(/•/g, '&bull; ');
    if (descEl) descEl.innerHTML = cleanDesc;

    if (addBtn) {
      addBtn.onclick = () => {
        const qty = parseInt(qtyVal ? qtyVal.textContent : '1') || 1;
        addToCart(prod.name, parseFloat(prod.price || '49'), images[0], qty);
        closeModal(modal);
      };
    }

    modal.classList.add('open');
  }

  // ==================== CART DRAWER ====================
  function addToCart(name, priceUSD, image, quantity = 1) {
    const existing = STATE.cart.find(item => item.name === name);
    if (existing) {
      existing.quantity += quantity;
    } else {
      STATE.cart.push({
        id: 'item_' + Date.now() + '_' + Math.floor(Math.random()*1000),
        name,
        priceUSD,
        image,
        quantity
      });
    }

    saveCart();
    updateCartDrawer();
    openCartDrawer();
    showToast(`Added ${quantity}× "${name}" to your bag`, 'Added to Bag');
  }

  function removeFromCart(id) {
    STATE.cart = STATE.cart.filter(item => item.id !== id);
    saveCart();
    updateCartDrawer();
  }

  function updateItemQty(id, delta) {
    const item = STATE.cart.find(i => i.id === id);
    if (!item) return;
    item.quantity += delta;
    if (item.quantity <= 0) {
      removeFromCart(id);
    } else {
      saveCart();
      updateCartDrawer();
    }
  }

  function saveCart() {
    localStorage.setItem('anchialo_cart', JSON.stringify(STATE.cart));
    updateCartBadge();
  }

  function updateCartBadge() {
    const totalCount = STATE.cart.reduce((sum, i) => sum + i.quantity, 0);
    document.querySelectorAll('.cart-count-badge').forEach(badge => {
      badge.textContent = totalCount;
    });
  }

  function updateCartDrawer() {
    const list = document.getElementById('cartItemsList');
    const subtotalEl = document.getElementById('cartSubtotal');
    const shippingEl = document.getElementById('cartShipping');
    const progressBar = document.getElementById('shippingProgressBar');
    const progressText = document.getElementById('shippingProgressText');

    if (!list) return;

    if (STATE.cart.length === 0) {
      list.innerHTML = `
        <div style="text-align:center; padding: 48px 16px; color:var(--text-muted);">
          <div style="font-size:36px; margin-bottom:12px;">🛍️</div>
          <div style="font-family:'Cinzel', serif; font-size:18px; color:var(--text-main); margin-bottom:8px;">Your Bag is Empty</div>
          <p style="font-size:13px;">Explore our Pomorie Dual Magnesium mineral formulations.</p>
        </div>
      `;
      if (subtotalEl) subtotalEl.textContent = formatPrice(0);
      if (shippingEl) shippingEl.textContent = 'Calculated at checkout';
      if (progressBar) progressBar.style.width = '0%';
      if (progressText) progressText.innerHTML = `Add <b>${formatPrice(STATE.freeShippingThresholdUSD)}</b> more for <b>FREE Global Air Express</b>`;
      return;
    }

    let subtotalUSD = 0;
    list.innerHTML = STATE.cart.map(item => {
      const lineTotalUSD = item.priceUSD * item.quantity;
      subtotalUSD += lineTotalUSD;

      return `
        <div class="cart-item">
          <img src="${item.image}" alt="${item.name}">
          <div class="cart-item-details">
            <div class="cart-item-title">${item.name}</div>
            <div class="cart-item-price">${formatPrice(item.priceUSD)}</div>
            <div class="cart-qty-ctrl">
              <button class="cart-qty-btn btn-dec" data-id="${item.id}">-</button>
              <span style="font-size:13px; font-weight:700;">${item.quantity}</span>
              <button class="cart-qty-btn btn-inc" data-id="${item.id}">+</button>
              <button style="background:none; border:none; color:#C62828; font-size:11px; cursor:pointer; margin-left:auto;" class="btn-del" data-id="${item.id}">Remove</button>
            </div>
          </div>
        </div>
      `;
    }).join('');

    // Attach cart list events
    list.querySelectorAll('.btn-dec').forEach(b => b.addEventListener('click', () => updateItemQty(b.getAttribute('data-id'), -1)));
    list.querySelectorAll('.btn-inc').forEach(b => b.addEventListener('click', () => updateItemQty(b.getAttribute('data-id'), 1)));
    list.querySelectorAll('.btn-del').forEach(b => b.addEventListener('click', () => removeFromCart(b.getAttribute('data-id'))));

    if (subtotalEl) subtotalEl.textContent = formatPrice(subtotalUSD);

    // Free shipping calculation
    const remainingUSD = STATE.freeShippingThresholdUSD - subtotalUSD;
    if (remainingUSD <= 0) {
      if (progressBar) progressBar.style.width = '100%';
      if (progressText) progressText.innerHTML = `🎉 <b>You unlocked FREE Global Air Express Shipping!</b>`;
      if (shippingEl) shippingEl.textContent = 'FREE';
    } else {
      const pct = Math.min(100, Math.round((subtotalUSD / STATE.freeShippingThresholdUSD) * 100));
      if (progressBar) progressBar.style.width = pct + '%';
      if (progressText) progressText.innerHTML = `Add <b>${formatPrice(remainingUSD)}</b> more for <b>FREE Global Express</b>`;
      if (shippingEl) shippingEl.textContent = formatPrice(15);
    }
  }

  function openCartDrawer() {
    const drawer = document.getElementById('cartDrawer');
    const overlay = document.getElementById('cartOverlay');
    if (drawer) drawer.classList.add('open');
    if (overlay) overlay.classList.add('open');
  }

  function closeCartDrawer() {
    const drawer = document.getElementById('cartDrawer');
    const overlay = document.getElementById('cartOverlay');
    if (drawer) drawer.classList.remove('open');
    if (overlay) overlay.classList.remove('open');
  }

  // ==================== CHECKOUT SIMULATION ====================
  function triggerCheckout() {
    if (STATE.cart.length === 0) {
      showToast('Your bag is empty! Please add products before checking out.', 'Empty Bag');
      return;
    }

    closeCartDrawer();
    const modal = document.getElementById('checkoutModal');
    if (!modal) return;

    const orderNum = 'ANC-' + Math.floor(100000 + Math.random() * 900000);
    const subtotalUSD = STATE.cart.reduce((sum, i) => sum + (i.priceUSD * i.quantity), 0);
    const shippingUSD = subtotalUSD >= STATE.freeShippingThresholdUSD ? 0 : 15;
    const grandTotalUSD = subtotalUSD + shippingUSD;

    const orderNumEl = document.getElementById('checkoutOrderNum');
    const summaryCard = document.getElementById('checkoutSummaryCard');

    if (orderNumEl) orderNumEl.textContent = `Order Protocol Ref: #${orderNum}`;
    if (summaryCard) {
      summaryCard.innerHTML = `
        <div class="checkout-summary-row">
          <span>Items Ordered (${STATE.cart.reduce((s, i) => s + i.quantity, 0)} units):</span>
          <span>${formatPrice(subtotalUSD)}</span>
        </div>
        <div class="checkout-summary-row">
          <span>Courier Shipping (Black Sea Express):</span>
          <span>${shippingUSD === 0 ? 'FREE' : formatPrice(shippingUSD)}</span>
        </div>
        <div class="checkout-summary-row">
          <span>Dispatched from:</span>
          <span>Pomorie Lab 8200, Bulgaria</span>
        </div>
        <div class="checkout-summary-row total">
          <span>Grand Total:</span>
          <span>${formatPrice(grandTotalUSD)}</span>
        </div>
      `;
    }

    modal.classList.add('open');
    // Clear cart upon successful order protocol
    STATE.cart = [];
    saveCart();
    updateCartDrawer();
    showToast(`Order #${orderNum} registered successfully!`, 'Sovereign Order Confirmed');
  }

  // ==================== CLINICAL ARTICLES ENGINE ====================
  function renderBlog() {
    const grid = document.getElementById('blogGrid');
    if (!grid) return;

    if (!STATE.blogPosts || STATE.blogPosts.length === 0) {
      grid.innerHTML = `<p style="text-align:center; color:var(--text-muted); grid-column:1/-1;">Loading clinical research papers...</p>`;
      return;
    }

    grid.innerHTML = STATE.blogPosts.slice(0, 9).map((post, idx) => {
      const img = (post.image && post.image.url) ? post.image.url : 'assets/mockups/anchialo_luxury_jar_mockup.jpg';
      const cleanSnippet = (post.description || '').slice(0, 140) + '...';
      const dateFormatted = post.datePublished ? new Date(post.datePublished).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' }) : 'Verified Study';

      return `
        <div class="blog-card">
          <div class="blog-img-wrap">
            <img src="${img}" alt="${post.title}" loading="lazy">
          </div>
          <div class="blog-body">
            <div>
              <div class="blog-date">Clinical Study • ${dateFormatted}</div>
              <div class="blog-title">${post.title}</div>
              <div class="blog-snippet">${cleanSnippet}</div>
            </div>
            <button class="btn-read-article" data-idx="${idx}">
              Read Full Clinical Study &rarr;
            </button>
          </div>
        </div>
      `;
    }).join('');

    grid.querySelectorAll('.btn-read-article').forEach(btn => {
      btn.addEventListener('click', () => {
        const idx = parseInt(btn.getAttribute('data-idx'));
        openArticleModal(STATE.blogPosts[idx]);
      });
    });
  }

  function openArticleModal(post) {
    if (!post) return;
    const modal = document.getElementById('articleModal');
    if (!modal) return;

    const titleEl = document.getElementById('articleModalTitle');
    const metaEl = document.getElementById('articleModalMeta');
    const bodyEl = document.getElementById('articleModalBody');

    if (titleEl) titleEl.textContent = post.title;
    if (metaEl) {
      const dateFormatted = post.datePublished ? new Date(post.datePublished).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }) : 'Verified Study';
      metaEl.innerHTML = `By <b>${post.author || 'Sotir Kichukov & Anchialo Balneology Labs'}</b> • Published: ${dateFormatted} • Reading time: 5 min`;
    }
    if (bodyEl) {
      const paragraphs = (post.body_text || post.description || '').split('\n').filter(p => p.trim() !== '');
      bodyEl.innerHTML = paragraphs.map(p => `<p style="margin-bottom:16px; font-size:15px; line-height:1.75; color:var(--text-main);">${p}</p>`).join('');
    }

    modal.classList.add('open');
  }

  function closeModal(modal) {
    if (modal) modal.classList.remove('open');
  }

  // ==================== GLOBAL INITIALIZATION ====================
  document.addEventListener('DOMContentLoaded', () => {
    // 1. Apply persisted theme & currency
    applyTheme(STATE.theme);
    const currSelect = document.getElementById('currencySelector');
    if (currSelect) {
      currSelect.value = STATE.currency;
      currSelect.addEventListener('change', (e) => setCurrency(e.target.value));
    }

    const themeBtn = document.getElementById('themeToggleBtn');
    if (themeBtn) themeBtn.addEventListener('click', toggleTheme);

    // 2. Mobile drawer
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const mobileDrawer = document.getElementById('mobileNavDrawer');
    if (mobileMenuBtn && mobileDrawer) {
      mobileMenuBtn.addEventListener('click', () => mobileDrawer.classList.toggle('open'));
      mobileDrawer.querySelectorAll('a').forEach(a => {
        a.addEventListener('click', () => mobileDrawer.classList.remove('open'));
      });
    }

    // 3. Cart events
    const cartToggleBtns = document.querySelectorAll('.btn-cart-toggle');
    cartToggleBtns.forEach(btn => btn.addEventListener('click', openCartDrawer));

    const cartCloseBtn = document.getElementById('cartCloseBtn');
    if (cartCloseBtn) cartCloseBtn.addEventListener('click', closeCartDrawer);

    const cartOverlay = document.getElementById('cartOverlay');
    if (cartOverlay) cartOverlay.addEventListener('click', closeCartDrawer);

    const checkoutBtn = document.getElementById('cartCheckoutBtn');
    if (checkoutBtn) checkoutBtn.addEventListener('click', triggerCheckout);

    // 4. Modal close handlers
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) closeModal(overlay);
      });
      const closeBtn = overlay.querySelector('.modal-close');
      if (closeBtn) closeBtn.addEventListener('click', () => closeModal(overlay));
    });

    // 5. Quantity controls in Quick View
    const qvDec = document.getElementById('qvQtyDec');
    const qvInc = document.getElementById('qvQtyInc');
    const qvVal = document.getElementById('qvQtyVal');
    if (qvDec && qvInc && qvVal) {
      qvDec.addEventListener('click', () => {
        let v = parseInt(qvVal.textContent) || 1;
        if (v > 1) qvVal.textContent = v - 1;
      });
      qvInc.addEventListener('click', () => {
        let v = parseInt(qvVal.textContent) || 1;
        qvVal.textContent = v + 1;
      });
    }

    // 6. Search Bar & Filters
    const searchInput = document.getElementById('catalogSearchInput');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        STATE.searchQuery = e.target.value;
        renderProducts();
      });
    }

    const filterBtns = document.querySelectorAll('.filter-btn');
    filterBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        filterBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        STATE.activeCategory = btn.getAttribute('data-cat') || 'all';
        renderProducts();
      });
    });

    // 7. Load Data (Immediate from dataset.js or fallback to fetch)
    if (window.ANCHIALO_DATA && window.ANCHIALO_DATA.products && window.ANCHIALO_DATA.blog) {
      STATE.products = window.ANCHIALO_DATA.products;
      STATE.blogPosts = window.ANCHIALO_DATA.blog;
      renderProducts();
      renderBlog();
      initStudio();
      updateCartDrawer();
      updateCartBadge();
    } else {
      Promise.all([
        fetch('data/products.json').then(r => r.json()).catch(() => []),
        fetch('data/blog_posts.json').then(r => r.json()).catch(() => [])
      ]).then(([products, blogPosts]) => {
        STATE.products = products;
        STATE.blogPosts = blogPosts;

        renderProducts();
        renderBlog();
        initStudio();
        updateCartDrawer();
        updateCartBadge();
      });
    }
  });

})();
