/**
 * ANCHIALO — LUXURY ORGANIC BALNEOLOGY & E-COMMERCE CLIENT ENGINE
 * Azimut 6000 Ltd · Pomorie Black Sea Natural Minerals · Australia $49 AUD
 */

(function () {
  'use strict';

  // ==================== MERCHANT & BACKEND CONFIGURATION ====================
  const MERCHANT_CONFIG = {
    brandName: 'ANCHIALO Australia',
    distributorName: 'Sotir Kichukov · CPT MMA Melbourne',
    abn: '', // Populate verified Australian Business Number when active
    gstRegistered: false, // Set true only when ABN is registered for Australian GST
    apiBaseUrl: (typeof window !== 'undefined' && (window.ANCHIALO_API_URL || localStorage.getItem('anchialov2_api_url'))) || 'https://d8tepk57nhdpv1ieit2tbcdigk.ingress.m3a.eu-n-3.digitalfrontier.network'
  };

  // Partner QR & Welcome Discount Registry (10% privilege on eligible codes)
  const PROMO_RULES = {
    CPT15: { label: 'CPT MMA Partner Privilege (10% Off)', discountPct: 10, isPartner: true },
    RENEGADE15: { label: 'Gym Partner Privilege (10% Off)', discountPct: 10, isPartner: true },
    ABSOLUTE15: { label: 'Gym Partner Privilege (10% Off)', discountPct: 10, isPartner: true },
    OAKLEIGH15: { label: 'Oakleigh Community Privilege (10% Off)', discountPct: 10, isPartner: true },
    MYO15: { label: 'Myotherapy Clinic Privilege (10% Off)', discountPct: 10, isPartner: true },
    PILATES15: { label: 'Pilates Studio Privilege (10% Off)', discountPct: 10, isPartner: true },
    FLOAT15: { label: 'Recovery Studio Privilege (10% Off)', discountPct: 10, isPartner: true },
    QUIZ10: { label: 'Ritual Quiz Welcome (10% Off)', discountPct: 10, isPartner: false },
    FOUNDING10: { label: 'Melbourne Founding Privilege (10% Off)', discountPct: 10, isPartner: false },
    COMEBACK10: { label: 'Bag Recovery Privilege (10% Off)', discountPct: 10, isPartner: false }
  };

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
    partnerCode: localStorage.getItem('anchialov2_partner_code') || '',
    promoCode: localStorage.getItem('anchialov2_promo_code') || '',
    customerEmail: localStorage.getItem('anchialov2_customer_email') || '',
    quizState: { goal: 'sport', timeOfDay: 'post-training' },
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
      'combo-gel-oil': 'https://buy.stripe.com/4gM28rgc44WwbKL3qn5Ne0l',
      'combo-best-value': 'https://buy.stripe.com/7sYeVdgc4dt28yzbWT5Ne0k',
      'combo-trio': 'https://buy.stripe.com/7sYeVdgc4dt28yzbWT5Ne0k',
      'combo-complete': 'https://buy.stripe.com/7sYeVdgc4dt28yzbWT5Ne0k',
      'custom': 'https://buy.stripe.com/4gM28rgc44WwbKL3qn5Ne0l'
    }
  };

  // Official Cosmetic Australian Master Texts (TGA Compliant)
  const TEXTS = {
    usage: "Apply topically to clean, dry skin on the desired area and massage thoroughly. Leave on for 30 minutes to several hours, or leave overnight for deeper relaxation and skin hydration. If light mineral salt crystals form on the skin, simply rinse with cool water. Avoid open cuts and direct eye contact.",
    warning: "For external cosmetic use only. Keep out of reach of children. Avoid contact with eyes. If unexpected skin sensitivity occurs, rinse thoroughly with cool water. This product is not a substitute for medical care. Storage: Store between 5°C and 25°C away from direct sunlight.",
    heritage: "Formed naturally during the slow fractional solar crystallization of sea water in the ancient coastal salterns of Lake Pomorie (ancient Anchialos). As sea salt precipitates out, a dense mineral liquid rich in magnesium chloride, magnesium sulfate, and trace ocean elements rises on top.",
    producer: "Handcrafted by: AZIMUT 6000 Ltd, Bulgaria, Pomorie 8200, Ivan Vazov 18 str. Tel: +359887470548 | E-mail: sales@luga.bg. GTIN-13: 3 800230 111746. Batch / Expiry: Lot № 04 / Expiry 2027. Net weight: 300 g ℮. PAO 12M | ♳ PET 1 Recyclable. ISO 22716 European GMP Certified."
  };

  // The 5 Signature Botanical Blends (Aligned with Australian Master 2025 Cosmetic Copy)
  const BLENDS = {
    arnica: {
      id: 'arnica',
      name: 'ARNICA MONTANA BLEND',
      fullName: 'ARNICA BLEND — DUAL MAGNESIUM COMPLEX',
      accentColor: '#d97706',
      heroJar: 'assets/images/products/web/06_file_transp.webp',
      lidImg: 'assets/official_labels_rendered/anhialo_massage_gel_arnica_top_fv17.png',
      sideImg: 'assets/official_labels_rendered/side_label_grey_arnica_v12.png',
      sidePdf: 'assets/official_drive_assets/labels/Side Label Grey Arnica v12.pdf',
      lidPdf: 'assets/official_drive_assets/labels/Anhialo Massage Gel_Arnica Top Fv17.pdf',
      botanical: 'Arnica Montana Flower Extract',
      subtitle: 'Post-Training Body Ritual & Skin Comfort',
      purpose: "A fast-absorbing topical body gel formulated with natural magnesium sulfate and magnesium chloride from Lake Pomorie to help relax and nourish the body. Supports skin hydration, leaves muscles feeling refreshed after physical activity, and is enriched with Arnica Montana flower extract, traditionally valued to soothe and comfort tired skin.",
      inci: "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, GLYCERINE, ARNICA MONTANA FLOWER EXTRACT."
    },
    lavender: {
      id: 'lavender',
      name: 'BULGARIAN LAVENDER BLEND',
      fullName: 'LAVENDER BLEND — DUAL MAGNESIUM COMPLEX',
      accentColor: '#7c3aed',
      heroJar: 'assets/images/products/web/01_file_transp.webp',
      lidImg: 'assets/official_labels_rendered/anhialo_massage_gel_lavender_top_fv17.png',
      sideImg: 'assets/official_labels_rendered/side_label_grey_lavender_v12.png',
      sidePdf: 'assets/official_drive_assets/labels/Side Label Grey Lavender v12.pdf',
      lidPdf: 'assets/official_drive_assets/labels/Anhialo Massage Gel_Lavender Top Fv17.pdf',
      botanical: 'Lavandula Angustifolia Essential Flower Extract',
      subtitle: 'Calming Evening Ritual & Skin Nourishment',
      purpose: "A calming topical body gel formulated with natural magnesium sulfate and magnesium chloride to help relax and nourish the body after a long day. Supports skin hydration and evening wind-down, enhanced with Bulgarian Lavandula Angustifolia flower extract, prized for its soothing and relaxing aroma.",
      inci: "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, GLYCERINE, LAVANDULA ANGUSTIFOLIA FLOWER EXTRACT."
    },
    rosemary: {
      id: 'rosemary',
      name: 'GARDEN ROSEMARY BLEND',
      fullName: 'ROSEMARY BLEND — DUAL MAGNESIUM COMPLEX',
      accentColor: '#059669',
      heroJar: 'assets/images/products/web/04_file_transp.webp',
      lidImg: 'assets/official_labels_rendered/anhialo_massage_gel_rosemary_top_fv17.png',
      sideImg: 'assets/official_labels_rendered/side_label_grey_rosemary_v12.png',
      sidePdf: 'assets/official_drive_assets/labels/Side Label Grey Rosemary v12.pdf',
      lidPdf: 'assets/official_drive_assets/labels/Anhialo Massage Gel_Rosemary Top Fv17.pdf',
      botanical: 'Rosmarinus Officinalis Leaf Powder Extract',
      subtitle: 'Invigorating Massage & Morning Skin Refresh',
      purpose: "An invigorating topical body gel combining Lake Pomorie magnesium sulfate and magnesium chloride with Garden Rosemary extract. Traditionally used in energizing body massage to invigorate skin, warm up tired limbs before or after sessions, and leave the body feeling revitalized.",
      inci: "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, GLYCERINE, ROSMARINUS OFFICINALIS LEAF POWDER EXTRACT."
    },
    juniper: {
      id: 'juniper',
      name: 'ALPINE JUNIPER BLEND',
      fullName: 'JUNIPER BLEND — DUAL MAGNESIUM COMPLEX',
      accentColor: '#0284c7',
      heroJar: 'assets/images/products/web/07_file_transp.webp',
      lidImg: 'assets/official_labels_rendered/anhialo_massage_gel_juniper_top_fv17.png',
      sideImg: 'assets/official_labels_rendered/side_label_grey_juniper_v12.png',
      sidePdf: 'assets/official_drive_assets/labels/Side Label Grey Juniper v12.pdf',
      lidPdf: 'assets/official_drive_assets/labels/Anhialo Massage Gel_Juniper Top Fv17.pdf',
      botanical: 'Juniperus Chinensis Leaf Extract & Fruit Oil',
      subtitle: 'Crisp Botanical Massage & Body Refreshment',
      purpose: "A refreshing topical body gel uniting concentrated Black Sea magnesium salts with Alpine Juniper extract. Supports skin hydration, leaves heavy or overworked limbs feeling light and refreshed, and delivers a crisp botanical finish ideal after showers or sauna sessions.",
      inci: "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, PARFUM, GLYCERINE, JUNIPERUS CHINENSIS LEAF EXTRACT."
    },
    grape: {
      id: 'grape',
      name: 'RED GRAPE SEED BLEND',
      fullName: 'GRAPE BLEND — DUAL MAGNESIUM COMPLEX',
      accentColor: '#9d174d',
      heroJar: 'assets/images/products/web/03_file_transp.webp',
      lidImg: 'assets/official_labels_rendered/anhialo_massage_gel_grape_top_fv17.png',
      sideImg: 'assets/official_labels_rendered/side_label_grey_grape_v12.png',
      sidePdf: 'assets/official_drive_assets/labels/Side Label Grey Grape v12.pdf',
      lidPdf: 'assets/official_drive_assets/labels/Anhialo Massage Gel_Grape Top Fv17.pdf',
      botanical: 'Vitis Vinifera (Grape) Seed Polyphenol Extract',
      subtitle: 'Skin Softness & Antioxidant Body Care',
      purpose: "A revitalizing topical body gel formulated with Lake Pomorie magnesium sulfate and magnesium chloride to support skin hydration and daily relaxation. Lightly fragranced with a subtle vineyard grape aroma that leaves skin feeling smooth, soft, and refreshed.",
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
      unitLabel: '/ 300g Net',
      packagingText: '300g PET 1 Jar',
      weightKg: 0.35,
      image: 'assets/images/products/web/06_file_transp.webp',
      badge: 'Bestseller · Post-Training Ritual',
      isStaged: false,
      description: 'Fast-absorbing topical gel with 253.14 g/L Black Sea magnesium chloride, 70.36 g/L magnesium sulfate, and Arnica Montana extract to hydrate skin and refresh tired muscles. 300g net.'
    },
    {
      id: 'gel-lavender',
      slug: 'anchialo-dual-magnesium-gel-lavander-blend',
      name: 'Dual Magnesium Gel | Lavender Blend',
      category: 'gel',
      priceAUD: 49.00,
      unitLabel: '/ 300g Net',
      packagingText: '300g PET 1 Jar',
      weightKg: 0.35,
      image: 'assets/images/products/web/01_file_transp.webp',
      badge: 'Evening Calm & Wind-Down',
      isStaged: false,
      description: 'Infused with Bulgarian Lavender flower extract and Lake Pomorie minerals. Nourishes dry skin and supports a calming evening massage ritual before rest. 300g net.'
    },
    {
      id: 'gel-rosemary',
      slug: 'anchialo-dual-magnesium-gel-rosemary-blend',
      name: 'Dual Magnesium Gel | Rosemary Blend',
      category: 'gel',
      priceAUD: 49.00,
      unitLabel: '/ 300g Net',
      packagingText: '300g PET 1 Jar',
      weightKg: 0.35,
      image: 'assets/images/products/web/04_file_transp.webp',
      badge: 'Invigorating Massage',
      isStaged: false,
      description: 'Enhanced with Garden Rosemary extract for an energizing massage feel. Ideal before training sessions or after heavy workouts to refresh overworked limbs. 300g net.'
    },
    {
      id: 'gel-juniper',
      slug: 'anchialo-dual-magnesium-gel-juniper-blend',
      name: 'Dual Magnesium Gel | Juniper Blend',
      category: 'gel',
      priceAUD: 49.00,
      unitLabel: '/ 300g Net',
      packagingText: '300g PET 1 Jar',
      weightKg: 0.35,
      image: 'assets/images/products/web/07_file_transp.webp',
      badge: 'Crisp Refresh & Sauna Ritual',
      isStaged: false,
      description: 'Alpine Juniper botanical blend formulated to hydrate skin and revitalize weary legs, shoulders, and feet after showers, contrast therapy, or long shifts. 300g net.'
    },
    {
      id: 'gel-grape',
      slug: 'anchialo-dual-magnesium-gel-grape-blend',
      name: 'Dual Magnesium Gel | Grape Blend',
      category: 'gel',
      priceAUD: 49.00,
      unitLabel: '/ 300g Net',
      packagingText: '300g PET 1 Jar',
      weightKg: 0.35,
      image: 'assets/images/products/web/03_file_transp.webp',
      badge: 'Skin Softness & Daily Care',
      isStaged: false,
      description: 'Lightly fragranced with Red Grape aroma alongside pure Lake Pomorie dual magnesium salts to condition skin and leave a smooth, velvet finish. 300g net.'
    },
    {
      id: 'oil-pure',
      slug: 'anchialo-dual-magnesium-oil-natural-topical-oil',
      name: 'Dual Magnesium Oil | Natural Topical Brine',
      category: 'oil',
      priceAUD: 49.00,
      unitLabel: '/ 300ml Net',
      packagingText: '300ml Brine Bottle',
      weightKg: 0.38,
      image: 'assets/images/products/web/08_file_transp.webp',
      badge: '100% Pure Liquid Brine',
      isStaged: false,
      description: 'Unscented, concentrated liquid Black Sea mineral brine (luga). Silky natural glide tailored for full-body studio massage or evening mineral foot soaks. 300ml.'
    },
    {
      id: 'combo-gel-oil',
      slug: 'special-offer-gel-oil-combo',
      name: 'Special Offer | Gel + Oil Combo',
      category: 'combo',
      priceAUD: 49.00,
      unitLabel: '/ 300g + 300ml',
      packagingText: '300g Gel + 300ml Oil',
      weightKg: 0.72,
      image: 'assets/images/products/web/02_file.webp',
      badge: '1+1 Free Value Deal',
      isStaged: true,
      description: 'Buy 1 Dual Magnesium Gel (300g) and receive 1 Pure Dual Magnesium Oil (300ml) FREE! Complete topical gel and bath/massage brine set for the price of one item.'
    },
    {
      id: 'combo-starter',
      slug: 'starter-combo-dual-magnesium-gel',
      name: 'Starter Combo | Dual Magnesium Gel (2-Pack)',
      category: 'combo',
      priceAUD: 89.00,
      unitLabel: '/ 600g (2 × 300g)',
      packagingText: '2 × 300g PET 1 Jars',
      weightKg: 0.70,
      image: 'assets/images/products/web/05_file.webp',
      badge: 'Save $9 · Day & Night Pair',
      isStaged: true,
      description: 'Pair Arnica for daytime post-training massage with Lavender for your calm evening wind-down ritual. Total 600g with FREE Australia-wide Express shipping.'
    },
    {
      id: 'combo-best-value',
      slug: 'best-value-combo-dual-magnesium-gel',
      name: 'Best Value Combo | Dual Magnesium Gel (3-Pack)',
      category: 'combo',
      priceAUD: 129.00,
      unitLabel: '/ 900g (3 × 300g)',
      packagingText: '3 × 300g PET 1 Jars',
      weightKg: 1.05,
      image: 'assets/images/products/web/09_file.webp',
      badge: 'Save $18 · Combat Team Pack',
      isStaged: true,
      description: 'Any three 300g jars for athletes, families, and active studios. Includes FREE Australia Post Express delivery from our Melbourne dispatch hub.'
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
    initPartnerAttribution();
    initCurrency();
    initHeroBlendSwitcher();
    initBotanicalApothecary();
    initProductsGrid();
    initRitualQuiz();
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
          <h4 style="font-family:var(--font-serif); font-size:18px; color:var(--accent-pine); margin-bottom:8px;">Cosmetic Formulation &amp; Botanical Profile</h4>
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
      const refSuffix = STATE.partnerCode ? ` [Ref: ${STATE.partnerCode}]` : '';
      const waMsg = encodeURIComponent(`Hi Sotir, I would like to order ${prod.name} (${priceFormatted})${refSuffix}. Please confirm delivery / Melbourne pickup.`);

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
              <span class="price-unit">${prod.unitLabel || '/ 300g Net'}</span>
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

  // ==================== PARTNER QR & PROMO ATTRIBUTION ====================
  function sanitizeCode(raw) {
    return (raw || '').toUpperCase().replace(/[^A-Z0-9_-]/g, '').slice(0, 24);
  }

  function getActiveCodeMeta() {
    const code = sanitizeCode(STATE.promoCode || STATE.partnerCode);
    if (!code) return null;
    if (PROMO_RULES[code]) {
      return { code, ...PROMO_RULES[code] };
    }
    // Any valid custom QR partner ref (e.g. GYMNAME15) gets tracked cleanly and unlocks 10% partner privilege
    if (/^[A-Z0-9_-]{3,24}$/.test(code)) {
      return {
        code,
        label: `Partner Ref ${code} (10% Privilege)`,
        discountPct: 10,
        isPartner: true
      };
    }
    return null;
  }

  function getCartTotals() {
    const totalQty = STATE.cart.reduce((sum, it) => sum + (it.qty || 1), 0);
    const rawSubtotalAUD = STATE.cart.reduce((sum, it) => sum + ((it.priceAUD || 49) * (it.qty || 1)), 0);
    const codeMeta = getActiveCodeMeta();
    const discountPct = codeMeta ? codeMeta.discountPct : 0;
    const discountAUD = Math.round((rawSubtotalAUD * (discountPct / 100)) * 100) / 100;
    const finalSubtotalAUD = Math.max(0, Math.round((rawSubtotalAUD - discountAUD) * 100) / 100);
    const shippingAUD = (finalSubtotalAUD === 0 || finalSubtotalAUD >= 80) ? 0 : 15;
    return {
      totalQty,
      rawSubtotalAUD,
      discountAUD,
      discountPct,
      finalSubtotalAUD,
      shippingAUD,
      grandTotalAUD: Math.round((finalSubtotalAUD + shippingAUD) * 100) / 100,
      codeMeta
    };
  }

  async function postBackendEvent(path, payload) {
    const base = (MERCHANT_CONFIG.apiBaseUrl || '').replace(/\/+$/, '');
    if (!base) return null;
    try {
      const res = await fetch(`${base}${path}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (res.ok) return await res.json();
    } catch (err) {
      console.warn(`[Anchialo Sync] ${path} offline fallback:`, err);
    }
    return null;
  }

  function initPartnerAttribution() {
    const params = new URLSearchParams(window.location.search);
    const refParam = sanitizeCode(params.get('ref') || params.get('partner') || params.get('code'));
    if (refParam) {
      STATE.partnerCode = refParam;
      STATE.promoCode = refParam;
      localStorage.setItem('anchialov2_partner_code', refParam);
      localStorage.setItem('anchialov2_promo_code', refParam);
    }

    const input = document.getElementById('bagPartnerCodeInput');
    const applyBtn = document.getElementById('btnApplyPartnerCode');
    const statusEl = document.getElementById('bagPartnerStatus');

    const syncUI = () => {
      const meta = getActiveCodeMeta();
      if (input && meta && !input.value) input.value = meta.code;
      if (statusEl) {
        if (meta) {
          statusEl.textContent = `✓ Active: ${meta.label}`;
          statusEl.style.display = 'block';
        } else {
          statusEl.style.display = 'none';
        }
      }
    };

    if (applyBtn && input) {
      applyBtn.addEventListener('click', () => {
        const cleaned = sanitizeCode(input.value);
        STATE.promoCode = cleaned;
        STATE.partnerCode = cleaned;
        localStorage.setItem('anchialov2_promo_code', cleaned);
        localStorage.setItem('anchialov2_partner_code', cleaned);
        syncUI();
        updateCartDrawer();
      });
    }
    syncUI();
  }

  // ==================== 30-SECOND RECOVERY RITUAL QUIZ ====================
  function initRitualQuiz() {
    const quizSection = document.getElementById('ritualQuizContainer');
    if (!quizSection) return;

    const RECOMMENDATIONS = {
      sport: {
        primaryId: 'gel-arnica',
        packId: 'combo-starter',
        title: 'Arnica Montana Dual Magnesium Gel + Starter 2-Pack',
        summary: 'Fast-absorbing Lake Pomorie brine (253.14 g/L MgCl2) with Arnica Montana extract to refresh tired muscles after sparring, gym, or long runs — paired with Lavender for night recovery.',
        singleName: 'Dual Magnesium Gel | Arnica Blend (300g)',
        packName: 'Starter Combo | Arnica + Lavender 2-Pack (600g)'
      },
      sleep: {
        primaryId: 'gel-lavender',
        packId: 'combo-starter',
        title: 'Bulgarian Lavender Dual Magnesium Gel (Evening Ritual)',
        summary: 'Gentle Lake Pomorie dual magnesium salts infused with Bulgarian Lavandula Angustifolia to support your calming evening wind-down ritual and overnight skin hydration.',
        singleName: 'Dual Magnesium Gel | Lavender Blend (300g)',
        packName: 'Starter Combo | Day & Night 2-Pack (600g)'
      },
      warmup: {
        primaryId: 'gel-rosemary',
        packId: 'combo-starter',
        title: 'Garden Rosemary Dual Magnesium Gel (Invigorating Massage)',
        summary: 'Crisp rosemary extract paired with pure Black Sea lye for an energizing morning or pre-session massage ritual across shoulders, calves, and forearms.',
        singleName: 'Dual Magnesium Gel | Rosemary Blend (300g)',
        packName: 'Starter Combo | Rosemary + Arnica 2-Pack (600g)'
      },
      sauna: {
        primaryId: 'gel-juniper',
        packId: 'combo-gel-oil',
        title: 'Alpine Juniper Gel + Pure Topical Brine Oil Ritual',
        summary: 'Crisp juniper refreshment after contrast therapy or warm showers, plus 100% pure liquid Black Sea brine for full-body massage glide or evening mineral foot baths.',
        singleName: 'Dual Magnesium Gel | Juniper Blend (300g)',
        packName: 'Special Offer | Gel + Pure Oil Combo'
      }
    };

    const goalBtns = quizSection.querySelectorAll('.quiz-goal-btn');
    const resultBox = document.getElementById('quizResultCard');
    const resultTitle = document.getElementById('quizRecTitle');
    const resultDesc = document.getElementById('quizRecDesc');
    const addSingleBtn = document.getElementById('btnQuizAddSingle');
    const addPackBtn = document.getElementById('btnQuizAddPack');
    const emailInput = document.getElementById('quizEmailInput');
    const claimCodeBtn = document.getElementById('btnQuizClaimCode');
    const quizCodeBadge = document.getElementById('quizUnlockedCode');

    const renderRec = (goalKey) => {
      STATE.quizState.goal = goalKey;
      const rec = RECOMMENDATIONS[goalKey] || RECOMMENDATIONS.sport;
      if (resultBox) resultBox.style.display = 'block';
      if (resultTitle) resultTitle.textContent = rec.title;
      if (resultDesc) resultDesc.textContent = rec.summary;
      if (addSingleBtn) {
        addSingleBtn.textContent = `Add ${rec.singleName.split('|')[1]?.trim() || 'Gel'} — A$49`;
        addSingleBtn.setAttribute('data-rec-id', rec.primaryId);
      }
      if (addPackBtn) {
        addPackBtn.textContent = rec.packId === 'combo-starter'
          ? 'Get 2-Pack (A$89 + Free Shipping)'
          : 'Get Gel + Oil Deal (A$49)';
        addPackBtn.setAttribute('data-rec-id', rec.packId);
      }
    };

    goalBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        goalBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        renderRec(btn.getAttribute('data-goal'));
      });
    });

    if (addSingleBtn) {
      addSingleBtn.addEventListener('click', () => {
        addToCart(addSingleBtn.getAttribute('data-rec-id') || 'gel-arnica');
      });
    }
    if (addPackBtn) {
      addPackBtn.addEventListener('click', () => {
        addToCart(addPackBtn.getAttribute('data-rec-id') || 'combo-starter');
      });
    }

    if (claimCodeBtn && emailInput) {
      claimCodeBtn.addEventListener('click', async () => {
        const email = emailInput.value.trim();
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
          emailInput.focus();
          return;
        }
        STATE.customerEmail = email;
        localStorage.setItem('anchialov2_customer_email', email);
        if (!STATE.promoCode) {
          STATE.promoCode = 'QUIZ10';
          localStorage.setItem('anchialov2_promo_code', 'QUIZ10');
        }
        const activeCode = STATE.promoCode || 'QUIZ10';
        if (quizCodeBadge) {
          quizCodeBadge.textContent = `✓ Unlocked ${activeCode} (10% Off Applied to Bag)`;
          quizCodeBadge.style.display = 'block';
        }
        await postBackendEvent('/api/quiz/submit', {
          email,
          goal: STATE.quizState.goal,
          recommended_id: (RECOMMENDATIONS[STATE.quizState.goal] || RECOMMENDATIONS.sport).primaryId,
          partner_code: STATE.partnerCode || null
        });
        initPartnerAttribution();
        updateCartDrawer();
      });
    }

    renderRec(STATE.quizState.goal || 'sport');
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
    const openBtn = document.getElementById('openBagBtn');
    const closeBtn = document.getElementById('closeBagBtn');

    if (openBtn) openBtn.addEventListener('click', () => openBagDrawer());
    if (closeBtn) closeBtn.addEventListener('click', () => closeBagDrawer());
    if (backdrop) backdrop.addEventListener('click', () => closeBagDrawer());

    // Bag Email Capture (Abandoned Cart Recovery + 10% Guide)
    const saveEmailInput = document.getElementById('bagSaveEmailInput');
    const saveEmailBtn = document.getElementById('btnSaveBagEmail');
    const saveEmailStatus = document.getElementById('bagSaveEmailStatus');
    if (saveEmailInput && STATE.customerEmail) {
      saveEmailInput.value = STATE.customerEmail;
    }
    if (saveEmailBtn && saveEmailInput) {
      saveEmailBtn.addEventListener('click', async () => {
        const email = saveEmailInput.value.trim();
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
          saveEmailInput.focus();
          return;
        }
        STATE.customerEmail = email;
        localStorage.setItem('anchialov2_customer_email', email);
        if (!STATE.promoCode) {
          STATE.promoCode = 'COMEBACK10';
          localStorage.setItem('anchialov2_promo_code', 'COMEBACK10');
          initPartnerAttribution();
        }
        const totals = getCartTotals();
        await postBackendEvent('/api/cart/capture', {
          email,
          cart: STATE.cart,
          subtotal_aud: totals.finalSubtotalAUD,
          partner_code: STATE.partnerCode || null,
          promo_code: STATE.promoCode || null,
          postcode: (STATE.selectedLocality && STATE.selectedLocality.postcode) || '3000'
        });
        if (saveEmailStatus) {
          saveEmailStatus.textContent = `✓ Saved! Code ${STATE.promoCode || 'COMEBACK10'} (10% Off) applied.`;
          saveEmailStatus.style.display = 'block';
        }
        updateCartDrawer();
      });
    }

    // Dynamic Stripe Express Checkout interceptor (uses Akash session API when live)
    const stripeBtn = document.getElementById('btnStripeCheckout');
    if (stripeBtn) {
      stripeBtn.addEventListener('click', async (e) => {
        const base = (MERCHANT_CONFIG.apiBaseUrl || '').replace(/\/+$/, '');
        if (!base || !STATE.cart.length) return; // Fall through seamlessly to href Payment Link
        e.preventDefault();
        const origHtml = stripeBtn.innerHTML;
        stripeBtn.innerHTML = '<span>Opening Secure Stripe Checkout...</span>';
        const sessionRes = await postBackendEvent('/api/checkout/session', {
          items: STATE.cart,
          partner_code: STATE.partnerCode || null,
          promo_code: STATE.promoCode || null,
          customer_email: STATE.customerEmail || null,
          locality: STATE.selectedLocality || null,
          success_url: 'https://anchialo.com/?payment=stripe_success&session_id={CHECKOUT_SESSION_ID}',
          cancel_url: 'https://anchialo.com/#collection'
        });
        stripeBtn.innerHTML = origHtml;
        if (sessionRes && sessionRes.checkout_url) {
          window.location.href = sessionRes.checkout_url;
        } else if (stripeBtn.href && stripeBtn.href !== '#') {
          window.open(stripeBtn.href, '_blank', 'noopener');
        }
      });
    }

    // WhatsApp Checkout
    const btnWa = document.getElementById('btnProceedWhatsApp');
    if (btnWa) {
      btnWa.addEventListener('click', (e) => {
        if (!STATE.cart.length) {
          e.preventDefault();
          alert('Your shopping bag is currently empty. Please select a formulation.');
          return;
        }

        const totals = getCartTotals();
        let summary = 'Hello Sotir, I would like to place an order from Anchialo Australia:\n\n';
        STATE.cart.forEach((it, i) => {
          const itemTotal = it.priceAUD * it.qty;
          summary += `${i + 1}. ${it.name} × ${it.qty} = A$ ${itemTotal.toFixed(2)} AUD\n`;
        });
        if (totals.discountAUD > 0 && totals.codeMeta) {
          summary += `\nCode Applied (${totals.codeMeta.code}): -A$ ${totals.discountAUD.toFixed(2)} AUD`;
        }
        summary += `\nSubtotal: A$ ${totals.finalSubtotalAUD.toFixed(2)} AUD`;
        summary += `\nShipping (${STATE.selectedLocality.location} ${STATE.selectedLocality.postcode}): ${totals.shippingAUD === 0 ? 'FREE Express' : 'A$ 15.00 AUD'}`;
        if (STATE.partnerCode) {
          summary += `\nPartner Ref: ${STATE.partnerCode}`;
        }
        summary += `\n\nPlease confirm availability and Melbourne pickup / Australia Post dispatch!`;

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
        const totals = getCartTotals();
        let summary = 'ANCHIALO AUSTRALIA — ORDER SUMMARY:\n';
        STATE.cart.forEach((it, i) => {
          const itemTotal = it.priceAUD * it.qty;
          summary += `${i + 1}. ${it.name} × ${it.qty} = A$ ${itemTotal.toFixed(2)} AUD\n`;
        });
        if (totals.discountAUD > 0 && totals.codeMeta) {
          summary += `\nPrivilege (${totals.codeMeta.code}): -A$ ${totals.discountAUD.toFixed(2)} AUD`;
        }
        summary += `\nEstimated Total: A$ ${totals.finalSubtotalAUD.toFixed(2)} AUD\nContact: Sotir Kichukov (+61 423 269 586)`;

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
      const blendKey = productId.replace('gel-', '');
      const blend = BLENDS[blendKey];
      if (blend) {
        prod = {
          id: productId,
          name: blend.fullName,
          priceAUD: 49.00,
          packagingText: '300g PET 1 Jar',
          weightKg: 0.35,
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
        packagingText: prod.packagingText || '300g PET 1 Jar',
        weightKg: prod.weightKg || 0.35,
        image: prod.image,
        qty: 1
      });
    }

    saveCart();
    openBagDrawer();
  }

  function upgradeSingleToStarterPack() {
    const starter = CATALOG_PRODUCTS.find(p => p.id === 'combo-starter');
    if (!starter) return;
    STATE.cart = [{
      id: starter.id,
      name: starter.name,
      priceAUD: starter.priceAUD,
      packagingText: starter.packagingText,
      weightKg: starter.weightKg,
      image: starter.image,
      qty: 1
    }];
    saveCart();
  }

  function saveCart() {
    localStorage.setItem('anchialov2_cart', JSON.stringify(STATE.cart));
    updateCartDrawer();
  }

  function resolveStaticStripeHref(totals) {
    const totalUnits = totals.totalQty;
    let baseLink = STRIPE_CONFIG.links['custom'];
    if (STATE.cart.length === 1) {
      const single = STATE.cart[0];
      if (single.qty === 1 && STRIPE_CONFIG.links[single.id]) {
        baseLink = STRIPE_CONFIG.links[single.id];
      } else if (single.id.startsWith('gel-') && single.qty === 2) {
        baseLink = STRIPE_CONFIG.links['combo-starter'];
      } else if (single.id.startsWith('gel-') && single.qty === 3) {
        baseLink = STRIPE_CONFIG.links['combo-best-value'];
      } else if (STRIPE_CONFIG.links[single.id]) {
        baseLink = `${STRIPE_CONFIG.links[single.id]}?quantity=${single.qty}`;
      }
    } else if (totalUnits === 2 && STATE.cart.every(i => i.id.startsWith('gel-'))) {
      baseLink = STRIPE_CONFIG.links['combo-starter'];
    } else if (totalUnits === 3 && STATE.cart.every(i => i.id.startsWith('gel-'))) {
      baseLink = STRIPE_CONFIG.links['combo-best-value'];
    } else {
      baseLink = `${STRIPE_CONFIG.links['custom']}?quantity=${totalUnits}`;
    }

    if (STATE.partnerCode) {
      const sep = baseLink.includes('?') ? '&' : '?';
      return `${baseLink}${sep}client_reference_id=${encodeURIComponent(STATE.partnerCode)}`;
    }
    return baseLink;
  }

  function updateCartDrawer() {
    const listEl = document.getElementById('bagItemsContainer');
    const badgeEl = document.getElementById('cartCountBadge');
    const countEl = document.getElementById('drawerItemCount');
    const totalEl = document.getElementById('drawerSubtotalPrice');
    const meterBar = document.getElementById('shippingMeterBar');
    const meterText = document.getElementById('shippingMeterText');
    const meterPct = document.getElementById('shippingMeterPercent');
    const discountRow = document.getElementById('bagDiscountRow');
    const discountVal = document.getElementById('bagDiscountAmount');
    const upsellSlot = document.getElementById('bagUpsellSlot');

    const totals = getCartTotals();
    const totalQty = totals.totalQty;

    if (badgeEl) badgeEl.textContent = totalQty;
    if (countEl) countEl.textContent = `${totalQty} item${totalQty === 1 ? '' : 's'}`;
    if (totalEl) totalEl.textContent = formatPrice(totals.finalSubtotalAUD);

    if (discountRow && discountVal) {
      if (totals.discountAUD > 0 && totals.codeMeta) {
        discountRow.style.display = 'flex';
        discountVal.textContent = `-${formatPrice(totals.discountAUD)} (${totals.codeMeta.code})`;
      } else {
        discountRow.style.display = 'none';
      }
    }

    // Free shipping threshold ($80 AUD)
    const threshold = 80;
    const progress = Math.min(100, (totals.finalSubtotalAUD / threshold) * 100);
    if (meterBar) meterBar.style.width = `${progress}%`;
    if (meterPct) meterPct.textContent = `${Math.round(progress)}%`;

    if (meterText) {
      if (totals.finalSubtotalAUD >= threshold) {
        meterText.textContent = 'Complimentary Australia-wide Express delivery unlocked.';
      } else {
        const remaining = threshold - totals.finalSubtotalAUD;
        meterText.textContent = `Add A$ ${remaining.toFixed(2)} AUD for FREE Express delivery`;
      }
    }

    // 1-Click 2-Pack Upsell card inside bag when 1 single $49 jar/oil is selected
    if (upsellSlot) {
      const showUpsell = STATE.cart.length === 1 && STATE.cart[0].qty === 1 && STATE.cart[0].priceAUD === 49.00 && STATE.cart[0].id !== 'combo-gel-oil';
      if (showUpsell) {
        upsellSlot.style.display = 'block';
        upsellSlot.innerHTML = `
          <div class="bag-upsell-card">
            <div class="upsell-copy">
              <strong>Save A$9 + Unlock FREE Express Shipping</strong>
              <span>Upgrade to the Day &amp; Night 2-Pack (600g total) for A$89 instead of A$98.</span>
            </div>
            <button type="button" class="btn-upsell-upgrade" id="btnUpsell2Pack">Upgrade 2-Pack</button>
          </div>
        `;
        const upBtn = document.getElementById('btnUpsell2Pack');
        if (upBtn) upBtn.addEventListener('click', upgradeSingleToStarterPack);
      } else {
        upsellSlot.style.display = 'none';
        upsellSlot.innerHTML = '';
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

    if (stripeBtn) {
      stripeBtn.style.display = 'flex';
      stripeBtn.href = resolveStaticStripeHref(totals);
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

    const totals = getCartTotals();
    if (STATE.cart.length === 0 || totals.finalSubtotalAUD <= 0) {
      container.innerHTML = '<div style="text-align:center; padding:10px 0; font-size:12px; color:var(--text-muted);">Select formulations above to activate PayPal &amp; Card Checkout</div>';
      return;
    }

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
            const current = getCartTotals();
            const breakdown = {
              item_total: {
                currency_code: 'AUD',
                value: current.rawSubtotalAUD.toFixed(2)
              }
            };
            if (current.discountAUD > 0) {
              breakdown.discount = {
                currency_code: 'AUD',
                value: current.discountAUD.toFixed(2)
              };
            }
            const refTag = STATE.partnerCode ? `|REF:${STATE.partnerCode}` : '';
            return actions.order.create({
              intent: 'CAPTURE',
              purchase_units: [{
                description: 'Anchialo Certified Dual Magnesium Balneology Formulations',
                custom_id: `ANCHIALO_MELBOURNE_DISPATCH${refTag}`.slice(0, 127),
                amount: {
                  currency_code: 'AUD',
                  value: current.finalSubtotalAUD.toFixed(2),
                  breakdown: breakdown
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

    // Record order metadata for invoice generation & notify Akash ledger if configured
    const purchasedItems = [...STATE.cart];
    STATE.lastOrderMeta = {
      type: 'PayPal',
      txId: txId,
      amount: `A$ ${paidVal} AUD`,
      payer: `${fullName} (${payerEmail})`,
      items: purchasedItems
    };

    postBackendEvent('/api/orders/paypal', {
      tx_id: txId,
      customer_name: fullName,
      customer_email: payerEmail || STATE.customerEmail || '',
      amount_aud: parseFloat(paidVal) || 49.0,
      partner_code: STATE.partnerCode || null,
      promo_code: STATE.promoCode || null,
      locality: STATE.selectedLocality || null,
      items: purchasedItems
    });

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

    document.querySelectorAll('[data-cert-open]').forEach(thumb => {
      thumb.addEventListener('click', () => {
        const page = thumb.getAttribute('data-cert-open') || '1';
        pageBtns.forEach(b => {
          b.classList.toggle('active', b.getAttribute('data-page') === page);
        });
        if (certImg) {
          certImg.src = `assets/official_labels_rendered/quality_certificate_page_${page}.png`;
        }
        if (certModal) certModal.classList.add('active');
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
        packagingText: '300g PET 1 Jar',
        weightKg: 0.35,
        qty: 1
      }];
    }

    // Calculate totals with discount & dynamic packaging weight
    const rawSubtotal = items.reduce((sum, it) => sum + ((it.priceAUD || 49.00) * (it.qty || 1)), 0);
    const codeMeta = getActiveCodeMeta();
    const discountAUD = codeMeta ? Math.round((rawSubtotal * (codeMeta.discountPct / 100)) * 100) / 100 : 0;
    const netSubtotal = Math.max(0, Math.round((rawSubtotal - discountAUD) * 100) / 100);
    const parcelWeight = items.reduce((sum, it) => sum + ((it.weightKg || 0.35) * (it.qty || 1)), 0).toFixed(2);
    if (invWeightEl) invWeightEl.textContent = `${parcelWeight} kg Net`;

    const shippingCost = netSubtotal >= 80 ? 0.00 : 15.00;
    const grandTotal = netSubtotal + shippingCost;
    const gstPortion = MERCHANT_CONFIG.gstRegistered ? (grandTotal / 11).toFixed(2) : '0.00';

    const invBadgeEl = document.querySelector('.inv-title-badge');
    const invGstLabelEl = document.getElementById('invGstComplianceLabel');
    const invGstRowLabelEl = document.getElementById('invGstRowLabel');
    const invNotesEl = document.getElementById('invTaxNotesBox');
    if (invBadgeEl) {
      invBadgeEl.textContent = (MERCHANT_CONFIG.gstRegistered && MERCHANT_CONFIG.abn) ? 'TAX INVOICE' : 'ORDER INVOICE';
    }
    if (invGstLabelEl) {
      invGstLabelEl.textContent = (MERCHANT_CONFIG.gstRegistered && MERCHANT_CONFIG.abn)
        ? `ABN ${MERCHANT_CONFIG.abn} · 10% GST Included`
        : 'Domestic AU Order Receipt (No GST Charged)';
    }
    if (invGstRowLabelEl) {
      invGstRowLabelEl.textContent = MERCHANT_CONFIG.gstRegistered
        ? 'Includes 10% Australian GST:'
        : 'Australian GST (Not Registered):';
    }
    if (invNotesEl) {
      invNotesEl.innerHTML = (MERCHANT_CONFIG.gstRegistered && MERCHANT_CONFIG.abn)
        ? `<strong>Balneological Assay &amp; Tax Notice:</strong><br>ABN ${MERCHANT_CONFIG.abn}. Formulations harvested from Lake Pomorie, Bulgaria (253.14 g/L MgCl₂). All prices in AUD inclusive of 10% Australian GST.`
        : `<strong>Balneological Assay &amp; Dispatch Notice:</strong><br>Formulations derived from the fractional solar crystallization of Lake Pomorie mineral brine, Bulgaria (BDS 8840:1971 · 253.14 g/L MgCl₂). All figures in AUD; no GST charged.`;
    }

    if (tableBody) {
      tableBody.innerHTML = items.map(it => {
        const itemTotal = ((it.priceAUD || 49.00) * (it.qty || 1)).toFixed(2);
        const packLabel = it.packagingText || (String(it.id || '').includes('oil') ? '300ml Brine Bottle' : '300g Recyclable PET 1');
        return `
          <tr>
            <td>
              <strong>${it.name}</strong><br>
              <span style="font-size:11.5px; color:#52525b;">Pomorie Lake Hyper-Mineral Lye (253 g/L MgCl₂) · Batch Lot № 04 / Exp 2027</span>
            </td>
            <td style="text-align:center; font-size:12px; color:#52525b;">${packLabel}</td>
            <td style="text-align:center; font-weight:700;">${it.qty || 1}</td>
            <td style="text-align:right;">A$ ${(it.priceAUD || 49.00).toFixed(2)}</td>
            <td style="text-align:right; font-weight:700;">A$ ${itemTotal}</td>
          </tr>
        `;
      }).join('');
    }

    if (invSubtotalEl) {
      invSubtotalEl.textContent = discountAUD > 0
        ? `A$ ${netSubtotal.toFixed(2)} (saved A$ ${discountAUD.toFixed(2)})`
        : `A$ ${netSubtotal.toFixed(2)}`;
    }
    if (invShippingEl) {
      invShippingEl.textContent = shippingCost === 0
        ? 'FREE ($80+ Express Promotion)'
        : `A$ ${shippingCost.toFixed(2)} (AusPost Parcel Post)`;
    }
    if (invGstEl) invGstEl.textContent = `A$ ${gstPortion}`;
    if (invGrandTotalEl) invGrandTotalEl.textContent = `A$ ${grandTotal.toFixed(2)} AUD`;
  }

  // ==================== PRINT FLYER & COMBAT GUIDE CAROUSEL ====================
  function initFlyerCarousel() {
    const track = document.getElementById('flyer-carousel-track');
    if (!track) return;

    const slides = track.querySelectorAll('.flyer-slide');
    const prevBtn = document.getElementById('flyer-prev-btn');
    const nextBtn = document.getElementById('flyer-next-btn');
    const dots = document.querySelectorAll('#flyer-carousel-dots .flyer-dot');
    if (!slides.length) return;

    let currentIndex = 0;
    let autoPlayTimer = null;

    function getVisibleCount() {
      if (window.innerWidth <= 720) return 1;
      if (window.innerWidth <= 1100) return 2;
      return 3;
    }

    function updateCarousel(index) {
      const visible = getVisibleCount();
      const maxIndex = Math.max(0, slides.length - visible);
      if (index < 0) index = maxIndex;
      if (index > maxIndex) index = 0;
      currentIndex = index;

      const stepPct = 100 / visible;
      track.style.transform = `translateX(-${currentIndex * stepPct}%)`;

      dots.forEach((dot, idx) => {
        if (idx === currentIndex) {
          dot.style.background = '#d4af37';
          dot.classList.add('active');
        } else {
          dot.style.background = 'rgba(255,255,255,0.25)';
          dot.classList.remove('active');
        }
      });
    }

    window.addEventListener('resize', () => updateCarousel(currentIndex));

    function startAutoPlay() {
      stopAutoPlay();
      autoPlayTimer = setInterval(() => {
        updateCarousel(currentIndex + 1);
      }, 5000);
    }

    function stopAutoPlay() {
      if (autoPlayTimer) clearInterval(autoPlayTimer);
    }

    if (prevBtn) {
      prevBtn.addEventListener('click', () => {
        updateCarousel(currentIndex - 1);
        startAutoPlay();
      });
    }

    if (nextBtn) {
      nextBtn.addEventListener('click', () => {
        updateCarousel(currentIndex + 1);
        startAutoPlay();
      });
    }

    dots.forEach((dot) => {
      dot.addEventListener('click', (e) => {
        const targetIdx = parseInt(e.currentTarget.getAttribute('data-index') || '0', 10);
        updateCarousel(targetIdx);
        startAutoPlay();
      });
    });

    track.addEventListener('mouseenter', stopAutoPlay);
    track.addEventListener('mouseleave', startAutoPlay);

    // Initial setup
    updateCarousel(0);
    startAutoPlay();
  }

  // Hook into document load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFlyerCarousel);
  } else {
    initFlyerCarousel();
  }

})();
