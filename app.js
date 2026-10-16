/**
 * ANCHIALO — OFFICIAL PLATFORM CLIENT ENGINE
 * Pure Pomorie Black Sea Mineral Balneotherapy
 * High-End Apothecary Interactive Experience
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

  const SHARED_TEXTS = {
    usage: "Apply topically to the desired area and massage thoroughly into the skin. Leave it on for 30 minutes to several hours, then rinse off with water. For best results, leave it on overnight to support deeper relaxation and recovery. Do not apply to open wounds, as the salts may cause stinging or irritation.",
    warning: "For external use only. Keep out of reach of children. Avoid contact with eyes. This product is not a substitute for medical treatment. Storage: Store at 5°C – 25°C / 41.0°F – 77.0°F. Note: Black Sea lye may be stored at higher temperatures, as long as it is not exposed to direct sunlight.",
    heritage: "Black Sea lye is a mineral-rich liquid that forms naturally during the evaporation of seawater in salt lakes along the Bulgarian Black Sea coast. As the water evaporates, salt settles at the bottom, and a dense, dark, non-crystallised liquid called lye forms on top. This lye contains high levels of natural minerals like magnesium sulfate, magnesium chloride, and sodium chloride. Traditionally used to support skin health, ease muscle and joint discomfort, and help the body recover after physical activity.",
    producer: "Produced by: AZIMUT 6000 Ltd, Bulgaria, Pomorie 8200, Ivan Vazov 18 str. Tel: +359887470548 | E-mail: grudev_g@abv.bg. GTIN-13 Barcode: 3 800230 111746. Batch / Expiry: Lot № 07 / 25.12.2027. Net volume: 300 g ℮. PAO 12M | ♳ PET 1 Recyclable. ISO 22716 GMP Certified."
  };

  const BLENDS = {
    arnica: {
      id: 'arnica',
      name: 'ARNICA BLEND — DUAL MAGNESIUM COMPLEX',
      accentColor: '#C69214',
      bgGlow: 'rgba(198, 146, 20, 0.35)',
      lidImg: 'labels/production_ready/high_res_png_300dpi/Top_Lid_Arnica_86mm_300dpi.png',
      sideImg: 'labels/production_ready/high_res_png_300dpi/Side_Label_Arnica_280x38mm_300dpi.png',
      sidePdf: 'labels/production_ready/pdf_print_ready_cmyk/Side_Label_Arnica_280x38mm_PRINT_READY.pdf',
      lidPdf: 'labels/production_ready/pdf_print_ready_cmyk/Top_Lid_Arnica_86mm_PRINT_READY.pdf',
      botanical: 'Arnica Montana flower extract (sesquiterpene lactones for micro-circulation)',
      scent: 'Warm herbal & fresh mountain meadow',
      colorName: 'Warm Goldenrod (#C69214)',
      purpose: "This is a fast-absorbing topical body gel formulated to provide the natural benefits of magnesium sulfate and magnesium chloride, absorbed through the skin to help relax and nourish the body. It supports hydration and contributes to a feeling of refreshment and revitalisation. The high magnesium content may assist in maintaining healthy skin and supporting overall well-being. Enriched with Arnica extract, traditionally used to soothe and comfort the body.",
      inci: "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, GLYCERINE, ARNICA MONTANA FLOWER EXTRACT."
    },
    lavender: {
      id: 'lavender',
      name: 'LAVENDER BLEND — DUAL MAGNESIUM COMPLEX',
      accentColor: '#6B5B95',
      bgGlow: 'rgba(107, 91, 149, 0.35)',
      lidImg: 'labels/production_ready/high_res_png_300dpi/Top_Lid_Lavender_86mm_300dpi.png',
      sideImg: 'labels/production_ready/high_res_png_300dpi/Side_Label_Lavender_280x38mm_300dpi.png',
      sidePdf: 'labels/production_ready/pdf_print_ready_cmyk/Side_Label_Lavender_280x38mm_PRINT_READY.pdf',
      lidPdf: 'labels/production_ready/pdf_print_ready_cmyk/Top_Lid_Lavender_86mm_PRINT_READY.pdf',
      botanical: 'Lavandula Angustifolia pure essential oil (linalool & linalyl acetate)',
      scent: 'Calming Mediterranean twilight lavender',
      colorName: 'Royal Lavender (#6B5B95)',
      purpose: "This is a topical body gel formulated to provide the natural benefits of magnesium sulfate and magnesium chloride, absorbed through the skin to help relax and nourish the body. It supports hydration and contributes to a feeling of refreshment and revitalisation. The high magnesium content may assist in maintaining healthy skin and supporting overall well-being. With Lavender extract, known for its calming and relaxing properties.",
      inci: "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, GLYCERINE, LAVANDULA ANGUSTIFOLIA FLOWER EXTRACT."
    },
    rosemary: {
      id: 'rosemary',
      name: 'ROSEMARY BLEND — DUAL MAGNESIUM COMPLEX',
      accentColor: '#4B6B38',
      bgGlow: 'rgba(75, 107, 56, 0.35)',
      lidImg: 'labels/production_ready/high_res_png_300dpi/Top_Lid_Rosemary_86mm_300dpi.png',
      sideImg: 'labels/production_ready/high_res_png_300dpi/Side_Label_Rosemary_280x38mm_300dpi.png',
      sidePdf: 'labels/production_ready/pdf_print_ready_cmyk/Side_Label_Rosemary_280x38mm_PRINT_READY.pdf',
      lidPdf: 'labels/production_ready/pdf_print_ready_cmyk/Top_Lid_Rosemary_86mm_PRINT_READY.pdf',
      botanical: 'Rosmarinus Officinalis leaf oil (rosmarinic acid & cineole)',
      scent: 'Invigorating pine-camphor herbal tone',
      colorName: 'Forest Rosemary (#4B6B38)',
      purpose: "This is a topical body gel formulated to provide the natural benefits of magnesium sulfate and magnesium chloride, absorbed through the skin to help relax and nourish the body. It supports hydration and contributes to a feeling of refreshment and revitalisation. The high magnesium content may assist in maintaining healthy skin and supporting overall well-being. Enhanced with Rosemary extract, traditionally used to support circulation and invigorate the skin.",
      inci: "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, GLYCERINE, ROSMARINUS OFFICINALIS LEAF POWDER EXTRACT."
    },
    juniper: {
      id: 'juniper',
      name: 'JUNIPER BLEND — DUAL MAGNESIUM COMPLEX',
      accentColor: '#285844',
      bgGlow: 'rgba(40, 88, 68, 0.35)',
      lidImg: 'labels/production_ready/high_res_png_300dpi/Top_Lid_Juniper_86mm_300dpi.png',
      sideImg: 'labels/production_ready/high_res_png_300dpi/Side_Label_Juniper_280x38mm_300dpi.png',
      sidePdf: 'labels/production_ready/pdf_print_ready_cmyk/Side_Label_Juniper_280x38mm_PRINT_READY.pdf',
      lidPdf: 'labels/production_ready/pdf_print_ready_cmyk/Top_Lid_Juniper_86mm_PRINT_READY.pdf',
      botanical: 'Juniperus Communis fruit oil (alpha-pinene warming complex)',
      scent: 'Crisp alpine coniferous wood notes',
      colorName: 'Deep Pine Juniper (#285844)',
      purpose: "This is a topical body gel formulated to provide the natural benefits of magnesium sulfate and magnesium chloride, absorbed through the skin to help relax and nourish the body. It supports hydration and contributes to a feeling of refreshment and revitalisation. The high magnesium content may assist in maintaining healthy skin and supporting overall well-being. Infused with Juniper extract, valued for its refreshing and revitalising qualities.",
      inci: "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, PARFUM, GLYCERINE, JUNIPERUS CHINENSIS LEAF EXTRACT."
    },
    grape: {
      id: 'grape',
      name: 'GRAPE BLEND — DUAL MAGNESIUM COMPLEX',
      accentColor: '#7E2A3C',
      bgGlow: 'rgba(126, 42, 60, 0.35)',
      lidImg: 'labels/production_ready/high_res_png_300dpi/Top_Lid_Grape_86mm_300dpi.png',
      sideImg: 'labels/production_ready/high_res_png_300dpi/Side_Label_Grape_280x38mm_300dpi.png',
      sidePdf: 'labels/production_ready/pdf_print_ready_cmyk/Side_Label_Grape_280x38mm_PRINT_READY.pdf',
      lidPdf: 'labels/production_ready/pdf_print_ready_cmyk/Top_Lid_Grape_86mm_PRINT_READY.pdf',
      botanical: 'Vitis Vinifera (Grape) seed extract (potent proanthocyanidins & resveratrol)',
      scent: 'Sun-drenched Black Sea vineyard bouquet',
      colorName: 'Burgundy Grape (#7E2A3C)',
      purpose: "This is a topical body gel formulated to provide the natural benefits of magnesium sulfate and magnesium chloride, absorbed through the skin to help relax and nourish the body. It supports hydration and contributes to a feeling of refreshment and revitalisation. The high magnesium content may assist in maintaining healthy skin and supporting overall well-being. Lightly fragranced with a pleasant Grape aroma for a fresh and enjoyable experience.",
      inci: "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, PARFUM, GLYCERINE."
    }
  };

  // Packaging HUD State
  let activeTextTab = 'purpose';
  let isPhiGridActive = false;

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
      themeBtn.innerHTML = theme === 'dark' 
        ? '<span class="mono" id="themeText" style="font-size:11px; font-weight:700; letter-spacing:1px;">LIGHT</span>' 
        : '<span class="mono" id="themeText" style="font-size:11px; font-weight:700; letter-spacing:1px;">OBSIDIAN</span>';
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
      <div class="status-dot bg-emerald" style="margin-right:0;"></div>
      <div>
        <div style="font-weight: 800; font-family:'JetBrains Mono', monospace; font-size:11px; margin-bottom:2px; color:var(--gold-primary); text-transform:uppercase; letter-spacing:1px;">${title}</div>
        <div style="font-size:13px; color:#EAE5DD;">${message}</div>
      </div>
    `;

    container.appendChild(toast);

    setTimeout(() => {
      toast.classList.add('hide');
      setTimeout(() => toast.remove(), 320);
    }, 3200);
  }

  // ==================== PACKAGING HUD STUDIO ====================
  function initStudio() {
    // 1. Variant tabs
    const tabs = document.querySelectorAll('.blend-tab');
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        const blendKey = tab.getAttribute('data-blend');
        switchBlend(blendKey);
      });
    });

    // 2. Zoom controls for Side Wrap
    document.querySelectorAll('.hud-pill-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.hud-pill-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const zoom = btn.getAttribute('data-zoom');
        const wrap = document.getElementById('sideLabelPanWrap');
        if (!wrap) return;
        wrap.className = 'side-label-pan-wrap';
        if (zoom === '2x') wrap.classList.add('zoomed-2x');
        if (zoom === '3x') wrap.classList.add('zoomed-3x');
        showToast(`Label magnification: ${zoom.toUpperCase()}`, 'Packaging Loupe');
      });
    });

    // 3. Golden Ratio Grid toggle
    const phiBtn = document.getElementById('btnTogglePhiGrid');
    const phiOverlay = document.getElementById('phiGridOverlay');
    if (phiBtn && phiOverlay) {
      phiBtn.addEventListener('click', () => {
        isPhiGridActive = !isPhiGridActive;
        phiOverlay.classList.toggle('active', isPhiGridActive);
        phiBtn.classList.toggle('active', isPhiGridActive);
        showToast(isPhiGridActive ? 'Golden Ratio (Φ = 1.618) Grid Overlay Enabled' : 'Golden Ratio Grid Disabled', 'HUD Grid');
      });
    }

    // 4. Horizontal drag-to-pan on side label container
    const sideBox = document.getElementById('sideLabelBox');
    if (sideBox) {
      let isDown = false;
      let startX;
      let scrollLeft;

      sideBox.addEventListener('mousedown', (e) => {
        isDown = true;
        sideBox.style.cursor = 'grabbing';
        startX = e.pageX - sideBox.offsetLeft;
        scrollLeft = sideBox.scrollLeft;
      });

      sideBox.addEventListener('mouseleave', () => {
        isDown = false;
        sideBox.style.cursor = 'grab';
      });

      sideBox.addEventListener('mouseup', () => {
        isDown = false;
        sideBox.style.cursor = 'grab';
      });

      sideBox.addEventListener('mousemove', (e) => {
        if (!isDown) return;
        e.preventDefault();
        const x = e.pageX - sideBox.offsetLeft;
        const walk = (x - startX) * 1.6;
        sideBox.scrollLeft = scrollLeft - walk;
      });
    }

    // 5. Master text inspector tabs
    document.querySelectorAll('.hud-inspector-tabs .btn-text-tab').forEach(btn => {
      btn.addEventListener('click', () => {
        const tabKey = btn.getAttribute('data-tab');
        updateMasterTextInspector(tabKey);
      });
    });

    // Initial variant load
    switchBlend('arnica');
    updateMasterTextInspector('purpose');
  }

  function switchBlend(blendKey) {
    const blend = BLENDS[blendKey];
    if (!blend) return;
    STATE.selectedBlend = blendKey;

    // Update active tab buttons
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

    // Update images in HUD
    const lidImg = document.getElementById('studioLidImg');
    const sideImg = document.getElementById('studioSideImg');

    if (lidImg) lidImg.src = blend.lidImg;
    if (sideImg) sideImg.src = blend.sideImg;

    // Update Telemetry Bar & Headers
    const hudActiveVariantTag = document.getElementById('hudActiveVariantTag');
    const hudLidTitle = document.getElementById('hudLidTitle');
    const hudWrapTitle = document.getElementById('hudWrapTitle');
    const hudBotanicalTitle = document.getElementById('hudBotanicalTitle');
    const hudBotanicalAction = document.getElementById('hudBotanicalAction');

    if (hudActiveVariantTag) hudActiveVariantTag.textContent = `VARIANT: ${blend.name.split('—')[0].trim()}`;
    if (hudLidTitle) hudLidTitle.textContent = `TOP LID Ø 86.0 MM — ${blend.name.split('—')[0].trim()}`;
    if (hudWrapTitle) hudWrapTitle.textContent = `SIDE WRAP LABEL — ${blend.name.split('—')[0].trim()} (280.0 × 38.0 MM @ 300 DPI)`;
    if (hudBotanicalTitle) hudBotanicalTitle.textContent = blend.botanical.split('(')[0].trim();
    if (hudBotanicalAction) hudBotanicalAction.textContent = blend.scent;

    // Update Download Links
    const dlLidPdf = document.getElementById('dlLidPdf');
    const dlSidePdf = document.getElementById('dlSidePdf');
    const dlLidPng = document.getElementById('dlLidPng');
    const dlSidePng = document.getElementById('dlSidePng');

    if (dlLidPdf) dlLidPdf.href = blend.lidPdf;
    if (dlSidePdf) dlSidePdf.href = blend.sidePdf;
    if (dlLidPng) dlLidPng.href = blend.lidImg;
    if (dlSidePng) dlSidePng.href = blend.sideImg;

    updateMasterTextInspector(activeTextTab);
  }

  function updateMasterTextInspector(tabKey = activeTextTab) {
    activeTextTab = tabKey;
    const blend = BLENDS[STATE.selectedBlend];
    if (!blend) return;

    const heading = document.getElementById('inspectorHeading');
    const code = document.getElementById('inspectorCode');
    const body = document.getElementById('inspectorBody');
    if (!heading || !body) return;

    const contentMap = {
      purpose: {
        code: 'SEC-01 // THERAPEUTIC PURPOSE',
        title: 'Purpose &amp; Formulation Benefits',
        text: blend.purpose
      },
      inci: {
        code: 'SEC-02 // INCI FORMULATION',
        title: 'Full INCI Ingredients (Australian TGA 2025 Standard)',
        text: `<b>Ingredients List:</b><br>${blend.inci}`
      },
      usage: {
        code: 'SEC-03 // APPLICATION PROTOCOL',
        title: 'Directions for Usage &amp; Overnight Recovery',
        text: SHARED_TEXTS.usage
      },
      warning: {
        code: 'SEC-04 // PRECAUTIONS & STORAGE',
        title: 'Precautions &amp; Recommended Storage',
        text: SHARED_TEXTS.warning
      },
      heritage: {
        code: 'SEC-05 // MINERAL ORIGIN',
        title: 'What is Pomorie Black Sea Lye?',
        text: SHARED_TEXTS.heritage
      },
      producer: {
        code: 'SEC-06 // BATCH & PRODUCER',
        title: 'Manufacturer &amp; Batch Traceability',
        text: SHARED_TEXTS.producer
      }
    };

    const item = contentMap[tabKey] || contentMap.purpose;
    if (code) code.textContent = item.code;
    heading.innerHTML = item.title;
    body.innerHTML = item.text;

    document.querySelectorAll('.hud-inspector-tabs .btn-text-tab').forEach(btn => {
      if (btn.getAttribute('data-tab') === tabKey) btn.classList.add('active');
      else btn.classList.remove('active');
    });
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
      const mainImg = (prod.images && prod.images[0]) || 'assets/images/products/06_file.png';
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

    const images = prod.images && prod.images.length > 0 ? prod.images : ['assets/images/products/06_file.png'];
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
          <div class="mono" style="font-size:12px; font-weight:700; color:var(--text-light); margin-bottom:12px;">[EMPTY BAG]</div>
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
      if (progressText) progressText.innerHTML = `<b>QUALIFIED FOR FREE GLOBAL AIR EXPRESS SHIPPING</b>`;
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

    if (orderNumEl) orderNumEl.textContent = `Order Reference: #${orderNum}`;
    if (summaryCard) {
      summaryCard.innerHTML = `
        <div class="checkout-summary-row">
          <span>Items Ordered (${STATE.cart.reduce((s, i) => s + i.quantity, 0)} units):</span>
          <span>${formatPrice(subtotalUSD)}</span>
        </div>
        <div class="checkout-summary-row">
          <span>Express Delivery (Black Sea Express):</span>
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
    // Clear cart upon order
    STATE.cart = [];
    saveCart();
    updateCartDrawer();
    showToast(`Order #${orderNum} registered successfully!`, 'Order Confirmed');
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
      const img = (post.image && post.image.url) ? post.image.url : 'assets/images/products/06_file.png';
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
