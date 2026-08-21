/* Shared sub-page behaviour: scroll reveals driven by live geometry so lazy
   images, resizes and anchor jumps can never leave a section invisible. */
(function () {
  'use strict';
  var els = Array.prototype.slice.call(document.querySelectorAll('.reveal'));
  if (!els.length) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    els.forEach(function (el) { el.classList.add('in'); });
    return;
  }
  var pending = els, queued = false;
  var sweep = function () {
    queued = false;
    var line = window.innerHeight * 0.92;
    for (var i = pending.length - 1; i >= 0; i--) {
      if (pending[i].getBoundingClientRect().top < line) {
        pending[i].classList.add('in');
        pending.splice(i, 1);
      }
    }
  };
  var request = function () {
    if (queued || !pending.length) return;
    queued = true;
    requestAnimationFrame(sweep);
  };
  window.addEventListener('scroll', request, { passive: true });
  window.addEventListener('resize', request);
  window.addEventListener('load', request);
  sweep();
})();

/* ---------- Meta Pixel: Lead events on contact CTAs ---------- */
/* Fires a standard `Lead` event when a visitor clicks a WhatsApp / phone /
   email link on any sub-page. Safely no-ops if the pixel isn't present. */
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
  window.smxLead = lead;
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
