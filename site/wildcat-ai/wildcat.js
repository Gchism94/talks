/* Progressive enhancement: without JavaScript, all audience sections remain readable. */
(() => {
  const bar = document.querySelector('.audience-tabs');
  if (!bar) return;
  const tabs = [...bar.querySelectorAll('[data-audience]')];
  const panels = tabs.map(tab => document.getElementById(tab.dataset.audience));
  bar.setAttribute('role', 'tablist');
  document.querySelector('.audience-panels').classList.add('is-tabbed');
  function select(index, focus = false) {
    const changed = panels[index].hidden;
    tabs.forEach((tab, i) => {
      tab.setAttribute('aria-selected', String(i === index));
      tab.tabIndex = i === index ? 0 : -1;
      panels[i].hidden = i !== index;
      if (i !== index) panels[i].querySelectorAll('details[open]').forEach(detail => { detail.open = false; });
    });
    if (focus) tabs[index].focus();
    if (changed) document.dispatchEvent(new CustomEvent('wildcataudiencechange', {detail: {panel: panels[index]}}));
  }
  tabs.forEach((tab, index) => {
    tab.id = `tab-${tab.dataset.audience}`;
    tab.setAttribute('role', 'tab');
    tab.setAttribute('aria-controls', panels[index].id);
    panels[index].setAttribute('role', 'tabpanel');
    panels[index].setAttribute('aria-labelledby', tab.id);
    panels[index].tabIndex = 0;
    tab.addEventListener('click', event => { event.preventDefault(); select(index); });
    tab.addEventListener('keydown', event => {
      const next = {ArrowRight: (index + 1) % tabs.length, ArrowLeft: (index + tabs.length - 1) % tabs.length, Home: 0, End: tabs.length - 1}[event.key];
      if (next !== undefined) { event.preventDefault(); select(next, true); }
      if (event.key === ' ') { event.preventDefault(); select(index); }
    });
  });
  const fromHash = () => tabs.findIndex(tab => `#${tab.dataset.audience}` === location.hash);
  select(Math.max(0, fromHash()));
  function revealAudience() {
    const index = fromHash();
    if (index < 0) return;
    select(index);
    // Reveal a hidden panel before scrolling, and retain the audience choices above it.
    document.getElementById('people').scrollIntoView({block: 'start'});
  }
  document.querySelectorAll('a[href^="#"]').forEach(link => {
    if (bar.contains(link) || link.hasAttribute('data-goal')) return;
    if (!tabs.some(tab => `#${tab.dataset.audience}` === link.hash)) return;
    link.addEventListener('click', event => {
      event.preventDefault();
      if (location.hash === link.hash) revealAudience();
      else { location.hash = link.hash; revealAudience(); }
    });
  });
  addEventListener('hashchange', revealAudience);
  if (fromHash() >= 0) requestAnimationFrame(revealAudience);
})();

/* A link to personal-account details opens the disclosure before scrolling. */
(() => {
  const details = document.getElementById('personal-tools');
  if (!(details instanceof HTMLDetailsElement)) return;
  const reveal = () => {
    if (location.hash === '#personal-tools') details.open = true;
  };
  document.querySelectorAll('a[href="#personal-tools"]').forEach(link => {
    link.addEventListener('click', () => { details.open = true; });
  });
  addEventListener('hashchange', reveal);
  reveal();
})();

/* Keep the reading path oriented without changing the URL or recording activity. */
(() => {
  if (!('IntersectionObserver' in window)) return;
  const links = [...document.querySelectorAll('.site-header nav a[href^="#"]')];
  const sections = links.map(link => document.querySelector(link.getAttribute('href')));
  const visible = new Set();
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => entry.isIntersecting ? visible.add(entry.target) : visible.delete(entry.target));
    const current = sections.find(section => visible.has(section));
    links.forEach((link, index) => {
      if (sections[index] === current) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
  }, {rootMargin: '-120px 0px -45% 0px'});
  sections.forEach(section => observer.observe(section));
})();

