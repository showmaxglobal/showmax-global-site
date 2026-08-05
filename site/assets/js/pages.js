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
