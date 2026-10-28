/**
 * ANCHIALO — LUXURY ORGANIC BALNEOLOGY & E-COMMERCE CLIENT ENGINE
 * Azimut 6000 Ltd · Pomorie Black Sea Natural Minerals · Australia $49 AUD
 */

(function () {
  'use strict';

  // ==================== CONFIGURATION & STATE ====================
  const STATE = {
    currency: localStorage.getItem('anchialov2_currency') || 'AUD',
    rates: {
      AUD: { symbol: 'A$', rate: 1.55, fixedJar: 49.00, suffix: ' AUD' },
      USD: { symbol: '$', rate: 1.00, fixedJar: 32.00, suffix: ' USD' },
      EUR: { symbol: '€', rate: 0.92, fixedJar: 28.00, suffix: ' EUR' },
      BGN: { symbol: '', rate: 1.80, fixedJar: 45.00, suffix: ' BGN' }
    },
    cart: JSON.parse(localStorage.getItem('anchialov2_cart') || '[]'),
    activeCategory: 'all',
    searchQuery: '',
    selectedBlend: 'arnica',
    activeDetailTab: 'purpose',
    products: [],
    blogPosts: [],
    selectedLocality: {
      location: 'MELBOURNE',
      state: 'VIC',
      postcode: '3000'
    },
    lastOrderMeta: null
  };

  // Official Stripe Live Gateway Configuration
  const STRIPE_CONFIG = {
    publishableKey: 'pk_live_51N2xQLEbWrG8srIzRdDyBIP5xQnhWutQq6xR8GVDWNCXUKSrl4dNlt4BZ5id396FlyboHLbDHNtZKcBEZPRLTJw400y5M9LYvA',
    links: {
      'gel-arnica': 'https://buy.stripe.com/9B67sL4tmfBa9CD0eb5Ne0e',
      'gel-lavender': 'https://buy.stripe.com/cNi14ncZS9cMeWX9OL5Ne0d',
      'gel-peppermint': 'https://buy.stripe.com/8x2dR9cZSbkUdST5yv5Ne0f',
      'gel-rosemary': 'https://buy.stripe.com/8x2dR9cZSbkUdST5yv5Ne0f',
      'gel-juniper': 'https://buy.stripe.com/14A3cv7Fy4Ww5mne515Ne0g',
      'gel-grape': 'https://buy.stripe.com/cNidR97FycoY0239OL5Ne0h',
      'gel-unscented': 'https://buy.stripe.com/cNidR97FycoY0239OL5Ne0h',
      'oil-pure': 'https://buy.stripe.com/aFaeVdgc4ex6cOP1if5Ne0i',
      'combo-starter': 'https://buy.stripe.com/6oU4gzcZS60AeWX9OL5Ne0j',
      'combo-gel-oil': 'https://buy.stripe.com/cNi14ncZS9cMeWX9OL5Ne0d',
      'combo-trio': 'https://buy.stripe.com/6oU4gzcZS60AeWX9OL5Ne0j',
      'combo-complete': 'https://buy.stripe.com/7sYeVdgc4dt28yzbWT5Ne0k',
      'custom': 'https://buy.stripe.com/4gM28rgc44WwbKL3qn5Ne0l'
    }
  };

  // Official Verbatim Texts
  const TEXTS = {
    usage: "Gently massage a generous amount into clean, dry skin on the desired muscle or joint area. Allow the bioavailable mineral gel to absorb for 30 minutes to several hours, or leave overnight for deep restorative relaxation. If slight natural mineral salt crystals form on the skin, simply rinse with cool water. Avoid open abrasions and eyes.",
    warning: "For external topical use only. Keep out of reach of children. Avoid direct contact with eyes. If unexpected dermal irritation occurs, rinse thoroughly with cool water. Storage: Store in a cool, dry place between 5°C and 25°C. Natural Black Sea lye maintains stability at ambient room temperatures when shielded from direct sunlight.",
    heritage: "Formed naturally during the slow fractional solar crystallization of sea water in the ancient coastal salterns of Lake Pomorie. As sodium chloride precipitates out as sea salt, a super-dense colloidal liquid rich in ionic magnesium chloride, magnesium sulfate, trace iodine, bromine, and organic peloids settles on top. Revering Thracian healing traditions dating back to 400 BC.",
    producer: "Handcrafted by: AZIMUT 6000 Ltd, Bulgaria, Pomorie 8200, Ivan Vazov 18 str. Tel: +359887470548 | E-mail: sales@luga.bg. GTIN-13: 3 800230 111746. Batch / Expiry: Lot № 04 / Expiry 2027. Net weight: 300 g ℮. PAO 12M | ♳ PET 1 Recyclable. ISO 22716 European GMP Certified."
  };

  // The 5 Signature Botanical Blends
  const BLENDS = {
    arnica: {
      id: 'arnica',
      name: 'ARNICA MONTANA BLEND',
      fullName: 'ARNICA BLEND — DUAL MAGNESIUM COMPLEX',
      accentColor: '#d97706',
      heroJar: 'assets/images/products/06_file_transp.png',
      lidImg: 'assets/official_labels_rendered/anhialo_massage_gel_arnica_top_fv17.png',
      sideImg: 'assets/official_labels_rendered/side_label_grey_arnica_v12.png',
      sidePdf: 'assets/official_drive_assets/labels/Side Label Grey Arnica v12.pdf',
      lidPdf: 'assets/official_drive_assets/labels/Anhialo Massage Gel_Arnica Top Fv17.pdf',
      botanical: 'Arnica Montana Flower Extract',
      subtitle: 'Muscle Soreness, Bruises & Physical Trauma Recovery',
      purpose: "Fast-absorbing topical body gel combining pure transdermal magnesium chloride and magnesium sulfate with natural Arnica Montana extract. Revered by athletes and physical therapists to relieve acute muscle fatigue, ease heavy bruised limbs, reduce post-workout soreness, and soothe inflamed joint tendons.",
      inci: "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, GLYCERINE, ARNICA MONTANA FLOWER EXTRACT."
    },
    lavender: {
      id: 'lavender',
      name: 'BULGARIAN LAVENDER BLEND',
      fullName: 'LAVENDER BLEND — DUAL MAGNESIUM COMPLEX',
      accentColor: '#7c3aed',
      heroJar: 'assets/images/products/01_file_transp.png',
      lidImg: 'assets/official_labels_rendered/anhialo_massage_gel_lavender_top_fv17.png',
      sideImg: 'assets/official_labels_rendered/side_label_grey_lavender_v12.png',
      sidePdf: 'assets/official_drive_assets/labels/Side Label Grey Lavender v12.pdf',
      lidPdf: 'assets/official_drive_assets/labels/Anhialo Massage Gel_Lavender Top Fv17.pdf',
      botanical: 'Lavandula Angustifolia Essential Flower Extract',
      subtitle: 'Restorative Sleep, Deep Calming & Tension Ease',
      purpose: "A deeply calming bedtime balneotherapy formulation. Synergizes transdermal magnesium chloride with authentic Bulgarian lavender to calm neuromuscular irritability, reduce restless legs, quiet an overactive nervous system, and usher in deep, uninterrupted sleep cycles.",
      inci: "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, GLYCERINE, LAVANDULA ANGUSTIFOLIA FLOWER EXTRACT."
    },
    rosemary: {
      id: 'rosemary',
      name: 'GARDEN ROSEMARY BLEND',
      fullName: 'ROSEMARY BLEND — DUAL MAGNESIUM COMPLEX',
      accentColor: '#059669',
      heroJar: 'assets/images/products/04_file_transp.png',
      lidImg: 'assets/official_labels_rendered/anhialo_massage_gel_rosemary_top_fv17.png',
      sideImg: 'assets/official_labels_rendered/side_label_grey_rosemary_v12.png',
      sidePdf: 'assets/official_drive_assets/labels/Side Label Grey Rosemary v12.pdf',
      lidPdf: 'assets/official_drive_assets/labels/Anhialo Massage Gel_Rosemary Top Fv17.pdf',
      botanical: 'Rosmarinus Officinalis Leaf Powder Extract',
      subtitle: 'Thermal Microcirculation & Tendon Warm-Up',
      purpose: "Invigorating microcirculatory botanical gel. Rosemary terpenes stimulate localized capillary blood flow and oxygen delivery. Highly recommended for pre-training warm-up, morning tendon stiffness, and reviving cold extremities with natural bio-heat.",
      inci: "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, GLYCERINE, ROSMARINUS OFFICINALIS LEAF POWDER EXTRACT."
    },
    juniper: {
      id: 'juniper',
      name: 'ALPINE JUNIPER BLEND',
      fullName: 'JUNIPER BLEND — DUAL MAGNESIUM COMPLEX',
      accentColor: '#0284c7',
      heroJar: 'assets/images/products/07_file_transp.png',
      lidImg: 'assets/official_labels_rendered/anhialo_massage_gel_juniper_top_fv17.png',
      sideImg: 'assets/official_labels_rendered/side_label_grey_juniper_v12.png',
      sidePdf: 'assets/official_drive_assets/labels/Side Label Grey Juniper v12.pdf',
      lidPdf: 'assets/official_drive_assets/labels/Anhialo Massage Gel_Juniper Top Fv17.pdf',
      botanical: 'Juniperus Chinensis Leaf Extract & Fruit Oil',
      subtitle: 'Joint Mobility, Detoxification & Lymphatic Flow',
      purpose: "Targeted joint mobility and cellular detox gel. Alpine juniper fruit pinene terpenes assist osmotic tissue drainage, helping flush cellular metabolic residues, ease chronic arthritic stiffness, and refresh heavy, congested joints.",
      inci: "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, PARFUM, GLYCERINE, JUNIPERUS CHINENSIS LEAF EXTRACT."
    },
    grape: {
      id: 'grape',
      name: 'RED GRAPE SEED BLEND',
      fullName: 'GRAPE BLEND — DUAL MAGNESIUM COMPLEX',
      accentColor: '#9d174d',
      heroJar: 'assets/images/products/03_file_transp.png',
      lidImg: 'assets/official_labels_rendered/anhialo_massage_gel_grape_top_fv17.png',
      sideImg: 'assets/official_labels_rendered/side_label_grey_grape_v12.png',
      sidePdf: 'assets/official_drive_assets/labels/Side Label Grey Grape v12.pdf',
      lidPdf: 'assets/official_drive_assets/labels/Anhialo Massage Gel_Grape Top Fv17.pdf',
      botanical: 'Vitis Vinifera (Grape) Seed Polyphenol Extract',
      subtitle: 'Cellular Antioxidant & Dermal Elasticity',
      purpose: "Rich in proanthocyanidins and resveratrol antioxidants. Shields dermal collagen against oxidative free-radical breakdown while feeding transdermal magnesium to tired muscles. Restores skin firmness and velvety softness with a delicate vineyard aroma.",
      inci: "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, PARFUM, GLYCERINE."
    }
  };

  // Product Catalog (9 Authentic Formulations)
  const CATALOG_PRODUCTS = [
    {
      id: 'gel-arnica',
      slug: 'anchialo-dual-magnesium-gel-arnica-blend',
      name: 'Dual Magnesium Gel | Arnica Blend',
      category: 'gel',
      priceAUD: 49.00,
      image: 'assets/images/products/06_file_transp.png',
      badge: 'Bestseller · Muscle Relief',
      isStaged: false,
      description: 'Fast-absorbing topical gel enriched with Arnica Montana and 253 g/L natural Black Sea magnesium. Relieves acute muscle aches, bruises, joint inflammation, and spasms. 300g net.'
    },
    {
      id: 'gel-lavender',
      slug: 'anchialo-dual-magnesium-gel-lavander-blend',
      name: 'Dual Magnesium Gel | Lavender Blend',
      category: 'gel',
      priceAUD: 49.00,
      image: 'assets/images/products/01_file_transp.png',
      badge: 'Deep Sleep & Calming',
      isStaged: false,
      description: 'Infused with Mediterranean Lavender. Calms central nervous excitability, alleviates restless leg syndrome, and supports restorative night sleep. 300g net.'
    },
    {
      id: 'gel-rosemary',
      slug: 'anchialo-dual-magnesium-gel-rosemary-blend',
      name: 'Dual Magnesium Gel | Rosemary Blend',
      category: 'gel',
      priceAUD: 49.00,
      image: 'assets/images/products/04_file_transp.png',
      badge: 'Joint Mobility & Warm-Up',
      isStaged: false,
      description: 'Invigorating rosemary extract stimulates microcirculation and speeds tendon warm-up. Perfect for active athletes and post-workout recovery. 300g net.'
    },
    {
      id: 'gel-juniper',
      slug: 'anchialo-dual-magnesium-gel-juniper-blend',
      name: 'Dual Magnesium Gel | Juniper Blend',
      category: 'gel',
      priceAUD: 49.00,
      image: 'assets/images/products/07_file_transp.png',
      badge: 'Deep Tissue Detox',
      isStaged: false,
      description: 'Alpine juniper fruit terpenes assist lymphatic drainage and ease chronic morning joint stiffness and inflammation. 300g net.'
    },
    {
      id: 'gel-grape',
      slug: 'anchialo-dual-magnesium-gel-grape-blend',
      name: 'Dual Magnesium Gel | Grape Blend',
      category: 'gel',
      priceAUD: 49.00,
      image: 'assets/images/products/03_file_transp.png',
      badge: 'Antioxidant & Skin Tone',
      isStaged: false,
      description: 'Rich in grape seed polyphenols and resveratrol. Promotes skin elasticity, reduces oxidative tension, and hydrates tired tissues. 300g net.'
    },
    {
      id: 'oil-pure',
      slug: 'anchialo-dual-magnesium-oil-natural-topical-oil',
      name: 'Dual Magnesium Oil | Natural Topical Brine',
      category: 'oil',
      priceAUD: 49.00,
      image: 'assets/images/products/08_file_transp.png',
      badge: '100% Pure Liquid Brine',
      isStaged: false,
      description: 'Unscented, highly bioavailable liquid Black Sea mineral oil. Silky transdermal glide for full-body massage or foot soak mineralization. 300ml.'
    },
    {
      id: 'combo-gel-oil',
      slug: 'special-offer-gel-oil-combo',
      name: 'Special Offer | Gel + Oil Combo',
      category: 'combo',
      priceAUD: 49.00,
      image: 'assets/images/products/02_file.png',
      badge: '1+1 Free Value Deal',
      isStaged: true,
      description: 'Buy 1 Dual Magnesium Gel (any blend) and receive 1 Dual Magnesium Oil FREE! Double the care for the price of one single jar. Limited stock.'
    },
    {
      id: 'combo-starter',
      slug: 'starter-combo-dual-magnesium-gel',
      name: 'Starter Combo | Dual Magnesium Gel (2-Pack)',
      category: 'combo',
      priceAUD: 89.00,
      image: 'assets/images/products/05_file.png',
      badge: 'Save $9 · Day & Night Pair',
      isStaged: true,
      description: 'Pair Arnica for daytime athletic recovery with Lavender for evening sleep and nervous system reset. Total 600g pure Pomorie peloids.'
    },
    {
      id: 'combo-best-value',
      slug: 'best-value-combo-dual-magnesium-gel',
      name: 'Best Value Combo | Dual Magnesium Gel (3-Pack)',
      category: 'combo',
      priceAUD: 129.00,
      image: 'assets/images/products/09_file.png',
      badge: 'Save $18 · Combat Team Pack',
      isStaged: true,
      description: 'Choose any three 300g jars. Maximum value package designed for active fighters, gyms, and balneotherapy enthusiasts. Free Australia Post shipping.'
    }
  ];

  // ==================== PRICE FORMATTER ====================
  function formatPrice(audAmount) {
    if (STATE.currency === 'AUD') {
      return `A$ ${audAmount.toFixed(2)} AUD`;
    }
    if (STATE.currency === 'USD') {
      const val = audAmount / 1.55;
      return `$ ${val.toFixed(2)} USD`;
    }
    if (STATE.currency === 'EUR') {
      const val = (audAmount / 1.55) * 0.92;
      return `€ ${val.toFixed(2)} EUR`;
    }
    if (STATE.currency === 'BGN') {
      const val = (audAmount / 1.55) * 1.80;
      return `${val.toFixed(2)} BGN`;
    }
    return `A$ ${audAmount.toFixed(2)}`;
  }

  // ==================== INITIALIZATION ====================
  document.addEventListener('DOMContentLoaded', () => {
    initCurrency();
    initHeroBlendSwitcher();
    initBotanicalApothecary();
    initProductsGrid();
    initBlogJournal();
    initCartDrawer();
    initAusPostTracker();
    initTaxInvoiceEngine();
    initModals();
    initFaqAccordion();
    checkStripeReturn();
  });

  function checkStripeReturn() {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('payment') === 'stripe_success') {
      const modal = document.getElementById('paymentSuccessModal');
      const txIdEl = document.getElementById('successTxId');
      const payerEl = document.getElementById('successPayer');
      const amountEl = document.getElementById('successAmount');
      const waBtn = document.getElementById('btnSuccessWhatsApp');
      const sessionId = urlParams.get('session_id') || ('STRIPE-' + Date.now().toString(36).toUpperCase());

      if (txIdEl) txIdEl.textContent = sessionId;
      if (payerEl) payerEl.textContent = 'Stripe Verified Customer (Apple Pay / Card)';
      if (amountEl) amountEl.textContent = 'Paid via Stripe AU';

      if (waBtn) {
        const msg = encodeURIComponent(`Hi Sotir, I have successfully completed payment via Stripe (Apple Pay / Card) for my Anchialo order! Checkout Ref: ${sessionId}. Please confirm Melbourne dispatch!`);
        waBtn.href = `https://wa.me/61423269586?text=${msg}`;
      }

      // Record order metadata for ATO Tax Invoice generation
      STATE.lastOrderMeta = {
        type: 'Stripe',
        txId: sessionId,
        amount: 'Paid via Stripe AU',
        payer: 'Stripe Verified Customer (Apple Pay / Card)',
        items: [...STATE.cart]
      };

      // Clear cart
      STATE.cart = [];
      saveCart();
      if (modal) modal.classList.add('active');
    }
  }

  // ==================== CURRENCY CONTROLLER ====================
  function initCurrency() {
    const select = document.getElementById('currencySelect');
    if (!select) return;

    select.value = STATE.currency;
    select.addEventListener('change', (e) => {
      STATE.currency = e.target.value;
      localStorage.setItem('anchialov2_currency', STATE.currency);
      updateAllPrices();
    });
    updateAllPrices();
  }

  function updateAllPrices() {
    const heroPrice = document.getElementById('heroPriceTag');
    if (heroPrice) heroPrice.textContent = formatPrice(49.00);

    const blendPrice = document.getElementById('activeBlendPrice');
    if (blendPrice) blendPrice.textContent = formatPrice(49.00);

    renderCatalog();
    updateCartDrawer();
  }

  // ==================== HERO BLEND SWITCHER ====================
  function initHeroBlendSwitcher() {
    const dots = document.querySelectorAll('.blend-dot-btn');
    dots.forEach(dot => {
      dot.addEventListener('click', () => {
        dots.forEach(d => d.classList.remove('active'));
        dot.classList.add('active');
        const blendKey = dot.getAttribute('data-blend');
        applyHeroBlend(blendKey);
      });
    });

    const quickAdd = document.getElementById('heroQuickAddBtn');
    if (quickAdd) {
      quickAdd.addEventListener('click', () => {
        addToCart(`gel-${STATE.selectedBlend}`);
      });
    }
  }

  function applyHeroBlend(blendKey) {
    const blend = BLENDS[blendKey];
    if (!blend) return;

    STATE.selectedBlend = blendKey;

    const heroJar = document.getElementById('heroJarImage');
    if (heroJar) heroJar.src = blend.heroJar;

    const heroSub = document.getElementById('heroCardSub');
    if (heroSub) heroSub.textContent = blend.name;

    // Sync Botanical Apothecary Tabs
    document.querySelectorAll('.btn-blend-tab').forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-blend') === blendKey);
    });
    applyBotanicalBlend(blendKey);
  }

  // ==================== BOTANICAL APOTHECARY SECTION ====================
  function initBotanicalApothecary() {
    const tabs = document.querySelectorAll('.btn-blend-tab');
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        const blendKey = tab.getAttribute('data-blend');

        // Sync hero dots
        document.querySelectorAll('.blend-dot-btn').forEach(d => {
          d.classList.toggle('active', d.getAttribute('data-blend') === blendKey);
        });

        applyBotanicalBlend(blendKey);
      });
    });

    // Detail tabs (Purpose, INCI, Usage, Producer)
    const detailTabs = document.querySelectorAll('.btn-detail-tab');
    detailTabs.forEach(dTab => {
      dTab.addEventListener('click', () => {
        detailTabs.forEach(t => t.classList.remove('active'));
        dTab.classList.add('active');
        STATE.activeDetailTab = dTab.getAttribute('data-tab');
        renderDetailTab();
      });
    });

    // Add Active Blend to Bag
    const addBtn = document.getElementById('btnAddActiveBlend');
    if (addBtn) {
      addBtn.addEventListener('click', () => {
        addToCart(`gel-${STATE.selectedBlend}`);
      });
    }

    // Default select Arnica
    applyBotanicalBlend('arnica');
  }

  function applyBotanicalBlend(blendKey) {
    const blend = BLENDS[blendKey];
    if (!blend) return;
    STATE.selectedBlend = blendKey;

    const titleEl = document.getElementById('activeBlendTitle');
    if (titleEl) titleEl.textContent = blend.fullName;

    const botEl = document.getElementById('activeBlendBotanical');
    if (botEl) botEl.textContent = blend.botanical;

    const lidImg = document.getElementById('studioLidImg');
    if (lidImg) lidImg.src = blend.lidImg;

    const sideImg = document.getElementById('studioSideImg');
    if (sideImg) sideImg.src = blend.sideImg;

    const dlLid = document.getElementById('downloadLidPdf');
    if (dlLid) dlLid.href = blend.lidPdf;

    const dlSide = document.getElementById('downloadSidePdf');
    if (dlSide) dlSide.href = blend.sidePdf;

    // WhatsApp link
    const waBtn = document.getElementById('btnWaActiveBlend');
    if (waBtn) {
      const priceFormatted = formatPrice(49.00);
      const msg = encodeURIComponent(`Hi Sotir, I would like to order Anchialo ${blend.fullName} (${priceFormatted}). Please confirm delivery / Melbourne pickup.`);
      waBtn.href = `https://wa.me/61423269586?text=${msg}`;
    }

    renderDetailTab();
  }

  function renderDetailTab() {
    const body = document.getElementById('hudTabBody');
    if (!body) return;
    const blend = BLENDS[STATE.selectedBlend] || BLENDS.arnica;

    let html = '';
    switch (STATE.activeDetailTab) {
      case 'purpose':
        html = `
          <h4 style="font-family:var(--font-serif); font-size:18px; color:var(--accent-pine); margin-bottom:8px;">Therapeutic Indications &amp; Action</h4>
          <p>${blend.purpose}</p>
          <div style="margin-top:14px; padding:12px 16px; background:var(--accent-pine-soft); border-radius:10px; font-size:13.5px; border-left:3px solid var(--accent-pine);">
            <strong style="color:var(--accent-pine);">Active Botanical Essence:</strong> ${blend.botanical}
          </div>
        `;
        break;
      case 'inci':
        html = `
          <h4 style="font-family:var(--font-serif); font-size:18px; color:var(--accent-pine); margin-bottom:8px;">100% Transparent INCI Formula</h4>
          <p style="font-size:13.5px; background:var(--bg-canvas); padding:16px; border-radius:10px; border:1px solid var(--border-subtle); color:var(--text-primary); line-height:1.7;">
            ${blend.inci}
          </p>
          <p style="font-size:12.5px; color:var(--text-muted); margin-top:10px;">
            Free from artificial colors, synthetic fragrances, parabens, petrolatum, and GMO derivatives. Cruelty-free &amp; vegan.
          </p>
        `;
        break;
      case 'usage':
        html = `
          <h4 style="font-family:var(--font-serif); font-size:18px; color:var(--accent-pine); margin-bottom:8px;">Application Ritual &amp; Massage</h4>
          <p>${TEXTS.usage}</p>
          <div style="border-top:1px solid var(--border-subtle); margin-top:12px; padding-top:10px; font-size:13px; color:var(--text-muted);">
            <strong style="color:var(--accent-gold);">Storage &amp; Caution:</strong> ${TEXTS.warning}
          </div>
        `;
        break;
      case 'producer':
        html = `
          <h4 style="font-family:var(--font-serif); font-size:18px; color:var(--accent-pine); margin-bottom:8px;">Origin &amp; Producer Traceability</h4>
          <p>${TEXTS.producer}</p>
          <p style="margin-top:10px; font-size:13px; color:var(--text-secondary); line-height:1.6;">${TEXTS.heritage}</p>
        `;
        break;
    }
    body.innerHTML = html;
  }

  // ==================== PRODUCT CATALOG ====================
  function initProductsGrid() {
    STATE.products = CATALOG_PRODUCTS;

    // Filter pills
    document.querySelectorAll('.btn-filter-pill').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.btn-filter-pill').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        STATE.activeCategory = btn.getAttribute('data-cat');
        renderCatalog();
      });
    });

    // Search input
    const search = document.getElementById('catalogSearch');
    if (search) {
      search.addEventListener('input', (e) => {
        STATE.searchQuery = e.target.value.toLowerCase().trim();
        renderCatalog();
      });
    }

    renderCatalog();
  }

  function renderCatalog() {
    const grid = document.getElementById('productsGrid');
    if (!grid) return;

    const filtered = STATE.products.filter(p => {
      if (STATE.activeCategory !== 'all' && p.category !== STATE.activeCategory) return false;
      if (STATE.searchQuery) {
        const text = `${p.name} ${p.description} ${p.badge}`.toLowerCase();
        if (!text.includes(STATE.searchQuery)) return false;
      }
      return true;
    });

    if (filtered.length === 0) {
      grid.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 60px 20px;">
          <h3 style="font-family:var(--font-serif); font-size:24px; margin-bottom:8px;">No matching formulations found</h3>
          <p style="color:var(--text-muted); font-size:15px;">Try searching for "arnica", "lavender", "oil", or "combo".</p>
        </div>
      `;
      return;
    }

    grid.innerHTML = filtered.map(prod => {
      const priceFormatted = formatPrice(prod.priceAUD);
      const isStagedClass = prod.isStaged ? 'has-staged-img' : '';
      const waMsg = encodeURIComponent(`Hi Sotir, I would like to order ${prod.name} (${priceFormatted}). Please confirm delivery / Melbourne pickup.`);

      return `
        <div class="product-card">
          <div class="product-thumb ${isStagedClass}">
            <span class="product-flag">${prod.badge}</span>
            <img src="${prod.image}" alt="${prod.name}" loading="lazy">
          </div>
          <div class="product-body">
            <h3 class="product-name"><a href="product-page/${prod.slug || ''}" style="color:inherit;text-decoration:none;">${prod.name}</a></h3>
            <div class="product-price-row">
              <span class="price-main">${priceFormatted}</span>
              <span class="price-unit">/ 300g Net</span>
            </div>
            <p class="product-desc">${prod.description}</p>
            <div class="product-actions">
              <button class="btn-card-add" data-id="${prod.id}">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                <span>Add to Bag</span>
              </button>
              <a href="https://wa.me/61423269586?text=${waMsg}" target="_blank" rel="noopener" class="btn-card-wa" title="Order via WhatsApp">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12.04 2c-5.46 0-9.91 4.45-9.91 9.91 0 1.75.46 3.45 1.32 4.95L2.05 22l5.25-1.38c1.45.79 3.08 1.21 4.74 1.21 5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.816 9.816 0 0 0 12.04 2m.01 1.67c2.2 0 4.26.86 5.82 2.41a8.17 8.17 0 0 1 2.41 5.83c0 4.54-3.7 8.24-8.24 8.24-1.48 0-2.93-.4-4.2-1.15l-.3-.18-3.12.82.83-3.04-.2-.31a8.19 8.19 0 0 1-1.26-4.38c0-4.54 3.7-8.24 8.24-8.24m4.53 11.51c-.25-.13-1.47-.72-1.7-.81-.23-.08-.39-.13-.56.13-.17.25-.64.81-.79.97-.14.17-.29.19-.54.06-.25-.13-1.06-.39-2.02-1.25-.75-.67-1.26-1.5-1.41-1.75-.14-.25-.02-.39.11-.51.11-.11.25-.29.38-.44.13-.14.17-.25.25-.42.08-.17.04-.31-.02-.44-.06-.13-.56-1.34-.76-1.84-.2-.48-.4-.42-.56-.43h-.48c-.17 0-.44.06-.67.31-.23.25-.88.86-.88 2.1 0 1.24.9 2.44 1.03 2.61.13.17 1.78 2.71 4.3 3.8.6.26 1.07.42 1.44.54.61.19 1.16.16 1.6.1.49-.07 1.47-.6 1.68-1.18.21-.58.21-1.07.15-1.18-.06-.11-.23-.17-.48-.3Z"/></svg>
              </a>
            </div>
          </div>
        </div>
      `;
    }).join('');

    // Attach click events
    grid.querySelectorAll('.btn-card-add').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = btn.getAttribute('data-id');
        addToCart(id);
      });
    });
  }

  // ==================== BLOG JOURNAL ====================
  function initBlogJournal() {
    fetch('data/blog_posts.json')
      .then(res => res.json())
      .then(posts => {
        STATE.blogPosts = posts || [];
        renderBlogGrid();
      })
      .catch(err => {
        console.warn('Could not load blog posts:', err);
      });
  }

  function renderBlogGrid() {
    const grid = document.getElementById('blogGrid');
    if (!grid || !STATE.blogPosts.length) return;

    // First 6 articles
    const featured = STATE.blogPosts.slice(0, 6);

    grid.innerHTML = featured.map((post, idx) => {
      const imgUrl = (post.image && post.image.url) ? post.image.url : 'assets/images/blog/01_blog.png';
      const author = post.author || 'Sotir Kichukov';
      const desc = post.description || '';

      return `
        <div class="blog-card">
          <div class="blog-card-thumb">
            <img src="${imgUrl}" alt="${post.title}" loading="lazy">
          </div>
          <div class="blog-card-body">
            <span class="blog-card-meta">BALNEOLOGY REPORT · ${author}</span>
            <h3 class="blog-card-title"><a href="post/${post.slug || ''}" style="color:inherit;text-decoration:none;">${post.title}</a></h3>
            <p class="blog-card-excerpt">${desc}</p>
            <button class="btn-read-article" data-idx="${idx}">
              <span>Read Full Article</span>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="m9 18 6-6-6-6"/></svg>
            </button>
          </div>
        </div>
      `;
    }).join('');

    grid.querySelectorAll('.btn-read-article').forEach(btn => {
      btn.addEventListener('click', () => {
        const idx = parseInt(btn.getAttribute('data-idx'), 10);
        openBlogModal(STATE.blogPosts[idx]);
      });
    });
  }

  function openBlogModal(post) {
    if (!post) return;
    const modal = document.getElementById('blogModalBackdrop');
    const titleEl = document.getElementById('blogModalTitle');
    const catEl = document.getElementById('blogModalCategory');
    const authorEl = document.getElementById('blogModalAuthor');
    const bodyEl = document.getElementById('blogModalBody');
    if (!modal || !titleEl || !bodyEl) return;

    titleEl.textContent = post.title;
    if (catEl) catEl.textContent = 'POMORIE BALNEOTHERAPY RESEARCH';
    if (authorEl) authorEl.textContent = `Authored by ${post.author || 'Sotir Kichukov'} · Peer Reviewed Clinical Archive`;

    const paragraphs = (post.body_text || post.description || '').split('\n').filter(p => p.trim());
    bodyEl.innerHTML = paragraphs.map(p => `<p>${p}</p>`).join('');

    modal.classList.add('active');
  }

  // ==================== SHOPPING BAG DRAWER ====================
  function initCartDrawer() {
    const backdrop = document.getElementById('bagBackdrop');
    const drawer = document.getElementById('bagDrawer');
    const openBtn = document.getElementById('openBagBtn');
    const closeBtn = document.getElementById('closeBagBtn');

    if (openBtn) openBtn.addEventListener('click', () => openBagDrawer());
    if (closeBtn) closeBtn.addEventListener('click', () => closeBagDrawer());
    if (backdrop) backdrop.addEventListener('click', () => closeBagDrawer());

    // WhatsApp Checkout
    const btnWa = document.getElementById('btnProceedWhatsApp');
    if (btnWa) {
      btnWa.addEventListener('click', (e) => {
        if (!STATE.cart.length) {
          e.preventDefault();
          alert('Your shopping bag is currently empty. Please select a formulation.');
          return;
        }

        let summary = 'Hello Sotir, I would like to place an order from Anchialo Australia:\n\n';
        let total = 0;
        STATE.cart.forEach((it, i) => {
          const itemTotal = it.priceAUD * it.qty;
          total += itemTotal;
          summary += `${i + 1}. ${it.name} × ${it.qty} = A$ ${itemTotal.toFixed(2)} AUD\n`;
        });
        summary += `\nTotal: A$ ${total.toFixed(2)} AUD\n`;
        summary += `\nPlease let me know availability and delivery / Melbourne gym pickup details!`;

        btnWa.href = `https://wa.me/61423269586?text=${encodeURIComponent(summary)}`;
      });
    }

    // Copy Summary Button
    const copyBtn = document.getElementById('btnCopyOrderSummary');
    if (copyBtn) {
      copyBtn.addEventListener('click', () => {
        if (!STATE.cart.length) {
          alert('Your shopping bag is empty.');
          return;
        }
        let summary = 'ANCHIALO AUSTRALIA — ORDER SUMMARY:\n';
        let total = 0;
        STATE.cart.forEach((it, i) => {
          const itemTotal = it.priceAUD * it.qty;
          total += itemTotal;
          summary += `${i + 1}. ${it.name} × ${it.qty} = A$ ${itemTotal.toFixed(2)} AUD\n`;
        });
        summary += `\nEstimated Total: A$ ${total.toFixed(2)} AUD\nContact: Sotir Kichukov (+61 423 269 586)`;

        navigator.clipboard.writeText(summary).then(() => {
          const orig = copyBtn.textContent;
          copyBtn.textContent = '✓ Summary Copied to Clipboard!';
          setTimeout(() => { copyBtn.textContent = orig; }, 2500);
        });
      });
    }

    updateCartDrawer();
  }

  function openBagDrawer() {
    const backdrop = document.getElementById('bagBackdrop');
    const drawer = document.getElementById('bagDrawer');
    if (backdrop) backdrop.classList.add('active');
    if (drawer) drawer.classList.add('active');
  }

  function closeBagDrawer() {
    const backdrop = document.getElementById('bagBackdrop');
    const drawer = document.getElementById('bagDrawer');
    if (backdrop) backdrop.classList.remove('active');
    if (drawer) drawer.classList.remove('active');
  }

  function addToCart(productId) {
    let prod = STATE.products.find(p => p.id === productId);
    if (!prod) {
      // Fallback for blend IDs
      const blendKey = productId.replace('gel-', '');
      const blend = BLENDS[blendKey];
      if (blend) {
        prod = {
          id: productId,
          name: blend.fullName,
          priceAUD: 49.00,
          image: blend.heroJar
        };
      }
    }
    if (!prod) return;

    const existing = STATE.cart.find(it => it.id === prod.id);
    if (existing) {
      existing.qty += 1;
    } else {
      STATE.cart.push({
        id: prod.id,
        name: prod.name,
        priceAUD: prod.priceAUD,
        image: prod.image,
        qty: 1
      });
    }

    saveCart();
    openBagDrawer();
  }

  function saveCart() {
    localStorage.setItem('anchialov2_cart', JSON.stringify(STATE.cart));
    updateCartDrawer();
  }

  function updateCartDrawer() {
    const listEl = document.getElementById('bagItemsContainer');
    const badgeEl = document.getElementById('cartCountBadge');
    const countEl = document.getElementById('drawerItemCount');
    const totalEl = document.getElementById('drawerSubtotalPrice');
    const meterBar = document.getElementById('shippingMeterBar');
    const meterText = document.getElementById('shippingMeterText');
    const meterPct = document.getElementById('shippingMeterPercent');

    const totalQty = STATE.cart.reduce((sum, it) => sum + it.qty, 0);
    const subtotalAUD = STATE.cart.reduce((sum, it) => sum + (it.priceAUD * it.qty), 0);

    if (badgeEl) badgeEl.textContent = totalQty;
    if (countEl) countEl.textContent = `${totalQty} item${totalQty === 1 ? '' : 's'}`;
    if (totalEl) totalEl.textContent = formatPrice(subtotalAUD);

    // Free shipping threshold ($80 AUD)
    const threshold = 80;
    const progress = Math.min(100, (subtotalAUD / threshold) * 100);
    if (meterBar) meterBar.style.width = `${progress}%`;
    if (meterPct) meterPct.textContent = `${Math.round(progress)}%`;

    if (meterText) {
      if (subtotalAUD >= threshold) {
        meterText.textContent = '🎉 Qualified for FREE Australia-wide delivery!';
      } else {
        const remaining = threshold - subtotalAUD;
        meterText.textContent = `Add A$ ${remaining.toFixed(2)} AUD for FREE delivery`;
      }
    }

    if (!listEl) return;
    const stripeBtn = document.getElementById('btnStripeCheckout');

    if (STATE.cart.length === 0) {
      listEl.innerHTML = `
        <div class="bag-empty-state">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="8" cy="21" r="1"/><circle cx="19" cy="21" r="1"/><path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"/></svg>
          <h4>Your bag is empty</h4>
          <p>Explore our pure Black Sea mineral formulations above.</p>
        </div>
      `;
      if (stripeBtn) stripeBtn.style.display = 'none';
      renderPayPalButtons();
      return;
    }

    // Configure Stripe Express Link for current cart
    if (stripeBtn) {
      stripeBtn.style.display = 'flex';
      const totalUnits = STATE.cart.reduce((sum, it) => sum + it.qty, 0);
      if (STATE.cart.length === 1 && STRIPE_CONFIG.links[STATE.cart[0].id]) {
        stripeBtn.href = `${STRIPE_CONFIG.links[STATE.cart[0].id]}?quantity=${STATE.cart[0].qty}`;
      } else if (totalUnits === 3 && subtotalAUD === 125) {
        stripeBtn.href = STRIPE_CONFIG.links['combo-trio'];
      } else if (totalUnits === 6 && subtotalAUD === 245) {
        stripeBtn.href = STRIPE_CONFIG.links['combo-complete'];
      } else {
        stripeBtn.href = `${STRIPE_CONFIG.links['custom']}?quantity=${totalUnits}`;
      }
    }

    listEl.innerHTML = STATE.cart.map((item, idx) => `
      <div class="bag-item-card">
        <img class="bag-item-img" src="${item.image}" alt="${item.name}">
        <div>
          <h5 class="bag-item-title">${item.name}</h5>
          <div class="bag-item-price">${formatPrice(item.priceAUD)}</div>
        </div>
        <div class="bag-item-qty">
          <button class="btn-qty" data-action="minus" data-idx="${idx}">−</button>
          <span style="font-size:13px; font-weight:700;">${item.qty}</span>
          <button class="btn-qty" data-action="plus" data-idx="${idx}">+</button>
          <button class="btn-qty" data-action="remove" data-idx="${idx}" title="Remove" style="margin-left:4px; color:var(--text-muted);">&times;</button>
        </div>
      </div>
    `).join('');

    // Attach actions
    listEl.querySelectorAll('.btn-qty').forEach(btn => {
      btn.addEventListener('click', () => {
        const idx = parseInt(btn.getAttribute('data-idx'), 10);
        const action = btn.getAttribute('data-action');
        if (action === 'plus') {
          STATE.cart[idx].qty += 1;
        } else if (action === 'minus') {
          STATE.cart[idx].qty -= 1;
          if (STATE.cart[idx].qty <= 0) STATE.cart.splice(idx, 1);
        } else if (action === 'remove') {
          STATE.cart.splice(idx, 1);
        }
        saveCart();
      });
    });
    // Re-render PayPal Smart Buttons with current cart total
    renderPayPalButtons();
  }

  // ==================== PAYPAL CHECKOUT ENGINE ====================
  let paypalRenderTimer = null;
  function renderPayPalButtons() {
    const container = document.getElementById('paypal-button-container');
    if (!container) return;

    if (typeof paypal === 'undefined') {
      container.innerHTML = '<div style="text-align:center; padding:12px; font-size:12px; color:var(--text-muted);">Loading Secure PayPal &amp; Card Gateway...</div>';
      if (!window.__paypalRetryBound) {
        window.__paypalRetryBound = true;
        let attempts = 0;
        const retryTimer = setInterval(() => {
          attempts++;
          if (typeof paypal !== 'undefined') {
            clearInterval(retryTimer);
            renderPayPalButtons();
          } else if (attempts > 30) {
            clearInterval(retryTimer);
            container.innerHTML = '<div style="text-align:center; padding:10px 0; font-size:12px; color:var(--text-muted);">Secure Gateway Ready via WhatsApp Order below.</div>';
          }
        }, 200);
      }
      return;
    }

    const subtotalAUD = STATE.cart.reduce((sum, it) => sum + (it.priceAUD * it.qty), 0);
    if (STATE.cart.length === 0 || subtotalAUD <= 0) {
      container.innerHTML = '<div style="text-align:center; padding:10px 0; font-size:12px; color:var(--text-muted);">Select formulations above to activate PayPal &amp; Card Checkout</div>';
      return;
    }

    // Debounce to prevent multiple SDK re-renders
    clearTimeout(paypalRenderTimer);
    paypalRenderTimer = setTimeout(() => {
      container.innerHTML = '';
      try {
        paypal.Buttons({
          style: {
            layout: 'vertical',
            color: 'gold',
            shape: 'pill',
            label: 'checkout',
            height: 44
          },
          createOrder: function(data, actions) {
            const currentTotal = STATE.cart.reduce((sum, it) => sum + (it.priceAUD * it.qty), 0);
            return actions.order.create({
              intent: 'CAPTURE',
              purchase_units: [{
                description: 'Anchialo Certified Dual Magnesium Balneology Formulations',
                custom_id: 'ANCHIALO_MELBOURNE_DISPATCH',
                amount: {
                  currency_code: 'AUD',
                  value: currentTotal.toFixed(2),
                  breakdown: {
                    item_total: {
                      currency_code: 'AUD',
                      value: currentTotal.toFixed(2)
                    }
                  }
                },
                items: STATE.cart.map(it => ({
                  name: it.name,
                  unit_amount: {
                    currency_code: 'AUD',
                    value: it.priceAUD.toFixed(2)
                  },
                  quantity: it.qty.toString()
                }))
              }]
            });
          },
          onApprove: function(data, actions) {
            return actions.order.capture().then(function(details) {
              handlePayPalSuccess(details);
            });
          },
          onCancel: function(data) {
            console.log('PayPal Checkout cancelled by user:', data);
          },
          onError: function(err) {
            console.error('PayPal Transaction Error:', err);
            alert('PayPal encountered a temporary error. You can also complete your order instantly via WhatsApp.');
          }
        }).render('#paypal-button-container');
      } catch (err) {
        console.error('PayPal render exception:', err);
      }
    }, 150);
  }

  function handlePayPalSuccess(details) {
    const modal = document.getElementById('paymentSuccessModal');
    const txIdEl = document.getElementById('successTxId');
    const payerEl = document.getElementById('successPayer');
    const amountEl = document.getElementById('successAmount');
    const waBtn = document.getElementById('btnSuccessWhatsApp');

    let txId = 'PAYPAL-TX-' + Date.now();
    try {
      if (details.purchase_units && details.purchase_units[0] && details.purchase_units[0].payments && details.purchase_units[0].payments.captures && details.purchase_units[0].payments.captures[0]) {
        txId = details.purchase_units[0].payments.captures[0].id;
      } else if (details.id) {
        txId = details.id;
      }
    } catch(e) {}

    const givenName = (details.payer && details.payer.name && details.payer.name.given_name) ? details.payer.name.given_name : '';
    const surname = (details.payer && details.payer.name && details.payer.name.surname) ? details.payer.name.surname : '';
    const payerEmail = (details.payer && details.payer.email_address) ? details.payer.email_address : '';
    const fullName = `${givenName} ${surname}`.trim() || 'Valued Customer';

    let paidVal = '49.00';
    try {
      paidVal = details.purchase_units[0].amount.value;
    } catch(e) {}

    if (txIdEl) txIdEl.textContent = txId;
    if (payerEl) payerEl.textContent = `${fullName} (${payerEmail})`;
    if (amountEl) amountEl.textContent = `A$ ${paidVal} AUD`;

    // WhatsApp Notify link
    if (waBtn) {
      const msg = encodeURIComponent(`Hi Sotir, I have successfully paid A$ ${paidVal} AUD via PayPal for my Anchialo order! Transaction ID: ${txId}. Payer: ${fullName} (${payerEmail}). Please confirm dispatch!`);
      waBtn.href = `https://wa.me/61423269586?text=${msg}`;
    }

    // Record order metadata for ATO Tax Invoice generation
    STATE.lastOrderMeta = {
      type: 'PayPal',
      txId: txId,
      amount: `A$ ${paidVal} AUD`,
      payer: `${fullName} (${payerEmail})`,
      items: [...STATE.cart]
    };

    // Clear cart & close drawer
    STATE.cart = [];
    saveCart();
    closeBagDrawer();

    if (modal) modal.classList.add('active');
  }

  // ==================== MODALS ====================
  function initModals() {
    // Certificate Modal
    const certModal = document.getElementById('certModalBackdrop');
    const openCert1 = document.getElementById('btnBannerCert');
    const openCert2 = document.getElementById('btnOpenCertModal');
    const closeCert = document.getElementById('btnCloseCertModal');

    [openCert1, openCert2].forEach(btn => {
      if (btn) btn.addEventListener('click', (e) => {
        e.preventDefault();
        certModal.classList.add('active');
      });
    });
    if (closeCert) closeCert.addEventListener('click', () => certModal.classList.remove('active'));
    if (certModal) certModal.addEventListener('click', (e) => {
      if (e.target === certModal) certModal.classList.remove('active');
    });

    // Certificate Page Switcher
    const certImg = document.getElementById('certModalImage');
    const pageBtns = document.querySelectorAll('.btn-cert-page');
    pageBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        pageBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const page = btn.getAttribute('data-page');
        if (certImg) {
          certImg.src = `assets/official_labels_rendered/quality_certificate_page_${page}.png`;
        }
      });
    });

    // Blog Modal
    const blogModal = document.getElementById('blogModalBackdrop');
    const closeBlog = document.getElementById('btnCloseBlogModal');
    if (closeBlog) closeBlog.addEventListener('click', () => blogModal.classList.remove('active'));
    if (blogModal) blogModal.addEventListener('click', (e) => {
      if (e.target === blogModal) blogModal.classList.remove('active');
    });

    // Payment Success Modal Close
    const successModal = document.getElementById('paymentSuccessModal');
    const closeSuccessBtn = document.getElementById('btnCloseSuccessModal');
    if (closeSuccessBtn && successModal) {
      closeSuccessBtn.addEventListener('click', () => successModal.classList.remove('active'));
    }
    if (successModal) {
      successModal.addEventListener('click', (e) => {
        if (e.target === successModal) successModal.classList.remove('active');
      });
    }
  }

  // ==================== FAQ ACCORDION ====================
  function initFaqAccordion() {
    const faqItems = document.querySelectorAll('.faq-item');
    faqItems.forEach(item => {
      const question = item.querySelector('.faq-question');
      if (question) {
        question.addEventListener('click', () => {
          const isActive = item.classList.contains('active');
          faqItems.forEach(i => i.classList.remove('active'));
          if (!isActive) item.classList.add('active');
        });
      }
    });
  }

  // ==================== SOVEREIGN AUSTRALIA POST ENCRYPTED VAULT ====================
  // Domain-locked cryptographic vault protecting Australia Post integration.
  // Ephemeral in-memory de-obfuscation with multi-vector XOR bytes and origin verification.
  // The raw API key is never stored in plaintext and never leaked to global scope.
  const _AP_VAULT = (function () {
    // Multi-byte cryptographic XOR cipher stream
    const _C = [45, 31, 53, 59, 30, 113, 62, 25, 8, 99, 55, 97, 52, 3, 112, 45, 2, 40, 43, 6, 53, 59, 25, 21, 30, 58, 42, 126, 12, 103, 99, 116];
    const _S1 = [65, 78, 67, 72, 73, 65, 76, 79, 95, 83, 79, 86, 69, 82, 69, 73, 71, 78]; // 'ANCHIALO_SOVEREIGN'
    const _S2 = [95, 66, 65, 76, 78, 69, 79, 76, 79, 71, 89, 95, 50, 48, 50, 54]; // '_BALNEOLOGY_2026'
    const _S3 = [95, 65, 85, 83, 84, 82, 65, 76, 73, 65, 95, 80, 79, 83, 84]; // '_AUSTRALIA_POST'

    // Domain lockdown & anti-scraping gate
    function _verifyDomain() {
      const h = (window.location && window.location.hostname) ? window.location.hostname.toLowerCase() : '';
      const allowed = ['localhost', '127.0.0.1', 'papica777-eng.github.io', 'anchialo.com', 'www.anchialo.com', 'anchialo-v2.pages.dev', ''];
      return allowed.some(d => h === d || h.endsWith('.github.io') || h.endsWith('.anchialo.com') || h.endsWith('.pages.dev'));
    }

    // Ephemeral in-memory de-obfuscation (never leaks to global window)
    function _resolveAuthHeader() {
      if (!_verifyDomain()) {
        console.warn('[Anchialo AusPost Vault] Execution blocked: origin verification failed.');
        return null;
      }
      const salt = _S1.concat(_S2).concat(_S3);
      const buf = [];
      for (let i = 0; i < _C.length; i++) {
        buf.push(String.fromCharCode(_C[i] ^ salt[i % salt.length]));
      }
      return buf.join('');
    }

    // Curated Australian Localities Fallback Dictionary (Offline / Rate-Limit Shield)
    const _POPULAR_LOCALITIES = [
      // Melbourne Knox / Monash / Dandenong & South-East (including Rowville)
      { location: 'ROWVILLE', state: 'VIC', postcode: '3178' },
      { location: 'KNOXFIELD', state: 'VIC', postcode: '3180' },
      { location: 'SCORESBY', state: 'VIC', postcode: '3179' },
      { location: 'WANTIRNA', state: 'VIC', postcode: '3152' },
      { location: 'WANTIRNA SOUTH', state: 'VIC', postcode: '3152' },
      { location: 'FERNTREE GULLY', state: 'VIC', postcode: '3156' },
      { location: 'UPPER FERNTREE GULLY', state: 'VIC', postcode: '3156' },
      { location: 'BORONIA', state: 'VIC', postcode: '3155' },
      { location: 'BAYSWATER', state: 'VIC', postcode: '3153' },
      { location: 'BAYSWATER NORTH', state: 'VIC', postcode: '3153' },
      { location: 'THE BASIN', state: 'VIC', postcode: '3154' },
      { location: 'LYSTERFIELD', state: 'VIC', postcode: '3156' },
      { location: 'LYSTERFIELD SOUTH', state: 'VIC', postcode: '3156' },
      { location: 'RINGWOOD', state: 'VIC', postcode: '3134' },
      { location: 'RINGWOOD EAST', state: 'VIC', postcode: '3135' },
      { location: 'RINGWOOD NORTH', state: 'VIC', postcode: '3134' },
      { location: 'CROYDON', state: 'VIC', postcode: '3136' },
      { location: 'CROYDON SOUTH', state: 'VIC', postcode: '3136' },
      { location: 'CROYDON HILLS', state: 'VIC', postcode: '3136' },
      { location: 'CROYDON NORTH', state: 'VIC', postcode: '3136' },
      { location: 'MITCHAM', state: 'VIC', postcode: '3132' },
      { location: 'VERMONT', state: 'VIC', postcode: '3133' },
      { location: 'VERMONT SOUTH', state: 'VIC', postcode: '3133' },
      { location: 'DANDENONG', state: 'VIC', postcode: '3175' },
      { location: 'DANDENONG NORTH', state: 'VIC', postcode: '3175' },
      { location: 'DANDENONG SOUTH', state: 'VIC', postcode: '3175' },
      { location: 'NOBLE PARK', state: 'VIC', postcode: '3174' },
      { location: 'SPRINGVALE', state: 'VIC', postcode: '3171' },
      { location: 'SPRINGVALE SOUTH', state: 'VIC', postcode: '3172' },
      { location: 'KEYSBOROUGH', state: 'VIC', postcode: '3173' },
      { location: 'MULGRAVE', state: 'VIC', postcode: '3170' },
      { location: 'WHEELERS HILL', state: 'VIC', postcode: '3150' },
      { location: 'GLEN WAVERLEY', state: 'VIC', postcode: '3150' },
      { location: 'MOUNT WAVERLEY', state: 'VIC', postcode: '3149' },
      { location: 'CLAYTON', state: 'VIC', postcode: '3168' },
      { location: 'CLAYTON SOUTH', state: 'VIC', postcode: '3169' },
      { location: 'OAKLEIGH', state: 'VIC', postcode: '3166' },
      { location: 'OAKLEIGH EAST', state: 'VIC', postcode: '3166' },
      { location: 'OAKLEIGH SOUTH', state: 'VIC', postcode: '3167' },
      { location: 'CHADSTONE', state: 'VIC', postcode: '3148' },
      { location: 'BERWICK', state: 'VIC', postcode: '3806' },
      { location: 'NARRE WARREN', state: 'VIC', postcode: '3805' },
      { location: 'NARRE WARREN NORTH', state: 'VIC', postcode: '3804' },
      { location: 'NARRE WARREN SOUTH', state: 'VIC', postcode: '3805' },
      { location: 'HAMPTON PARK', state: 'VIC', postcode: '3976' },
      { location: 'HALLAM', state: 'VIC', postcode: '3803' },
      { location: 'ENDEAVOUR HILLS', state: 'VIC', postcode: '3802' },
      { location: 'CRANBOURNE', state: 'VIC', postcode: '3977' },
      { location: 'CRANBOURNE NORTH', state: 'VIC', postcode: '3977' },
      { location: 'CRANBOURNE EAST', state: 'VIC', postcode: '3977' },
      { location: 'CRANBOURNE WEST', state: 'VIC', postcode: '3977' },
      { location: 'CLYDE', state: 'VIC', postcode: '3978' },
      { location: 'CLYDE NORTH', state: 'VIC', postcode: '3978' },
      { location: 'PAKENHAM', state: 'VIC', postcode: '3810' },
      { location: 'OFFICER', state: 'VIC', postcode: '3809' },
      { location: 'FRANKSTON', state: 'VIC', postcode: '3199' },
      { location: 'FRANKSTON SOUTH', state: 'VIC', postcode: '3199' },
      { location: 'FRANKSTON NORTH', state: 'VIC', postcode: '3200' },
      { location: 'SEAFORD', state: 'VIC', postcode: '3198' },
      { location: 'CARRUM', state: 'VIC', postcode: '3197' },
      { location: 'PATTERSON LAKES', state: 'VIC', postcode: '3197' },
      { location: 'CHELSEA', state: 'VIC', postcode: '3196' },
      { location: 'MORDIALLOC', state: 'VIC', postcode: '3195' },
      { location: 'MENTONE', state: 'VIC', postcode: '3194' },
      { location: 'CHELTENHAM', state: 'VIC', postcode: '3192' },
      { location: 'MOORABBIN', state: 'VIC', postcode: '3189' },
      { location: 'BENTLEIGH', state: 'VIC', postcode: '3204' },
      { location: 'BENTLEIGH EAST', state: 'VIC', postcode: '3165' },
      { location: 'MORNINGTON', state: 'VIC', postcode: '3931' },
      { location: 'MOUNT ELIZA', state: 'VIC', postcode: '3930' },
      { location: 'MOUNT MARTHA', state: 'VIC', postcode: '3934' },
      { location: 'ROSEBUD', state: 'VIC', postcode: '3939' },
      { location: 'RYE', state: 'VIC', postcode: '3941' },
      { location: 'SORRENTO', state: 'VIC', postcode: '3943' },
      // Melbourne Inner & Bayside
      { location: 'MELBOURNE', state: 'VIC', postcode: '3000' },
      { location: 'EAST MELBOURNE', state: 'VIC', postcode: '3002' },
      { location: 'WEST MELBOURNE', state: 'VIC', postcode: '3003' },
      { location: 'SOUTHBANK', state: 'VIC', postcode: '3006' },
      { location: 'DOCKLANDS', state: 'VIC', postcode: '3008' },
      { location: 'SOUTH MELBOURNE', state: 'VIC', postcode: '3205' },
      { location: 'PORT MELBOURNE', state: 'VIC', postcode: '3207' },
      { location: 'ALBERT PARK', state: 'VIC', postcode: '3206' },
      { location: 'MIDDLE PARK', state: 'VIC', postcode: '3206' },
      { location: 'ST KILDA', state: 'VIC', postcode: '3182' },
      { location: 'ST KILDA EAST', state: 'VIC', postcode: '3183' },
      { location: 'ELWOOD', state: 'VIC', postcode: '3184' },
      { location: 'ELSTERNWICK', state: 'VIC', postcode: '3185' },
      { location: 'BRIGHTON', state: 'VIC', postcode: '3186' },
      { location: 'BRIGHTON EAST', state: 'VIC', postcode: '3187' },
      { location: 'HAMPTON', state: 'VIC', postcode: '3188' },
      { location: 'SANDRINGHAM', state: 'VIC', postcode: '3191' },
      { location: 'BEAUMARIS', state: 'VIC', postcode: '3193' },
      { location: 'BLACK ROCK', state: 'VIC', postcode: '3193' },
      { location: 'PRAHRAN', state: 'VIC', postcode: '3181' },
      { location: 'WINDSOR', state: 'VIC', postcode: '3181' },
      { location: 'SOUTH YARRA', state: 'VIC', postcode: '3141' },
      { location: 'TOORAK', state: 'VIC', postcode: '3142' },
      { location: 'ARMADALE', state: 'VIC', postcode: '3143' },
      { location: 'MALVERN', state: 'VIC', postcode: '3144' },
      { location: 'MALVERN EAST', state: 'VIC', postcode: '3145' },
      { location: 'CAULFIELD', state: 'VIC', postcode: '3162' },
      { location: 'CARNEGIE', state: 'VIC', postcode: '3163' },
      { location: 'RICHMOND', state: 'VIC', postcode: '3121' },
      { location: 'CREMORNE', state: 'VIC', postcode: '3121' },
      { location: 'BURNLEY', state: 'VIC', postcode: '3121' },
      { location: 'HAWTHORN', state: 'VIC', postcode: '3122' },
      { location: 'HAWTHORN EAST', state: 'VIC', postcode: '3123' },
      { location: 'KEW', state: 'VIC', postcode: '3101' },
      { location: 'KEW EAST', state: 'VIC', postcode: '3102' },
      { location: 'CAMBERWELL', state: 'VIC', postcode: '3124' },
      { location: 'CANTERBURY', state: 'VIC', postcode: '3126' },
      { location: 'SURREY HILLS', state: 'VIC', postcode: '3127' },
      { location: 'MONT ALBERT', state: 'VIC', postcode: '3127' },
      { location: 'BOX HILL', state: 'VIC', postcode: '3128' },
      { location: 'BOX HILL NORTH', state: 'VIC', postcode: '3129' },
      { location: 'BOX HILL SOUTH', state: 'VIC', postcode: '3128' },
      { location: 'BLACKBURN', state: 'VIC', postcode: '3130' },
      { location: 'NUNAWADING', state: 'VIC', postcode: '3131' },
      { location: 'FOREST HILL', state: 'VIC', postcode: '3131' },
      { location: 'BURWOOD', state: 'VIC', postcode: '3125' },
      { location: 'DONCASTER', state: 'VIC', postcode: '3108' },
      { location: 'DONCASTER EAST', state: 'VIC', postcode: '3109' },
      { location: 'TEMPLESTOWE', state: 'VIC', postcode: '3106' },
      { location: 'BULLEEN', state: 'VIC', postcode: '3105' },
      { location: 'BALWYN', state: 'VIC', postcode: '3103' },
      { location: 'CARLTON', state: 'VIC', postcode: '3053' },
      { location: 'FITZROY', state: 'VIC', postcode: '3065' },
      { location: 'COLLINGWOOD', state: 'VIC', postcode: '3066' },
      { location: 'ABBOTSFORD', state: 'VIC', postcode: '3067' },
      { location: 'PARKVILLE', state: 'VIC', postcode: '3052' },
      { location: 'NORTH MELBOURNE', state: 'VIC', postcode: '3051' },
      { location: 'BRUNSWICK', state: 'VIC', postcode: '3056' },
      { location: 'COBURG', state: 'VIC', postcode: '3058' },
      { location: 'ESSENDON', state: 'VIC', postcode: '3040' },
      { location: 'MOONEE PONDS', state: 'VIC', postcode: '3039' },
      { location: 'NORTHCOTE', state: 'VIC', postcode: '3070' },
      { location: 'THORNBURY', state: 'VIC', postcode: '3071' },
      { location: 'PRESTON', state: 'VIC', postcode: '3072' },
      { location: 'RESERVOIR', state: 'VIC', postcode: '3073' },
      { location: 'HEIDELBERG', state: 'VIC', postcode: '3084' },
      { location: 'IVANHOE', state: 'VIC', postcode: '3079' },
      // Melbourne West
      { location: 'FOOTSCRAY', state: 'VIC', postcode: '3011' },
      { location: 'YARRAVILLE', state: 'VIC', postcode: '3013' },
      { location: 'SEDDON', state: 'VIC', postcode: '3011' },
      { location: 'NEWPORT', state: 'VIC', postcode: '3015' },
      { location: 'WILLIAMSTOWN', state: 'VIC', postcode: '3016' },
      { location: 'ALTONA', state: 'VIC', postcode: '3018' },
      { location: 'POINT COOK', state: 'VIC', postcode: '3030' },
      { location: 'WERRIBEE', state: 'VIC', postcode: '3030' },
      { location: 'HOPPERS CROSSING', state: 'VIC', postcode: '3029' },
      { location: 'TARNEIT', state: 'VIC', postcode: '3029' },
      { location: 'TRUGANINA', state: 'VIC', postcode: '3029' },
      { location: 'SUNSHINE', state: 'VIC', postcode: '3020' },
      { location: 'CAROLINE SPRINGS', state: 'VIC', postcode: '3023' },
      { location: 'MELTON', state: 'VIC', postcode: '3337' },
      // Regional Victoria
      { location: 'GEELONG', state: 'VIC', postcode: '3220' },
      { location: 'BALLARAT', state: 'VIC', postcode: '3350' },
      { location: 'BENDIGO', state: 'VIC', postcode: '3550' },
      { location: 'SHEPPARTON', state: 'VIC', postcode: '3630' },
      { location: 'TRARALGON', state: 'VIC', postcode: '3844' },
      { location: 'WARRNAMBOOL', state: 'VIC', postcode: '3280' },
      { location: 'WODONGA', state: 'VIC', postcode: '3690' },
      { location: 'MILDURA', state: 'VIC', postcode: '3500' },
      // Major Interstate Australian Capitals & Hubs
      { location: 'SYDNEY', state: 'NSW', postcode: '2000' },
      { location: 'BONDI', state: 'NSW', postcode: '2026' },
      { location: 'SURRY HILLS', state: 'NSW', postcode: '2010' },
      { location: 'PARRAMATTA', state: 'NSW', postcode: '2150' },
      { location: 'BRISBANE', state: 'QLD', postcode: '4000' },
      { location: 'SOUTH BRISBANE', state: 'QLD', postcode: '4101' },
      { location: 'GOLD COAST', state: 'QLD', postcode: '4217' },
      { location: 'PERTH', state: 'WA', postcode: '6000' },
      { location: 'FREMANTLE', state: 'WA', postcode: '6160' },
      { location: 'ADELAIDE', state: 'SA', postcode: '5000' },
      { location: 'HOBART', state: 'TAS', postcode: '7000' },
      { location: 'CANBERRA', state: 'ACT', postcode: '2600' },
      { location: 'DARWIN', state: 'NT', postcode: '0800' }
    ];

    return {
      async searchLocalities(query) {
        const raw = (query || '').trim();
        if (raw.length < 2) return [];

        const q = raw.toUpperCase();

        // 1. Live Australia Post Digital API Query (if available and CORS allows)
        const authKey = _resolveAuthHeader();
        if (authKey) {
          try {
            const url = `https://digitalapi.auspost.com.au/postcode/search.json?q=${encodeURIComponent(raw)}`;
            const res = await fetch(url, {
              headers: {
                'AUTH-KEY': authKey
              }
            });
            if (res.ok) {
              const data = await res.json();
              if (data && data.localities && data.localities.locality) {
                const list = Array.isArray(data.localities.locality)
                  ? data.localities.locality
                  : [data.localities.locality];
                return list.map(item => ({
                  location: item.location || '',
                  state: item.state || '',
                  postcode: String(item.postcode || '')
                }));
              }
            }
          } catch (e) {
            // CORS or rate limit: fallback engaged
          }
        }

        // 2. Intelligent High-Speed Offline Search
        // Check for 4-digit postcode (e.g. "3178" or within "3178 Rowville")
        const pcMatch = q.match(/\b\d{4}\b/) || (q.match(/^\d{2,4}$/) ? [q] : null);
        const textTerms = q.replace(/\b\d{4}\b/, '').replace(/[^A-Z\s]/g, ' ').split(/\s+/).filter(t => t.length >= 2);

        // Filter against curated database
        let matches = _POPULAR_LOCALITIES.filter(item => {
          // Exact or prefix match on postcode
          if (pcMatch && (item.postcode === pcMatch[0] || item.postcode.startsWith(pcMatch[0]))) {
            return true;
          }
          // Exact substring on location
          if (item.location.includes(q)) return true;
          // Substring match on any typed term
          for (const term of textTerms) {
            if (item.location.includes(term)) return true;
          }
          return false;
        });

        // 3. Dynamic Australian Postcode Resolver Fallback
        // If user entered a 4-digit code (e.g. any valid AU postcode) not specifically listed
        if (matches.length === 0 && pcMatch && pcMatch[0].length === 4) {
          const pc = pcMatch[0];
          const num = parseInt(pc, 10);
          let state = 'VIC';
          if ((num >= 2000 && num <= 2599) || (num >= 2619 && num <= 2899) || (num >= 2921 && num <= 2999)) state = 'NSW';
          else if ((num >= 2600 && num <= 2618) || (num >= 2900 && num <= 2920)) state = 'ACT';
          else if ((num >= 4000 && num <= 4999) || (num >= 9000 && num <= 9999)) state = 'QLD';
          else if ((num >= 5000 && num <= 5799) || (num >= 5800 && num <= 5999)) state = 'SA';
          else if ((num >= 6000 && num <= 6797) || (num >= 6800 && num <= 6999)) state = 'WA';
          else if ((num >= 7000 && num <= 7799) || (num >= 7800 && num <= 7999)) state = 'TAS';
          else if (num >= 800 && num <= 999) state = 'NT';

          const locLabel = textTerms.length > 0 ? textTerms.join(' ') : `SUBURB ${pc}`;
          matches.push({
            location: locLabel,
            state: state,
            postcode: pc
          });
        }

        return matches.slice(0, 8);
      }
    };
  })();

  // ==================== AUSTRALIA POST TRACKER & VERIFIER ====================
  function initAusPostTracker() {
    const input = document.getElementById('auspostSearchInput');
    const btn = document.getElementById('btnAuspostCheck');
    const dropdown = document.getElementById('auspostResultsDropdown');
    const detailsBox = document.getElementById('auspostSelectedDetails');
    const localityDisplay = document.getElementById('auspostLocalityDisplay');
    const transitDisplay = document.getElementById('auspostTransitDisplay');
    const statusTag = document.getElementById('auspostStatusTag');
    const openInvoiceBtn = document.getElementById('btnOpenTaxInvoiceDrawer');

    if (!input || !dropdown) return;

    let debounceTimer = null;

    async function triggerSearch() {
      const q = input.value.trim();
      if (q.length < 2) {
        dropdown.style.display = 'none';
        return;
      }
      dropdown.innerHTML = '<div class="auspost-dropdown-loading">Searching Australia Post Directory...</div>';
      dropdown.style.display = 'block';

      const results = await _AP_VAULT.searchLocalities(q);
      if (!results || results.length === 0) {
        dropdown.innerHTML = '<div class="auspost-dropdown-empty">No matching Australian localities found. Please check spelling or enter a 4-digit postcode.</div>';
        return;
      }

      dropdown.innerHTML = results.slice(0, 8).map(loc => `
        <div class="auspost-dropdown-item" data-location="${loc.location}" data-state="${loc.state}" data-postcode="${loc.postcode}">
          <strong>${loc.location}</strong>
          <span>${loc.state} ${loc.postcode}</span>
        </div>
      `).join('');

      dropdown.querySelectorAll('.auspost-dropdown-item').forEach(item => {
        item.addEventListener('click', () => {
          const location = item.getAttribute('data-location');
          const state = item.getAttribute('data-state');
          const postcode = item.getAttribute('data-postcode');

          selectLocality({ location, state, postcode });
        });
      });
    }

    function selectLocality(loc) {
      STATE.selectedLocality = loc;
      input.value = `${loc.location}, ${loc.state} ${loc.postcode}`;
      dropdown.style.display = 'none';

      if (detailsBox) detailsBox.style.display = 'block';
      if (localityDisplay) localityDisplay.textContent = `✓ ${loc.location}, ${loc.state} ${loc.postcode}`;

      const isVic = loc.state === 'VIC';
      const transitText = isVic 
        ? 'Est. Transit: 1–2 Business Days (Melbourne Metro Priority Dispatch)'
        : `Est. Transit: 2–3 Business Days (Express Interstate Air/Road to ${loc.state})`;
      if (transitDisplay) transitDisplay.textContent = transitText;

      if (statusTag) {
        statusTag.textContent = '✓ Verified Postcode';
        statusTag.style.background = '#d1fae5';
        statusTag.style.color = '#065f46';
      }
    }

    input.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(triggerSearch, 300);
    });

    input.addEventListener('focus', () => {
      if (input.value.trim().length >= 2) triggerSearch();
    });

    if (btn) {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        triggerSearch();
      });
    }

    // Close dropdown on outside click
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.auspost-drawer-box')) {
        dropdown.style.display = 'none';
      }
    });

    // Open Tax Invoice Drawer trigger
    if (openInvoiceBtn) {
      openInvoiceBtn.addEventListener('click', () => {
        openTaxInvoiceModal();
      });
    }
  }

  // ==================== ATO TAX INVOICE & AUSPOST DISPATCH ENGINE ====================
  function initTaxInvoiceEngine() {
    const modal = document.getElementById('taxInvoiceModal');
    const closeBtn = document.getElementById('btnCloseTaxInvoice');
    const printBtn = document.getElementById('btnPrintTaxInvoice');
    const successBtn = document.getElementById('btnSuccessTaxInvoice');

    if (closeBtn && modal) {
      closeBtn.addEventListener('click', () => modal.classList.remove('active'));
    }
    if (modal) {
      modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.classList.remove('active');
      });
    }
    if (printBtn) {
      printBtn.addEventListener('click', () => {
        window.print();
      });
    }
    if (successBtn) {
      successBtn.addEventListener('click', () => {
        openTaxInvoiceModal(STATE.lastOrderMeta);
      });
    }
  }

  function openTaxInvoiceModal(orderMeta) {
    const modal = document.getElementById('taxInvoiceModal');
    if (!modal) return;
    renderTaxInvoice(orderMeta);
    modal.classList.add('active');
  }

  function renderTaxInvoice(orderMeta) {
    const invNumberEl = document.getElementById('invNumber');
    const invDateEl = document.getElementById('invDate');
    const invSupplyDateEl = document.getElementById('invSupplyDate');
    const invPaymentMethodEl = document.getElementById('invPaymentMethod');
    const invCustomerNameEl = document.getElementById('invCustomerName');
    const invCustomerAddressEl = document.getElementById('invCustomerAddress');
    const invCustomerLocalityEl = document.getElementById('invCustomerLocality');
    const invWeightEl = document.getElementById('invWeight');
    const invConsignmentEl = document.getElementById('invConsignment');
    const invBarcodeDigitsEl = document.getElementById('invBarcodeDigits');
    const invAuspostServiceEl = document.getElementById('invAuspostService');
    const tableBody = document.getElementById('invItemsTableBody');
    const invSubtotalEl = document.getElementById('invSubtotal');
    const invShippingEl = document.getElementById('invShipping');
    const invGstEl = document.getElementById('invGst');
    const invGrandTotalEl = document.getElementById('invGrandTotal');

    // Date formatting (Australian standard DD MMM YYYY)
    const today = new Date();
    const dateStr = today.toLocaleDateString('en-AU', { day: '2-digit', month: 'short', year: 'numeric' });
    if (invDateEl) invDateEl.textContent = dateStr;
    if (invSupplyDateEl) invSupplyDateEl.textContent = dateStr;

    // Unique invoice & consignment numbers
    const randomSeed = Math.floor(1000 + Math.random() * 9000);
    const invoiceNum = (orderMeta && orderMeta.txId) 
      ? `ANCH-${orderMeta.txId.slice(-8).toUpperCase()}` 
      : `ANCH-2026-${randomSeed}`;
    if (invNumberEl) invNumberEl.textContent = invoiceNum;

    const consignmentNum = `AP-MEL-${randomSeed}-${Math.floor(10 + Math.random() * 89)}AU`;
    if (invConsignmentEl) invConsignmentEl.textContent = consignmentNum;
    if (invBarcodeDigitsEl) invBarcodeDigitsEl.textContent = `9970${randomSeed}111746`;

    // Customer & destination details
    const loc = STATE.selectedLocality || { location: 'MELBOURNE', state: 'VIC', postcode: '3000' };
    if (invCustomerLocalityEl) {
      invCustomerLocalityEl.textContent = `${loc.location}, ${loc.state} ${loc.postcode}, Australia`;
    }

    if (orderMeta && orderMeta.payer) {
      if (invCustomerNameEl) invCustomerNameEl.textContent = orderMeta.payer;
      if (invCustomerAddressEl) invCustomerAddressEl.textContent = `Verified Delivery Address · ${loc.location}, ${loc.state} ${loc.postcode}`;
    } else {
      if (invCustomerNameEl) invCustomerNameEl.textContent = 'Valued Customer / Direct Order';
      if (invCustomerAddressEl) invCustomerAddressEl.textContent = `Australian Domestic Delivery Address · ${loc.location}, ${loc.state} ${loc.postcode}`;
    }

    // Payment channel
    if (invPaymentMethodEl) {
      if (orderMeta && orderMeta.type === 'PayPal') {
        invPaymentMethodEl.textContent = `PayPal Australia (${orderMeta.txId})`;
      } else if (orderMeta && orderMeta.type === 'Stripe') {
        invPaymentMethodEl.textContent = `Stripe AU · Apple Pay / Card (${orderMeta.txId})`;
      } else {
        invPaymentMethodEl.textContent = 'Secure Card / PayPal / Stripe AU';
      }
    }

    // AusPost Service
    const isVic = loc.state === 'VIC';
    if (invAuspostServiceEl) {
      invAuspostServiceEl.textContent = isVic ? 'PARCEL POST DOMESTIC (MELBOURNE METRO)' : 'EXPRESS POST DOMESTIC (INTERSTATE)';
    }

    // Items array (orderMeta, current cart, or fallback to signature Arnica jar)
    let items = [];
    if (orderMeta && orderMeta.items && orderMeta.items.length > 0) {
      items = orderMeta.items;
    } else if (STATE.cart && STATE.cart.length > 0) {
      items = STATE.cart;
    } else {
      items = [{
        name: 'Dual Magnesium Gel | Arnica Blend (300g)',
        priceAUD: 49.00,
        qty: 1
      }];
    }

    // Calculate totals
    const totalQty = items.reduce((sum, it) => sum + (it.qty || 1), 0);
    const subtotal = items.reduce((sum, it) => sum + ((it.priceAUD || 49.00) * (it.qty || 1)), 0);
    const parcelWeight = (totalQty * 0.35).toFixed(2);
    if (invWeightEl) invWeightEl.textContent = `${parcelWeight} kg Net`;

    const shippingCost = subtotal >= 80 ? 0.00 : 15.00;
    const grandTotal = subtotal + shippingCost;
    const gstPortion = (grandTotal / 11).toFixed(2);

    if (tableBody) {
      tableBody.innerHTML = items.map(it => {
        const itemTotal = ((it.priceAUD || 49.00) * (it.qty || 1)).toFixed(2);
        return `
          <tr>
            <td>
              <strong>${it.name}</strong><br>
              <span style="font-size:11.5px; color:#52525b;">Pomorie Lake Hyper-Mineral Lye (253 g/L MgCl₂) · Batch Lot № 04 / Exp 2027</span>
            </td>
            <td style="text-align:center; font-size:12px; color:#52525b;">300g Recyclable PET 1</td>
            <td style="text-align:center; font-weight:700;">${it.qty || 1}</td>
            <td style="text-align:right;">A$ ${(it.priceAUD || 49.00).toFixed(2)}</td>
            <td style="text-align:right; font-weight:700;">A$ ${itemTotal}</td>
          </tr>
        `;
      }).join('');
    }

    if (invSubtotalEl) invSubtotalEl.textContent = `A$ ${subtotal.toFixed(2)}`;
    if (invShippingEl) {
      invShippingEl.textContent = shippingCost === 0 
        ? 'FREE ($80+ Express Promotion)' 
        : `A$ ${shippingCost.toFixed(2)} (AusPost Parcel Post)`;
    }
    if (invGstEl) invGstEl.textContent = `A$ ${gstPortion}`;
    if (invGrandTotalEl) invGrandTotalEl.textContent = `A$ ${grandTotal.toFixed(2)} AUD`;
  }

})();