/* A quiet campus heartbeat. Only decorative layers move; all copy stays still. */
(() => {
  const art = document.querySelector('.hero-art');
  const orbit = art?.querySelector('.art-orbit');
  const toggle = art?.querySelector('.motion-toggle');
  if (!orbit || !toggle || !orbit.animate || !('IntersectionObserver' in window)) return;

  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const printMedia = matchMedia('print');
  let inView = false;
  let userPaused = false;
  const core = orbit.querySelector('span:nth-child(4)');
  const animations = [core.animate([
    {transform: 'scale(1)', opacity: .96, offset: 0},
    {transform: 'scale(1.035)', opacity: 1, offset: .26},
    {transform: 'scale(1.01)', opacity: .98, offset: .43},
    {transform: 'scale(1.025)', opacity: 1, offset: .58},
    {transform: 'scale(1)', opacity: .96, offset: 1},
  ], {duration: 5600, iterations: Infinity, easing: 'ease-in-out'})];

  for (let i = 0; i < 2; i++) {
    const ripple = document.createElement('span');
    ripple.className = 'art-ripple';
    orbit.append(ripple);
    animations.push(ripple.animate([
      {transform: 'scale(.98)', opacity: 0, offset: 0},
      {transform: 'scale(1.12)', opacity: .42, offset: .22},
      {transform: 'scale(1.8)', opacity: 0, offset: 1},
    ], {duration: 8000, delay: i * 4000, iterations: Infinity, easing: 'ease-out'}));
  }
  // Local, gently changing contours suggest refraction around the heart.
  // Keep distortion separate from the core and every text-bearing layer.
  for (let i = 0; i < 2; i++) {
    const contour = document.createElement('span');
    contour.className = `art-distortion art-distortion-${i}`;
    orbit.append(contour);
    animations.push(contour.animate([
      {borderRadius: '48% 52% 51% 49% / 51% 48% 52% 49%', transform: `rotate(${i * 90}deg) scale(1)`, opacity: .34},
      {borderRadius: '52% 48% 49% 51% / 48% 53% 47% 52%', transform: `rotate(${i * 90 + 12}deg) scale(1.025, .985)`, opacity: .5},
      {borderRadius: '48% 52% 51% 49% / 51% 48% 52% 49%', transform: `rotate(${i * 90}deg) scale(1)`, opacity: .34},
    ], {duration: 11000 + i * 2500, iterations: Infinity, easing: 'ease-in-out'}));
  }
  animations.forEach(animation => animation.pause());

  function syncMotion() {
    const staticMode = reducedMotion.matches || printMedia.matches;
    toggle.hidden = staticMode;
    toggle.textContent = userPaused ? 'Resume motion' : 'Pause motion';
    animations.forEach(animation => {
      if (staticMode) animation.cancel();
      else if (inView && !document.hidden && !userPaused) animation.play();
      else animation.pause();
    });
  }
  toggle.addEventListener('click', () => {
    userPaused = !userPaused;
    syncMotion();
    document.dispatchEvent(new CustomEvent('wildcatmotionchange', {detail: {paused: userPaused}}));
  });
  const observer = new IntersectionObserver(([entry]) => {
    inView = entry.isIntersecting;
    syncMotion();
  }, {threshold: 0});
  observer.observe(art);
  reducedMotion.addEventListener('change', syncMotion);
  printMedia.addEventListener('change', syncMotion);
  document.addEventListener('visibilitychange', syncMotion);
  syncMotion();
})();

/* A translucent mouse halo and short click ripple, without replacing the native pointer. */
(() => {
  if (!Element.prototype.animate) return;
  const finePointer = matchMedia('(hover: hover) and (pointer: fine)');
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const layer = document.createElement('div');
  layer.className = 'pointer-effects';
  layer.setAttribute('aria-hidden', 'true');
  const halo = document.createElement('span');
  halo.className = 'pointer-halo';
  halo.hidden = true;
  layer.append(halo);
  document.body.append(layer);
  let userPaused = false;
  let frame = 0;
  let x = 0;
  let y = 0;
  const enabled = () => finePointer.matches && !reducedMotion.matches && !userPaused && !document.hidden;
  const darkSurface = target => Boolean(target instanceof Element && target.closest('.hero-stage, .pilot-section, .map-platform, .story-bridge, .studio-opening, .studio-manifesto, .journey-page .site-header, .studio-page .site-header'));
  function clear() {
    cancelAnimationFrame(frame);
    frame = 0;
    halo.hidden = true;
    layer.querySelectorAll('.pointer-pulse').forEach(pulse => {
      pulse.getAnimations().forEach(animation => animation.cancel());
      pulse.remove();
    });
  }
  document.addEventListener('pointermove', event => {
    if (!enabled() || event.pointerType !== 'mouse') { clear(); return; }
    x = event.clientX;
    y = event.clientY;
    halo.classList.toggle('on-dark', darkSurface(event.target));
    if (!frame) frame = requestAnimationFrame(() => {
      halo.style.transform = `translate3d(${x}px, ${y}px, 0) translate(-50%, -50%)`;
      halo.hidden = false;
      frame = 0;
    });
  }, {passive: true});
  document.addEventListener('click', event => {
    if (!enabled() || event.detail === 0 || event.pointerType !== 'mouse') return;
    const pulse = document.createElement('span');
    pulse.className = `pointer-pulse${darkSurface(event.target) ? ' on-dark' : ''}`;
    pulse.style.left = `${event.clientX}px`;
    pulse.style.top = `${event.clientY}px`;
    // Bound transient elements even during rapid repeated clicks.
    if (layer.querySelectorAll('.pointer-pulse').length >= 3) layer.querySelector('.pointer-pulse').remove();
    layer.append(pulse);
    const animation = pulse.animate([
      {transform: 'translate(-50%, -50%) scale(.6)', opacity: .55},
      {transform: 'translate(-50%, -50%) scale(2.2)', opacity: 0},
    ], {duration: 650, easing: 'cubic-bezier(.16,1,.3,1)'});
    animation.finished.then(() => pulse.remove(), () => pulse.remove());
  });
  document.addEventListener('pointerout', event => { if (!event.relatedTarget) clear(); });
  document.addEventListener('keydown', clear);
  document.addEventListener('visibilitychange', clear);
  window.addEventListener('blur', clear);
  window.addEventListener('scroll', clear, {passive: true});
  finePointer.addEventListener('change', clear);
  reducedMotion.addEventListener('change', clear);
  document.addEventListener('wildcatmotionchange', event => { userPaused = event.detail.paused; clear(); });
})();

