/* ============================================================
   SHOWMAX GLOBAL — interactions & motion
   GSAP-driven with an IntersectionObserver fallback.
   ============================================================ */
(function () {
  'use strict';

  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var docEl = document.documentElement;
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var finePointer = window.matchMedia('(pointer: fine)').matches;
  var hasGSAP = typeof window.gsap !== 'undefined' && typeof window.ScrollTrigger !== 'undefined';

  if (reduced) docEl.classList.add('no-motion');
  if (hasGSAP && !reduced) {
    docEl.classList.add('gsap');
    gsap.registerPlugin(ScrollTrigger);
  } else {
    /* Nothing will animate the hero in, so release the pre-paint intro state now
       rather than waiting out the head script's safety timeout. */
    docEl.classList.remove('js-anim');
  }

  /* ---------- Preloader ---------- */
  (function preloader() {
    var seen = false;
    try { seen = sessionStorage.getItem('smx-seen') === '1'; } catch (e) {}
    if (reduced || seen) {
      docEl.classList.add('no-loader', 'loaded');
    } else {
      var done = function () {
        docEl.classList.add('loaded');
        try { sessionStorage.setItem('smx-seen', '1'); } catch (e) {}
      };
      window.addEventListener('load', function () { setTimeout(done, 450); });
      setTimeout(done, 2400); // hard cap
    }
  })();

  /* ---------- Scroll progress + nav state + scroll-top ---------- */
  (function scrollUI() {
    var bar = $('#progressBar'), nav = $('#nav'), topBtn = $('#scrollTop');
    var ticking = false;
    var update = function () {
      var y = window.scrollY;
      var h = docEl.scrollHeight - window.innerHeight;
      if (bar) bar.style.transform = 'scaleX(' + (h > 0 ? Math.min(y / h, 1) : 0) + ')';
      if (nav) nav.classList.toggle('scrolled', y > 40);
      if (topBtn) topBtn.classList.toggle('show', y > 600);
      ticking = false;
    };
    window.addEventListener('scroll', function () {
      if (!ticking) { requestAnimationFrame(update); ticking = true; }
    }, { passive: true });
    update();
    if (topBtn) topBtn.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: reduced ? 'auto' : 'smooth' });
    });
  })();

  /* ---------- Mobile menu ---------- */
  (function menu() {
    var ham = $('#hamburger'), menuEl = $('#menu');
    if (!ham || !menuEl) return;
    var setOpen = function (open) {
      document.body.classList.toggle('menu-open', open);
      ham.setAttribute('aria-expanded', String(open));
      menuEl.setAttribute('aria-hidden', String(!open));
      document.body.style.overflow = open ? 'hidden' : '';
    };
    ham.addEventListener('click', function () {
      setOpen(!document.body.classList.contains('menu-open'));
    });
    $$('a', menuEl).forEach(function (a) {
      a.addEventListener('click', function () { setOpen(false); });
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && document.body.classList.contains('menu-open')) setOpen(false);
    });
  })();

  /* ---------- Cursor ring ---------- */
  (function cursor() {
    var el = $('#cursor');
    if (!el || !finePointer || reduced) return;
    var x = -100, y = -100, cx = -100, cy = -100, visible = false;
    document.addEventListener('mousemove', function (e) {
      x = e.clientX; y = e.clientY;
      if (!visible) { el.classList.add('on'); visible = true; }
    }, { passive: true });
    document.addEventListener('mouseleave', function () { el.classList.remove('on'); visible = false; });
    var loop = function () {
      cx += (x - cx) * 0.16; cy += (y - cy) * 0.16;
      el.style.left = cx + 'px'; el.style.top = cy + 'px';
      requestAnimationFrame(loop);
    };
    loop();
    document.addEventListener('mouseover', function (e) {
      if (e.target.closest('a, button, .svc, .faq-q, input, select, textarea')) el.classList.add('grow');
    });
    document.addEventListener('mouseout', function (e) {
      if (e.target.closest('a, button, .svc, .faq-q, input, select, textarea')) el.classList.remove('grow');
    });
  })();

  /* ---------- Magnetic buttons ---------- */
  (function magnetic() {
    if (!finePointer || reduced) return;
    $$('.magnetic').forEach(function (btn) {
      var inner = $('.m-in', btn) || btn;
      var strength = 12;
      btn.addEventListener('pointermove', function (e) {
        var r = btn.getBoundingClientRect();
        var dx = (e.clientX - r.left - r.width / 2) / (r.width / 2);
        var dy = (e.clientY - r.top - r.height / 2) / (r.height / 2);
        inner.style.transform = 'translate(' + dx * strength + 'px,' + dy * strength * 0.7 + 'px)';
        inner.style.transition = 'transform .1s linear';
        inner.style.display = 'inline-flex';
        inner.style.alignItems = 'center';
        inner.style.gap = '.6rem';
      });
      btn.addEventListener('pointerleave', function () {
        inner.style.transition = 'transform .5s cubic-bezier(.22,.61,.21,1)';
        inner.style.transform = 'translate(0,0)';
      });
    });
  })();

  /* ---------- Hero video (desktop, after full load) ---------- */
  (function heroVideo() {
    var video = $('#heroVideo');
    if (!video) return;
    var conn = navigator.connection || {};
    var okToLoad = window.matchMedia('(min-width: 900px)').matches &&
      !reduced && !conn.saveData &&
      (typeof conn.effectiveType === 'undefined' || /4g/.test(conn.effectiveType));
    if (!okToLoad) return;
    var start = function () {
      /* VP9 first — roughly half the bytes of the H.264 copy, which stays as the
         fallback for browsers that cannot decode it. */
      [['assets/video/hero.webm', 'video/webm'], ['assets/video/hero.mp4', 'video/mp4']].forEach(function (s) {
        var el = document.createElement('source');
        el.src = s[0];
        el.type = s[1];
        video.appendChild(el);
      });
      video.load();
      var p = video.play();
      if (p && p.then) p.catch(function () {});
      video.addEventListener('playing', function () { video.classList.add('playing'); }, { once: true });
    };
    if (document.readyState === 'complete') setTimeout(start, 300);
    else window.addEventListener('load', function () { setTimeout(start, 300); });
    document.addEventListener('visibilitychange', function () {
      if (document.hidden) { video.pause(); }
      else if (video.classList.contains('playing')) { var p = video.play(); if (p && p.then) p.catch(function () {}); }
    });
  })();

  /* ---------- Gold dust particles ---------- */
  (function dust() {
    var canvas = $('#dust');
    if (!canvas || reduced || !window.matchMedia('(min-width: 720px)').matches) return;
    var ctx = canvas.getContext('2d');
    var w, h, parts = [], dpr = Math.min(window.devicePixelRatio || 1, 2);
    var COUNT = 46;
    var resize = function () {
      var r = canvas.parentElement.getBoundingClientRect();
      w = r.width; h = r.height;
      canvas.width = w * dpr; canvas.height = h * dpr;
      canvas.style.width = w + 'px'; canvas.style.height = h + 'px';
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    var mk = function () {
      return {
        x: Math.random() * w, y: h + Math.random() * h * 0.3,
        r: 0.6 + Math.random() * 1.7,
        vy: 0.12 + Math.random() * 0.4,
        vx: (Math.random() - 0.5) * 0.14,
        o: 0.12 + Math.random() * 0.5,
        tw: Math.random() * Math.PI * 2
      };
    };
    resize();
    for (var i = 0; i < COUNT; i++) { var p = mk(); p.y = Math.random() * h; parts.push(p); }
    window.addEventListener('resize', resize);
    var running = true;
    document.addEventListener('visibilitychange', function () { running = !document.hidden; if (running) tick(); });
    var tick = function () {
      if (!running) return;
      ctx.clearRect(0, 0, w, h);
      for (var i = 0; i < parts.length; i++) {
        var p = parts[i];
        p.y -= p.vy; p.x += p.vx; p.tw += 0.02;
        if (p.y < -8) { parts[i] = mk(); continue; }
        var a = p.o * (0.6 + 0.4 * Math.sin(p.tw));
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(245, 203, 31,' + a.toFixed(3) + ')';
        ctx.fill();
      }
      requestAnimationFrame(tick);
    };
    tick();
  })();

  /* ---------- Hero mouse parallax (chips + media) ---------- */
  (function heroParallax() {
    if (!finePointer || reduced) return;
    var hero = $('.hero');
    if (!hero) return;
    var chips = $$('.chip', hero);
    var media = $('.hero-media', hero);
    var rx = 0, ry = 0, tx = 0, ty = 0;
    hero.addEventListener('pointermove', function (e) {
      var r = hero.getBoundingClientRect();
      tx = (e.clientX - r.left) / r.width - 0.5;
      ty = (e.clientY - r.top) / r.height - 0.5;
    }, { passive: true });
    var loop = function () {
      rx += (tx - rx) * 0.05; ry += (ty - ry) * 0.05;
      chips.forEach(function (c) {
        var d = parseFloat(c.getAttribute('data-depth') || '20');
        c.style.marginLeft = (rx * d) + 'px';
        c.style.marginTop = (ry * d) + 'px';
      });
      if (media) media.style.transform = 'translate(' + (rx * -14) + 'px,' + (ry * -10) + 'px) scale(1.045)';
      requestAnimationFrame(loop);
    };
    loop();
  })();

  /* ---------- Service card spotlight + tilt ---------- */
  (function cardFx() {
    if (!finePointer || reduced) return;
    $$('.svc').forEach(function (card) {
      card.addEventListener('pointermove', function (e) {
        var r = card.getBoundingClientRect();
        var px = ((e.clientX - r.left) / r.width) * 100;
        var py = ((e.clientY - r.top) / r.height) * 100;
        card.style.setProperty('--mx', px + '%');
        card.style.setProperty('--my', py + '%');
        var rx = ((e.clientY - r.top) / r.height - 0.5) * -4;
        var ry = ((e.clientX - r.left) / r.width - 0.5) * 5;
        card.style.transform = 'translateY(-8px) perspective(900px) rotateX(' + rx + 'deg) rotateY(' + ry + 'deg)';
      });
      card.addEventListener('pointerleave', function () {
        card.style.transform = '';
      });
    });
  })();

  /* ---------- Reveals, parallax, counters, process rail ---------- */
  var counters = $$('.cnt');
  var countTo = function (el) {
    if (el.__done) return;
    el.__done = true;
    var target = parseInt(el.getAttribute('data-to'), 10) || 0;
    var t0 = null, dur = 1400;
    var step = function (ts) {
      if (!t0) t0 = ts;
      var k = Math.min((ts - t0) / dur, 1);
      k = 1 - Math.pow(1 - k, 4); // ease-out-quart
      el.textContent = Math.round(target * k);
      if (k < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  };

  /* Reveals and counters are driven by a live-geometry sweep rather than cached
     ScrollTrigger positions. Reading getBoundingClientRect at sweep time keeps them
     correct through lazy-loaded images, orientation changes and mobile URL-bar resizes,
     and the "top is above the trigger line" test also catches elements the reader
     jumped straight past via an anchor link. GSAP only supplies the motion. */
  (function revealSweep() {
    var pending = $$('[data-rev]');
    var pendingCounters = counters.slice();
    if (!pending.length && !pendingCounters.length) return;

    var show = function (batch) {
      if (hasGSAP && !reduced) {
        gsap.fromTo(batch,
          { y: 40, opacity: 0, filter: 'blur(8px)' },
          { y: 0, opacity: 1, filter: 'blur(0px)', duration: 1.05, stagger: 0.09, ease: 'power3.out', overwrite: true,
            onComplete: function () { batch.forEach(function (el) { el.style.filter = ''; }); } });
      }
      batch.forEach(function (el) { el.classList.add('in'); });
    };

    if (reduced) {
      show(pending); pending = [];
      pendingCounters.forEach(function (el) { el.textContent = el.getAttribute('data-to'); el.__done = true; });
      return;
    }

    var queued = false;
    var sweep = function () {
      queued = false;
      var line = window.innerHeight * 0.92, batch = [], i, r;
      for (i = pending.length - 1; i >= 0; i--) {
        if (pending[i].getBoundingClientRect().top < line) { batch.push(pending[i]); pending.splice(i, 1); }
      }
      if (batch.length) show(batch.reverse());
      for (i = pendingCounters.length - 1; i >= 0; i--) {
        r = pendingCounters[i].getBoundingClientRect();
        if (r.top < window.innerHeight * 0.85) { countTo(pendingCounters[i]); pendingCounters.splice(i, 1); }
      }
    };
    var request = function () {
      if (queued || (!pending.length && !pendingCounters.length)) return;
      queued = true;
      requestAnimationFrame(sweep);
    };
    window.addEventListener('scroll', request, { passive: true });
    window.addEventListener('resize', request);
    window.addEventListener('load', request);
    sweep();
  })();

  if (hasGSAP && !reduced) {
    /* Hero intro. The fromTo tweens render their start state immediately, so making the
       title visible here cannot flash it in its natural position first. */
    gsap.set('.hero-title', { opacity: 1 });
    var tl = gsap.timeline({ defaults: { ease: 'power4.out' }, delay: 0.15 });
    tl.fromTo('.hero-title .ht-in',
      { yPercent: 118, rotate: 3 },
      { yPercent: 0, rotate: 0, duration: 1.35, stagger: 0.1 }, 0.1)
      .fromTo('[data-hero-el]',
        { y: 26, opacity: 0, filter: 'blur(8px)' },
        { y: 0, opacity: 1, filter: 'blur(0px)', duration: 1, stagger: 0.12 }, 0.55)
      .fromTo('.chip',
        { y: 40, opacity: 0, scale: 0.92 },
        { y: 0, opacity: 1, scale: 1, duration: 1.2, stagger: 0.16, clearProps: 'transform' }, 0.9)
      .fromTo('.hero-scroll', { opacity: 0 }, { opacity: 1, duration: 0.8 }, 1.4);
    gsap.fromTo('.hero-media', { scale: 1.14 }, { scale: 1.045, duration: 2.6, ease: 'power3.out' });

    /* Keep scrubbed triggers honest once lazy images and fonts have settled */
    window.addEventListener('load', function () { ScrollTrigger.refresh(); });
    setTimeout(function () { ScrollTrigger.refresh(); }, 1800);

    /* Image parallax inside frames */
    $$('[data-plx]').forEach(function (img) {
      gsap.fromTo(img, { yPercent: -6 }, {
        yPercent: 6, ease: 'none',
        scrollTrigger: { trigger: img.closest('.about-frame') || img, start: 'top bottom', end: 'bottom top', scrub: true }
      });
    });
    /* Band background parallax */
    $$('[data-plx-band]').forEach(function (img) {
      gsap.fromTo(img, { yPercent: -10 }, {
        yPercent: 4, ease: 'none',
        scrollTrigger: { trigger: img.closest('.stats-band, .cta-band'), start: 'top bottom', end: 'bottom top', scrub: true }
      });
    });

    /* Process rail + step activation */
    var rail = $('#procRail');
    if (rail) {
      gsap.fromTo(rail, { scaleY: 0 }, {
        scaleY: 1, ease: 'none',
        scrollTrigger: { trigger: '#procSteps', start: 'top 72%', end: 'bottom 55%', scrub: 0.6 }
      });
    }
    $$('.proc-step').forEach(function (step) {
      ScrollTrigger.create({
        trigger: step, start: 'top 62%', end: 'bottom 30%',
        onToggle: function (self) { step.classList.toggle('on', self.isActive); }
      });
    });

    /* Marquee slight slowdown at rest is CSS-driven; nothing needed here */
  } else {
    /* -------- Fallback: no GSAP (or reduced motion) -------- */
    var rail2 = $('#procRail');
    if (rail2) rail2.style.transform = 'scaleY(1)';
    if (reduced || !('IntersectionObserver' in window)) {
      $$('.proc-step').forEach(function (el) { el.classList.add('on'); });
    } else {
      var io3 = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) { en.target.classList.toggle('on', en.isIntersecting); });
      }, { rootMargin: '-38% 0px -30% 0px' });
      $$('.proc-step').forEach(function (el) { io3.observe(el); });
    }
  }

  /* ---------- Services modal ---------- */
  var SERVICES = [
    { name: 'Branding & Advertisement',
      icon: '<svg viewBox="0 0 24 24" fill="none" stroke="#F5CB1F" stroke-width="1.5" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 3a17 17 0 010 18M5 7c4 2 10 2 14 0M5 17c4-2 10-2 14 0"/></svg>',
      long: 'Your brand is the first thing people judge and the last thing they forget. We build a complete visual identity \u2014 then turn it into advertising creative that actually sells, across print, social and digital.',
      includes: ['Custom logo design (primary + variations)', 'Colour palette & typography system', 'Complete brand guidelines document', 'Advertisement & campaign creatives (print + digital)', 'Social media profile & stationery kit'],
      ideal: 'new businesses, rebrands, and brands that need both an identity and ads that convert.' },
    { name: 'Digital Marketing',
      icon: '<svg viewBox="0 0 24 24" fill="none" stroke="#F5CB1F" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 17l5-5 4 4 8-8"/><path d="M15 8h5v5"/></svg>',
      long: "Impressions don't pay the bills \u2014 customers do. We build and manage paid campaigns engineered around one metric that matters: qualified leads at a cost that makes sense for your business.",
      includes: ['Google & Meta ad campaign setup', 'Audience research & targeting', 'Ad creative & copywriting', 'Conversion tracking & pixels', 'Weekly optimisation & reporting'],
      ideal: 'businesses that need a predictable, scalable flow of enquiries and sales.' },
    { name: 'Website & SEO',
      icon: '<svg viewBox="0 0 24 24" fill="none" stroke="#F5CB1F" stroke-width="1.5" stroke-linecap="round"><rect x="3" y="4" width="18" height="14" rx="2.5"/><path d="M3 8.5h18M7 21h10"/></svg>',
      long: 'A website should be your hardest-working salesperson. We design fast, mobile-first sites that look premium and convert \u2014 then optimise them to rank on Google so customers find you first.',
      includes: ['Custom responsive website design', 'Mobile & speed optimisation', 'On-page & technical SEO', 'Google Business Profile & local SEO', 'Analytics & search console setup'],
      ideal: "any business without a site, or one that looks dated and doesn't bring in leads." },
    { name: 'Social Media',
      icon: '<svg viewBox="0 0 24 24" fill="none" stroke="#F5CB1F" stroke-width="1.5" stroke-linecap="round"><circle cx="12" cy="12" r="3.2"/><path d="M12 2a10 10 0 00-7 17M12 22a10 10 0 007-17"/><circle cx="19" cy="5" r="2"/><circle cx="5" cy="19" r="2"/></svg>',
      long: 'Showing up consistently is what builds trust online. We plan, design and publish scroll-stopping content that keeps your brand active, recognisable and growing across every platform.',
      includes: ['Monthly content calendar', 'Post & reel design + captions', 'Hashtag & posting strategy', 'Community management & replies', 'Monthly growth reporting'],
      ideal: 'brands that want a professional, always-on presence without the daily effort.' },
    { name: 'Video Ads Creation',
      icon: '<svg viewBox="0 0 24 24" fill="none" stroke="#F5CB1F" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2.5" y="6.5" width="13" height="11" rx="2.5"/><path d="M15.5 11l6-3.2v8.4l-6-3.2z"/></svg>',
      long: 'Video is what stops the scroll and sells in seconds. We handle the whole pipeline \u2014 concept, script, shoot and edit \u2014 producing platform-ready video ads and reels designed to convert, not just to look pretty.',
      includes: ['Concept & scriptwriting', 'Short-form reels & video ads', 'Professional editing & motion graphics', 'Subtitles & platform-specific cuts', 'Hooks & thumbnails optimised for reach'],
      ideal: 'brands that want to grow on reels, run video ad campaigns, or launch a product with impact.' },
    { name: 'Content Strategy',
      icon: '<svg viewBox="0 0 24 24" fill="none" stroke="#F5CB1F" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16v12H8l-4 4z"/><path d="M8 9h8M8 12h5"/></svg>',
      long: 'Great content turns strangers into followers and followers into customers. We create content that educates, builds authority and quietly does your selling \u2014 while ranking on search at the same time.',
      includes: ['SEO blog articles & website copy', 'Reel & video scripts', 'Email & newsletter copy', 'Case studies & landing pages', 'Content calendar & topic research'],
      ideal: 'businesses that want to be seen as the expert in their field.' },
    { name: 'Brand Promotion',
      icon: '<svg viewBox="0 0 24 24" fill="none" stroke="#F5CB1F" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 11l18-5v12L3 13z"/><path d="M11.6 16.8a3 3 0 11-5.8-1.6"/></svg>',
      long: 'Sometimes you need a moment that gets everyone talking. We design launch and promotion campaigns \u2014 with the right influencers and PR \u2014 to put your brand in front of thousands of the right people, fast.',
      includes: ['Launch campaign strategy', 'Influencer identification & outreach', 'PR & media coordination', 'Giveaway & collaboration planning', 'Campaign performance tracking'],
      ideal: 'product launches, new openings, and brands ready for a visibility push.' },
    { name: 'UAE\u2013India Trade Facilitation',
      icon: '<svg viewBox="0 0 24 24" fill="none" stroke="#F5CB1F" stroke-width="1.5" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M12 3a15 15 0 010 18M12 3a15 15 0 000 18"/></svg>',
      long: 'With offices in Indore and Sharjah and the India\u2013UAE CEPA opening doors both ways, we help businesses cross the bridge confidently \u2014 from market research and brand localisation to finding the right partners and setting up your presence in the other market.',
      includes: ['India & UAE market research', 'Brand localisation for the target market', 'Partner & distributor identification', 'Business-setup & CEPA guidance', 'Bilingual marketing & go-to-market support'],
      ideal: 'Indian businesses entering the UAE, and UAE businesses entering India.' }
  ];
  var WA = 'https://wa.me/917024397999';
  var CHECK = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#F5CB1F" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg>';

  (function modal() {
    var overlay = $('#modalOverlay'), mBody = $('#modalBody'), closeBtn = $('#modalClose');
    if (!overlay || !mBody) return;
    var lastFocus = null;

    var esc = function (s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;'); };

    var open = function (i, page) {
      var s = SERVICES[i];
      if (!s) return;
      var waMsg = WA + '?text=' + encodeURIComponent("Hi Showmax Global, I'm interested in your " + s.name + ' service. Please share more details.');
      mBody.innerHTML =
        '<div class="modal-icon">' + s.icon + '</div>' +
        '<h3 class="modal-title" id="modalTitle">' + esc(s.name) + '</h3>' +
        '<p class="modal-desc">' + esc(s.long) + '</p>' +
        '<p class="modal-sub">What’s included</p>' +
        '<ul class="modal-list">' + s.includes.map(function (x) { return '<li>' + CHECK + '<span>' + esc(x) + '</span></li>'; }).join('') + '</ul>' +
        '<div class="modal-ideal"><strong>Ideal for:</strong> ' + esc(s.ideal) + '</div>' +
        '<div class="modal-actions"><a class="btn btn-gold" href="' + waMsg + '" target="_blank" rel="noopener">Enquire on WhatsApp <span class="ar">&rarr;</span></a>' +
        (page ? '<a class="btn btn-ghost" href="' + page + '">Read the full guide</a>' : '') +
        '<a class="btn btn-ghost" href="#contact" id="modalContact">Contact form</a></div>';
      overlay.classList.add('open');
      document.body.style.overflow = 'hidden';
      lastFocus = document.activeElement;
      closeBtn.focus();
      var mc = $('#modalContact');
      if (mc) mc.addEventListener('click', close);
    };
    var close = function () {
      overlay.classList.remove('open');
      document.body.style.overflow = '';
      if (lastFocus) lastFocus.focus();
    };
    $$('.svc').forEach(function (btn) {
      btn.addEventListener('click', function () {
        open(parseInt(btn.getAttribute('data-svc'), 10), btn.getAttribute('data-page'));
      });
    });
    closeBtn.addEventListener('click', close);
    overlay.addEventListener('click', function (e) { if (e.target === overlay) close(); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && overlay.classList.contains('open')) close();
      /* simple focus trap */
      if (e.key === 'Tab' && overlay.classList.contains('open')) {
        var focusables = $$('button, a, [tabindex]:not([tabindex="-1"])', overlay);
        if (!focusables.length) return;
        var first = focusables[0], last = focusables[focusables.length - 1];
        if (e.shiftKey && document.activeElement === first) { last.focus(); e.preventDefault(); }
        else if (!e.shiftKey && document.activeElement === last) { first.focus(); e.preventDefault(); }
      }
    });
  })();

  /* ---------- Pricing region toggle (INR / AED) ---------- */
  (function currency() {
    var toggle = $('.cur-toggle');
    if (!toggle) return;
    var amounts = $$('.pkg-price .amount');
    $$('button', toggle).forEach(function (btn) {
      btn.addEventListener('click', function () {
        var cur = btn.getAttribute('data-cur');
        $$('button', toggle).forEach(function (b) {
          var on = b === btn;
          b.classList.toggle('active', on);
          b.setAttribute('aria-selected', String(on));
        });
        amounts.forEach(function (el) {
          var next = el.getAttribute('data-' + cur);
          if (!next || el.textContent === next) return;
          el.classList.add('swap');
          setTimeout(function () { el.textContent = next; el.classList.remove('swap'); }, 200);
        });
      });
    });
  })();

  /* ---------- FAQ accordion ---------- */
  (function faq() {
    $$('.faq-q').forEach(function (q) {
      q.addEventListener('click', function () {
        var f = q.parentElement;
        var isOpen = f.classList.contains('open');
        $$('.faq').forEach(function (x) {
          x.classList.remove('open');
          var b = $('.faq-q', x); if (b) b.setAttribute('aria-expanded', 'false');
        });
        if (!isOpen) {
          f.classList.add('open');
          q.setAttribute('aria-expanded', 'true');
        }
      });
    });
  })();

  /* ---------- Contact form -> WhatsApp ---------- */
  (function form() {
    var form = $('#contactForm');
    if (!form) return;
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var name = form.name.value.trim(),
          phone = form.phone.value.trim(),
          email = form.email.value.trim(),
          service = form.service.value,
          message = form.message.value.trim();
      var ok = true;
      [['name', name], ['phone', phone], ['email', email]].forEach(function (p) {
        var el = form[p[0]];
        if (!p[1]) { el.classList.add('err'); ok = false; } else { el.classList.remove('err'); }
      });
      if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { form.email.classList.add('err'); ok = false; }
      if (!ok) return;
      var txt = 'New enquiry for Showmax Global%0A%0A' +
        'Name: ' + encodeURIComponent(name) + '%0A' +
        'Phone: ' + encodeURIComponent(phone) + '%0A' +
        'Email: ' + encodeURIComponent(email) + '%0A' +
        'Service: ' + encodeURIComponent(service || 'Not specified') + '%0A' +
        'Message: ' + encodeURIComponent(message || '—');
      window.open(WA + '?text=' + txt, '_blank');
      if (window.smxLead) window.smxLead('Contact form');
      var s = $('#formSuccess');
      if (s) {
        s.style.display = 'block';
        setTimeout(function () { s.style.display = 'none'; }, 6000);
      }
      form.reset();
    });
  })();

})();

/* ---------- Meta Pixel: Lead events on contact CTAs ---------- */
/* Fires a standard `Lead` event when a visitor takes a real contact action:
   submits the enquiry form, or clicks a WhatsApp / phone / email link.
   Safely no-ops if the pixel (window.fbq) isn't present. */
(function leadTracking() {
  'use strict';
  var lastAt = {};
  function lead(channel) {
    if (typeof window.fbq !== 'function') return;
    var now = Date.now();
    if (lastAt[channel] && now - lastAt[channel] < 1000) return; // de-dupe rapid repeats
    lastAt[channel] = now;
    window.fbq('track', 'Lead', { content_name: channel, content_category: 'contact' });
  }
  window.smxLead = lead; // let the contact-form handler report a Lead on success
  document.addEventListener('click', function (e) {
    var t = e.target;
    var a = t && t.closest ? t.closest('a[href]') : null;
    if (!a) return;
    var href = a.getAttribute('href') || '';
    if (/wa\.me|api\.whatsapp\.com/i.test(href)) lead('WhatsApp');
    else if (/^tel:/i.test(href)) lead('Phone call');
    else if (/^mailto:/i.test(href)) lead('Email');
  }, true);
})();