/* Short cues explain a change or direction; reading content is never hidden on scroll. */
(() => {
  if (!Element.prototype.animate) return;
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const printMedia = matchMedia('print');
  const active = new Map();
  let userPaused = false;
  const enabled = () => !reducedMotion.matches && !printMedia.matches && !userPaused && !document.hidden;
  function clear() {
    active.forEach(animation => animation.cancel());
    active.clear();
  }
  function cue(element, frames, options) {
    if (!enabled() || !element) return;
    active.get(element)?.cancel();
    const animation = element.animate(frames, options);
    active.set(element, animation);
    const finish = () => { if (active.get(element) === animation) active.delete(element); };
    animation.finished.then(finish, finish);
  }
  document.addEventListener('wildcataudiencechange', event => {
    clear();
    event.detail.panel.querySelectorAll('.audience-promise, .audience-example').forEach((element, i) => {
      cue(element, [{opacity: .75, transform: 'translateY(5px)'}, {opacity: 1, transform: 'translateY(0)'}],
        {duration: 240, delay: i * 35, easing: 'ease-out'});
    });
  });
  document.querySelectorAll('.audience-depth, .responsibility, .footer-credit').forEach(details => {
    details.addEventListener('toggle', () => {
      const content = details.querySelector('.audience-depth-content, .responsibility-grid, .footer-credit-content');
      if (details.open) cue(content, [{opacity: .8, transform: 'translateY(3px)'}, {opacity: 1, transform: 'translateY(0)'}], {duration: 200, easing: 'ease-out'});
      else active.get(content)?.cancel();
    });
  });
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        observer.unobserve(entry.target);
        cue(entry.target, [
          {opacity: .6, transform: 'translateY(-3px)'},
          {opacity: 1, transform: 'translateY(3px)', offset: .6},
          {opacity: 1, transform: 'translateY(0)'},
        ], {duration: 850, easing: 'ease-in-out'});
      });
    }, {threshold: 1, rootMargin: '-130px 0px -30px 0px'});
    document.querySelectorAll('.system-map .map-flow > span').forEach(arrow => observer.observe(arrow));
  }
  reducedMotion.addEventListener('change', clear);
  printMedia.addEventListener('change', clear);
  document.addEventListener('visibilitychange', clear);
  document.addEventListener('wildcatmotionchange', event => { userPaused = event.detail.paused; clear(); });
})();

/* A small change in depth joins the opening to the next scene. Native scrolling stays native. */
(() => {
  const opening = document.querySelector('.journey-page .opening');
  if (!opening) return;
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const printMedia = matchMedia('print');
  let userPaused = false;
  let frame = 0;
  function draw() {
    frame = 0;
    document.body.classList.toggle('has-scrolled', scrollY > 40);
    const enabled = !reducedMotion.matches && !printMedia.matches && !userPaused;
    const progress = enabled ? Math.min(1, Math.max(0, -opening.getBoundingClientRect().top / opening.offsetHeight)) : 0;
    opening.style.setProperty('--orb-travel', `${progress * 85}px`);
    opening.style.setProperty('--orb-scale', String(1 + progress * .065));
    opening.style.setProperty('--copy-travel', `${progress * 22}px`);
  }
  function schedule() {
    if (!frame && !document.hidden) frame = requestAnimationFrame(draw);
  }
  addEventListener('scroll', schedule, {passive: true});
  addEventListener('resize', schedule, {passive: true});
  reducedMotion.addEventListener('change', schedule);
  printMedia.addEventListener('change', schedule);
  document.addEventListener('wildcatmotionchange', event => { userPaused = event.detail.paused; schedule(); });
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) { cancelAnimationFrame(frame); frame = 0; }
    else schedule();
  });
  schedule();
})();

/* A review notice, not authentication. Native dialog provides focus containment and Escape. */
(() => {
  const dialog = document.querySelector('.review-notice');
  const reopen = document.querySelector('.review-reopen');
  if (!(dialog instanceof HTMLDialogElement) || typeof dialog.showModal !== 'function') return;
  let returnFocus;
  function openNotice() {
    if (dialog.open) return;
    returnFocus = document.activeElement;
    dialog.showModal();
    document.body.classList.add('review-notice-open');
  }
  dialog.addEventListener('close', () => {
    document.body.classList.remove('review-notice-open');
    const target = returnFocus instanceof HTMLElement && returnFocus !== document.body
      ? returnFocus : document.querySelector('.hero-slide-link');
    target?.focus({preventScroll: true});
  });
  if (reopen) {
    reopen.hidden = false;
    reopen.addEventListener('click', openNotice);
  }
  openNotice();
})();
