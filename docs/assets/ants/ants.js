'use strict';
(() => {
  const $ = (id) => document.getElementById(id);
  const slides = [...document.querySelectorAll('.slide')];
  let current = 0;
  const notes = $('notesDialog');
  const menu = $('menuDialog');
  const videos = [...document.querySelectorAll('video')];
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const pauses = [];
  // Reveal complete ideas, keeping the slide geometry and visual evidence fixed.
  const builds = new WeakMap();
  const revealStyle = document.createElement('style');
  revealStyle.textContent = `
    [data-reveal-hidden]{visibility:hidden;pointer-events:none}
    #counter small{display:block;font-size:12px;line-height:1.25}
    #revealAllBtn{white-space:nowrap}
    @media(max-width:520px){.nav-group{gap:5px}.nav #revealAllBtn{padding:7px;font-size:14px}}
    @media print{[data-reveal-hidden]{visibility:visible!important}#revealAllBtn{display:none}}
  `;
  document.head.append(revealStyle);
  const revealAll = document.createElement('button');
  revealAll.id = 'revealAllBtn';
  revealAll.textContent = 'Show all';
  revealAll.hidden = true;
  $('menuBtn').after(revealAll);
  function register(scope, groups) {
    groups = groups.map(group => group.filter(Boolean)).filter(group => group.length);
    if (groups.length > 1) builds.set(scope, { groups, visible: 1 });
  }
  function splitIdeas(element, ideas) {
    if (!element) return [];
    element.replaceChildren();
    return ideas.map((idea, i) => {
      const span = document.createElement('span');
      span.className = 'reveal-idea';
      span.innerHTML = idea;
      if (i) element.append(document.createElement('br'));
      element.append(span);
      return [span];
    });
  }
  function guideLines(scope, selector) {
    // The original SVG combines several independent connectors in one path.
    // Separate them so each label appears with its own connector.
    return [...scope.querySelectorAll(selector)].flatMap(path => {
      const segments = path.getAttribute('d').match(/[Mm][^Mm]*/g) || [];
      if (segments.length < 2) return [path];
      const lines = segments.map(segment => {
        const line = path.cloneNode(false);
        line.setAttribute('d', segment.trim());
        return line;
      });
      path.replaceWith(...lines);
      return lines;
    });
  }
  const leadIdeas = {
    'A mountain, many ant neighborhoods': ['Forest floor.', 'Sunny openings.', 'Dry country to the north.'],
    'The queen is not the foreman': ['The queen lays eggs.', 'The workers coordinate<br>the work.'],
    'From egg to adult': ['Egg → larva → pupa → adult', 'Workers tend the<br>growing generation.'],
    'When ants take wing': ['A male alate.', 'A queen alate.', 'A wingless worker.'],
    'Same species. Different bodies.': ['Small workers.', 'Big-headed majors.<br>One fire-ant colony.'],
    'Small ants, a larger web of life': ['Soil. Seeds. Birds.', 'Keep room for the neighbors<br>that connect them.']
  };
  const explanatory = new Set([
    'Ants that move the forest floor', 'Inside the ant colony',
    'Farming, about 66 million years ago', 'A chemical signal can also be a weapon',
    'A defense that costs a life', 'Can a trail choose itself?',
    'How many neighbors make a decision?', 'Small excavators, lasting changes',
    'A seed with a packed lunch', 'The leaves feed the fungus', 'Living ladders',
    'When recognition is disrupted'
  ]);
  slides.forEach(slide => {
    if (slide.classList.contains('section-break') || slide.dataset.time === 'Reference appendix') return;
    const title = slide.dataset.title;
    const panels = [...slide.querySelectorAll('.example-panel')];
    const scopes = panels.length ? panels : [slide];
    scopes.forEach(scope => {
      // Models, games and the seed sequence already expose information through
      // their own controls. Their controls must always remain operable.
      if (scope.querySelector('canvas, .head-game, #seedNext')) return;
      let groups = [];
      if (title === 'An ant, up close') {
        const paths = guideLines(scope, '.anatomy-board svg path');
        const labels = [...scope.querySelectorAll('.parts-label text')];
        const mobile = [...scope.querySelectorAll('.parts-mobile span')];
        groups = [[0, 1], [2, 3], [4, 5]].map(indices => indices.flatMap(i => [paths[i], labels[i], mobile[i]]));
      } else if (title === 'Two groups to get to know') {
        groups = [...scope.querySelectorAll('.species-pair article')].map(card => [...card.querySelectorAll('p:not(.latin):not(.photo-credit)')] );
      } else if (title === 'Pollen moves. Then seeds move.') {
        groups = [...scope.querySelectorAll('.ecology-pair figcaption')].map(caption => {
          const copy = document.createElement('span');
          while (caption.firstChild && caption.firstChild.nodeName !== 'A') copy.append(caption.firstChild);
          caption.prepend(copy);
          return [copy];
        });
      } else if (title === 'Plants can feed and house their guards') {
        groups = [...scope.querySelectorAll('.plant-trio figcaption')].map(caption => [caption]);
      } else if (scope.querySelector('.local-jobs, .ecology-lines, .home-actions')) {
        groups = [...scope.querySelectorAll('.local-jobs>li, .ecology-lines>li, .home-actions>li')].map(item => [item]);
      } else if (leadIdeas[title]) {
        groups = splitIdeas(scope.querySelector('.lead'), leadIdeas[title]);
        if (title === 'When ants take wing') {
          const paths = guideLines(scope, '.alate-board svg path');
          const labels = [...scope.querySelectorAll('.alate-board svg text')];
          groups.forEach((group, i) => group.push(paths[i], labels[i]));
        }
      } else if (explanatory.has(title)) {
        const lead = scope.querySelector('.lead');
        const cue = scope.querySelector('.watch-cue');
        if (scope.id === 'seedPhoto') {
          groups = splitIdeas(lead, ['The seed travels.', 'The ants eat the oily reward.']);
        } else if (title === 'The leaves feed the fungus' && !cue) {
          groups = splitIdeas(lead, ['Leaves are the growing medium.', 'The fungus is the crop.']);
        } else if (lead && cue) groups = [[lead], [cue]];
        else if (lead && scope.querySelector('.footnote')) groups = [[lead], []];
      } else if (title === 'A border can become a battlefield') {
        groups = [[scope.querySelector('.lead')], [scope.querySelector('.footnote')]];
      }
      if (groups.length > 1) {
        const final = groups[groups.length - 1];
        scope.querySelectorAll('.footnote').forEach(note => {
          if (!/©|CC BY|CC0/.test(note.textContent) && !groups.some(group => group.includes(note))) final.push(note);
        });
        if (title === 'When ants take wing') final.push(scope.querySelector('.watch-cue'));
        if (scope.id === 'homeLearning') final.push(scope.querySelector('.memory-card'));
        register(scope, groups);
      }
    });
  });
  function context() {
    const slide = slides[current];
    return slide.querySelector('.example-panel:not([hidden])') || slide;
  }
  function paintBuild(scope) {
    const build = builds.get(scope);
    if (!build) return;
    build.groups.forEach((group, i) => group.forEach(element => {
      const concealed = i >= build.visible;
      element.toggleAttribute('data-reveal-hidden', concealed);
      if (concealed) element.setAttribute('aria-hidden', 'true');
      else element.removeAttribute('aria-hidden');
      element.inert = concealed;
    }));
  }
  function updateBuildControls() {
    const build = builds.get(context());
    const hasMore = build && build.visible < build.groups.length;
    const canRewind = build && build.visible > 1;
    $('counter').textContent = (current + 1) + ' / ' + slides.length;
    if (build) {
      const status = document.createElement('small');
      status.textContent = 'Text ' + build.visible + ' / ' + build.groups.length;
      $('counter').append(status);
    }
    revealAll.hidden = !build;
    revealAll.textContent = hasMore ? 'Show all' : 'Build text';
    revealAll.setAttribute('aria-label', hasMore ? 'Show all text on this slide' : 'Restart text reveals on this slide');
    $('nextBtn').disabled = !hasMore && current === slides.length - 1;
    $('prevBtn').disabled = !canRewind && current === 0;
    $('nextBtn').setAttribute('aria-label', hasMore ? 'Show next point' : 'Next slide');
    $('nextBtn').title = hasMore ? 'Show next point' : 'Next slide';
    $('prevBtn').setAttribute('aria-label', canRewind ? 'Hide last point' : 'Previous slide');
    $('prevBtn').title = canRewind ? 'Hide last point' : 'Previous slide';
  }
  function changeBuild(visible) {
    const scope = context();
    const build = builds.get(scope);
    if (!build) return;
    build.visible = visible;
    paintBuild(scope);
    updateBuildControls();
    const text = build.groups[visible - 1].map(element => element.textContent.trim()).filter(Boolean).join('. ');
    $('slideAnnounce').textContent = 'Text ' + visible + ' of ' + build.groups.length + ': ' + text;
  }
  function forward() {
    const build = builds.get(context());
    if (build && build.visible < build.groups.length) changeBuild(build.visible + 1);
    else show(current + 1);
  }
  function backward() {
    const build = builds.get(context());
    if (build && build.visible > 1) changeBuild(build.visible - 1);
    else show(current - 1, true, true);
  }
  revealAll.onclick = () => {
    const build = builds.get(context());
    if (build) changeBuild(build.visible < build.groups.length ? build.groups.length : 1);
  };

  function pauseAll() {
    pauses.forEach((fn) => fn()); videos.forEach((video) => video.pause());
    document.querySelectorAll('.online-film iframe').forEach((frame) => {
      const host = frame.parentElement;
      frame.remove();
      host.querySelector('img').hidden = false;
      host.querySelector('.load-film').hidden = false;
    });
  }
  document.querySelectorAll('[data-view]').forEach((button) => {
    button.onclick = () => {
      pauseAll();
      const group = button.closest('.example-switch');
      group.querySelectorAll('[data-view]').forEach((b) => b.setAttribute('aria-pressed', String(b === button)));
      group.querySelectorAll('.example-panel').forEach((panel) => { panel.hidden = panel.id !== button.dataset.view; });
      updateBuildControls();
      // A canvas that was hidden now has its displayed dimensions.
      window.dispatchEvent(new Event('resize'));
    };
  });
  document.querySelectorAll('.load-film').forEach((button) => {
    button.onclick = () => {
      pauseAll();
      const host = button.closest('.online-film');
      const frame = document.createElement('iframe');
      frame.src = host.dataset.embed;
      frame.title = host.dataset.filmTitle;
      frame.allow = 'autoplay; fullscreen; picture-in-picture; encrypted-media';
      frame.referrerPolicy = 'strict-origin-when-cross-origin';
      frame.allowFullscreen = true;
      host.querySelector('img').hidden = true;
      button.hidden = true;
      host.append(frame);
    };
  });
  function show(index, updateHash = true, complete = false) {
    if (!Number.isFinite(index)) index = 0;
    index = Math.max(0, Math.min(slides.length - 1, index));
    pauseAll();
    current = index;
    slides.forEach((s, i) => { s.classList.toggle('active', i === index); s.inert = i !== index; });
    [slides[index], ...slides[index].querySelectorAll('.example-panel')].forEach(scope => {
      const build = builds.get(scope);
      if (build) build.visible = complete ? build.groups.length : 1;
      paintBuild(scope);
    });
    updateBuildControls();
    $('timing').textContent = slides[index].dataset.time;
    $('progressBar').style.width = ((index + 1) / slides.length * 100) + '%';
    $('slideAnnounce').textContent = 'Slide ' + (index + 1) + ': ' + slides[index].dataset.title;
    if (updateHash) history.replaceState(null, '', '#' + (index + 1));
    window.scrollTo(0, 0);
    if (slides[index].querySelector('#trailCanvas')) drawTrail();
    if (slides[index].querySelector('#quorumCanvas')) drawQuorum();
  }
  function openNotes() {
    if ($('notesBtn').hidden) return;
    $('notesTitle').textContent = (current + 1) + '. ' + slides[current].dataset.title;
    $('notesBody').innerHTML = slides[current].querySelector('.speaker-notes').innerHTML;
    pauseAll(); notes.showModal();
  }
  $('outline').replaceChildren();
  let outlineChapter = '', outlineGroup;
  slides.forEach((slide, i) => {
    if (slide.dataset.chapter !== outlineChapter) {
      outlineChapter = slide.dataset.chapter;
      const section = document.createElement('li');
      section.className = 'outline-section';
      const heading = document.createElement('h3');
      heading.textContent = outlineChapter;
      outlineGroup = document.createElement('ol');
      outlineGroup.className = 'outline-slides';
      section.append(heading, outlineGroup);
      $('outline').append(section);
    }
    const li = document.createElement('li'); const btn = document.createElement('button');
    const title = document.createElement('span'); const time = document.createElement('small');
    title.textContent = (i + 1) + '. ' + slide.dataset.title; time.textContent = slide.dataset.time;
    btn.append(title, time); btn.onclick = () => { menu.close(); show(i); }; li.append(btn); outlineGroup.append(li);
  });
  $('menuBtn').onclick = () => { pauseAll(); menu.showModal(); };
  $('notesBtn').onclick = openNotes;
  document.querySelectorAll('[data-close]').forEach((btn) => { btn.onclick = () => btn.closest('dialog').close(); });
  async function fullScreen() {
    if (!document.fullscreenElement) {
      try { await document.documentElement.requestFullscreen(); } catch { $('fullBtn').textContent = 'Use browser full screen'; }
    } else await document.exitFullscreen();
  }
  $('fullBtn').onclick = fullScreen;
  document.addEventListener('fullscreenchange', () => {
    $('fullBtn').textContent = document.fullscreenElement ? 'Exit full screen' : 'Full screen';
    $('fullBtn').setAttribute('aria-label', $('fullBtn').textContent);
  });
  $('prevBtn').onclick = backward; $('nextBtn').onclick = forward;
  window.addEventListener('hashchange', () => show(Number(location.hash.slice(1) || 1) - 1, false));
  document.addEventListener('keydown', (event) => {
    if (notes.open || menu.open || event.altKey || event.metaKey || event.ctrlKey) return;
    const key = event.key.toLowerCase();
    const navArrow = event.target.closest('.nav') && ['arrowright', 'arrowleft', 'pagedown', 'pageup'].includes(key);
    if ((!navArrow && /INPUT|TEXTAREA|SELECT|BUTTON|VIDEO/.test(event.target.tagName)) || event.target.isContentEditable) return;
    if (key === 'arrowright' || key === 'pagedown' || key === ' ') { event.preventDefault(); forward(); }
    else if (key === 'arrowleft' || key === 'pageup') { event.preventDefault(); backward(); }
    else if (key === 'home') show(0);
    else if (key === 'end') show(slides.length - 1);
    else if (key === 'n') openNotes();
    else if (key === 'f') fullScreen();
  });
  document.addEventListener('visibilitychange', () => { if (document.hidden) pauseAll(); });
  reduced.addEventListener('change', () => { if (reduced.matches) pauseAll(); });
  // Each model has its own independent random generator. These are teaching
  // mechanisms, not fitted parameters, observed data, or species predictions.
  function randomGenerator(seed) {
    let state = seed >>> 0;
    return () => { state ^= state << 13; state ^= state >>> 17; state ^= state << 5; return (state >>> 0) / 4294967296; };
  }
  // Original vector drawings: readable anatomy and alternating leg strokes.
  function drawAnt(ctx, x, y, angle, color, scale = 1, phase = 0, carrying = false) {
    ctx.save(); ctx.translate(x,y); ctx.rotate(angle); ctx.scale(scale,scale);
    ctx.lineCap='round'; ctx.lineJoin='round'; ctx.strokeStyle=color; ctx.lineWidth=1.15;
    for(let side of [-1,1]) for(let leg=0;leg<3;leg++) {
      const swing=Math.sin(phase+leg*Math.PI+side*Math.PI)*2.2, root=leg*3-1;
      ctx.beginPath();ctx.moveTo(root,side*1.5);ctx.lineTo(root-2+swing,side*5.3);
      ctx.lineTo(root-7+swing,side*(9.5-leg*.5));ctx.lineTo(root-10+swing,side*10.7);ctx.stroke();
    }
    const sheen=ctx.createLinearGradient(0,-5,0,5);sheen.addColorStop(0,'#776651');sheen.addColorStop(.35,color);sheen.addColorStop(1,'#171e18');
    ctx.fillStyle=sheen;
    for(const [cx,rx,ry] of [[-10,7.2,4.5],[-1.8,1.4,1.6],[3,5.1,2.9],[11,4.5,4.2]]) {
      ctx.beginPath();ctx.ellipse(cx,0,rx,ry,0,0,Math.PI*2);ctx.fill();
    }
    ctx.fillStyle='#101c17';ctx.beginPath();ctx.arc(12,-3,.85,0,Math.PI*2);ctx.arc(12,3,.85,0,Math.PI*2);ctx.fill();
    ctx.strokeStyle=color;ctx.lineWidth=.9;
    for(let side of [-1,1]) {
      ctx.beginPath();ctx.moveTo(13,side*2);ctx.lineTo(17,side*(5+Math.sin(phase*.5)*.6));ctx.lineTo(22,side*5);ctx.stroke();
      ctx.beginPath();ctx.moveTo(14,side*1.5);ctx.lineTo(17.5,side*2.2);ctx.lineTo(17,side*.3);ctx.stroke();
    }
    if(carrying){ctx.fillStyle='#ead7a4';ctx.beginPath();ctx.ellipse(19,0,3,2.7,0,0,Math.PI*2);ctx.fill();}
    ctx.restore();
  }
  function leaf(ctx,x,y,angle,size,color) {
    ctx.save();ctx.translate(x,y);ctx.rotate(angle);ctx.fillStyle=color;ctx.beginPath();
    ctx.moveTo(-size,0);ctx.bezierCurveTo(-size*.4,-size*.48,size*.45,-size*.48,size,0);
    ctx.bezierCurveTo(size*.4,size*.35,-size*.4,size*.4,-size,0);ctx.fill();
    ctx.strokeStyle='#6e725344';ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(-size,0);ctx.lineTo(size,0);ctx.stroke();ctx.restore();
  }
  function forestFloor(ctx,height) {
    const ground=ctx.createLinearGradient(0,0,1000,height);ground.addColorStop(0,'#e8e2d1');ground.addColorStop(1,'#ded5bc');
    ctx.fillStyle=ground;ctx.fillRect(0,0,1000,height);
    const rng=randomGenerator(8173);
    for(let i=0;i<250;i++){ctx.fillStyle=i%3?'#8b795912':'#b7a57f38';ctx.beginPath();ctx.ellipse(rng()*1000,rng()*height,1+rng()*2,.5+rng()*1.1,rng()*6,0,Math.PI*2);ctx.fill();}
    [[36,25,.5,63,'#9a98704d'],[940,32,-.6,72,'#a79d7245'],[40,height-25,-.6,55,'#ac98634d'],[940,height-20,.5,83,'#6f7c5b35']].forEach(args=>leaf(ctx,...args));
    ctx.strokeStyle='#b09a6a55';ctx.lineWidth=2;
    for(let i=0;i<9;i++){let x=35+i*123;ctx.beginPath();ctx.moveTo(x,height-8);ctx.lineTo(x+30,height-15);ctx.stroke();}
  }
  function label(ctx,text,x,y,size=22) {ctx.font=size+'px Plex, Arial';ctx.fillStyle='#263d30';ctx.textAlign='center';ctx.fillText(text,x,y);}
  function nest(ctx,x,y,size=1) {
    ctx.save();ctx.translate(x,y);ctx.scale(size,size);
    ctx.fillStyle='#bbaa87';ctx.beginPath();ctx.ellipse(0,7,48,29,0,0,Math.PI*2);ctx.fill();
    ctx.fillStyle='#cabea0';ctx.beginPath();ctx.ellipse(0,1,40,25,0,0,Math.PI*2);ctx.fill();
    const inside=ctx.createRadialGradient(-3,-3,3,0,0,21);inside.addColorStop(0,'#15251d');inside.addColorStop(1,'#66513a');
    ctx.fillStyle=inside;ctx.beginPath();ctx.ellipse(0,0,23,13,-.08,0,Math.PI*2);ctx.fill();
    for(let i=0;i<8;i++){ctx.fillStyle=i%2?'#9f9478':'#d1c7ac';ctx.beginPath();ctx.ellipse(Math.cos(i*1.9)*32,6+Math.sin(i*1.9)*17,3,2,i,0,Math.PI*2);ctx.fill();}
    ctx.restore();
  }
  const tctx = $('trailCanvas').getContext('2d');
  let trail = {}; let tRng; let trailRun = 0;
  function resetTrail() {
    trailRun++; tRng = randomGenerator(9013 + trailRun * 7919);
    trail = { running: false, clock: 0, spawn: 0, scent: $('trailScent').getAttribute('aria-pressed') === 'true', blocked: $('trailBlock').getAttribute('aria-pressed') === 'true', p: [1, 1], trips: [0, 0], ants: [] };
    $('trailPlay').textContent = 'Start ants'; drawTrail();
  }
  function pauseTrail() { trail.running = false; $('trailPlay').textContent = 'Start ants'; }
  pauses.push(pauseTrail);
  function advanceTrail(dt) {
    trail.clock += dt; trail.spawn += dt;
    trail.p = trail.p.map((p) => Math.max(1, p * Math.exp(-0.06 * dt)));
    while (trail.spawn >= 0.14) {
      trail.spawn -= 0.14;
      const a = Math.pow(trail.p[0], 2.2), b = Math.pow(trail.p[1], 2.2);
      const prob = trail.scent ? (0.06 + 0.88 * a / (a + b)) : 0.5;
      const branch = trail.blocked ? 1 : (tRng() < prob ? 0 : 1);
      trail.ants.push({ branch, progress: 0, speed: 0.45 + tRng() * 0.08 });
    }
    for (const ant of trail.ants) {
      ant.progress += ant.speed * dt;
      if (ant.progress >= 2) { trail.trips[ant.branch]++; if (trail.scent) trail.p[ant.branch] += 1.8; }
    }
    trail.ants = trail.ants.filter((ant) => ant.progress < 2);
  }
  function trailPoint(branch, p) {
    return { x: 150 + 700 * p, y: 162 + (branch === 0 ? -90 : 90) * Math.sin(Math.PI * p) };
  }
  function drawTrail() {
    forestFloor(tctx,330);
    const textScale=Math.min(1.5,Math.max(1,750/($('trailCanvas').getBoundingClientRect().width||1000)));
    for(let branch=0;branch<2;branch++) {
      const path=new Path2D();
      for(let i=0;i<=100;i++){const p=trailPoint(branch,i/100);if(!i)path.moveTo(p.x,p.y);else path.lineTo(p.x,p.y);}
      tctx.strokeStyle='#bbad8d66';tctx.lineWidth=28;tctx.stroke(path);
      tctx.strokeStyle='#eee8d6';tctx.lineWidth=23;tctx.stroke(path);
      if(trail.scent){tctx.save();tctx.strokeStyle='#bf8b24';tctx.lineWidth=13;tctx.globalAlpha=Math.min(.72,.08+trail.p[branch]/65);tctx.shadowBlur=10;tctx.shadowColor='#bc8c30';tctx.stroke(path);tctx.restore();}
    }
    nest(tctx,108,164);label(tctx,'Nest',108,225,22*textScale);
    leaf(tctx,897,163,-.3,38,'#77804a');leaf(tctx,908,166,.25,23,'#a3a855');
    tctx.fillStyle='#d6b565';for(let i=0;i<5;i++){tctx.beginPath();tctx.arc(888+i*8,160+(i%2)*8,4,0,Math.PI*2);tctx.fill();}
    label(tctx,'Food',902,225,22*textScale);
    label(tctx,'Upper route',500,30,22*textScale);label(tctx,'Lower route',500,317,22*textScale);
    if(trail.blocked){tctx.save();tctx.translate(500,72);tctx.rotate(.55);tctx.fillStyle='#80674d';tctx.fillRect(-25,-9,50,18);tctx.strokeStyle='#b69b72';tctx.lineWidth=2;tctx.beginPath();tctx.moveTo(-22,-3);tctx.lineTo(22,-3);tctx.stroke();tctx.restore();label(tctx,'Closed',500,57,18);}
    for(const ant of trail.ants){
      const home=ant.progress>1,p=home?2-ant.progress:ant.progress;
      const pos=trailPoint(ant.branch,p),tangent=Math.atan2((ant.branch===0?-90:90)*Math.PI*Math.cos(Math.PI*p),700);
      drawAnt(tctx,pos.x,pos.y+(home?7:-7),tangent+(home?Math.PI:0),'#293b2e',.82,trail.clock*19+ant.speed*20,home);
    }
    $('trailStatus').textContent='Upper: '+trail.trips[0]+' trips · Lower: '+trail.trips[1]+' trips · '+(trail.running?'Running':(trail.clock?'Paused':'Ready'));
  }
  $('trailPlay').onclick = () => { trail.running = !trail.running; $('trailPlay').textContent = trail.running ? 'Pause ants' : 'Start ants'; drawTrail(); };
  $('trailStep').onclick = () => { pauseTrail(); for (let i = 0; i < 120; i++) advanceTrail(0.05); drawTrail(); };
  $('trailReset').onclick = resetTrail;
  $('trailScent').onclick = () => { const on = $('trailScent').getAttribute('aria-pressed') !== 'true'; $('trailScent').setAttribute('aria-pressed', String(on)); $('trailScent').textContent = 'Scent: ' + (on ? 'on' : 'off'); resetTrail(); };
  $('trailBlock').onclick = () => { trail.blocked = !trail.blocked; $('trailBlock').setAttribute('aria-pressed', String(trail.blocked)); $('trailBlock').textContent = trail.blocked ? 'Reopen upper route' : 'Block upper route'; drawTrail(); };
  const qctx = $('quorumCanvas').getContext('2d'); let quorum = {}; let qRng; let qRun = 0;
  function resetQuorum() {
    qRun++; qRng = randomGenerator(1117 + qRun * 6151);
    quorum = { running: false, time: 0, next: 0, assessments: 0, counts: [0, 0], moving: [], decision: null, threshold: Number($('threshold').value) };
    $('thresholdValue').textContent = quorum.threshold; $('quorumPlay').textContent = 'Start scouts'; drawQuorum();
  }
  function pauseQuorum() { quorum.running=false; $('quorumPlay').textContent=quorum.decision != null?'Show transport':'Start scouts'; }
  pauses.push(pauseQuorum);
  function assessment() {
    if (quorum.decision !== null) return;
    quorum.assessments++;
    // Near site has greater discovery weight, but lower acceptance probability.
    const w0 = 1.8 + quorum.counts[0] * 0.3, w1 = 1 + quorum.counts[1] * 0.3;
    const site = qRng() < w0 / (w0 + w1) ? 0 : 1;
    const accepted = qRng() < (site === 0 ? 0.35 : 0.83);
    if (accepted) quorum.counts[site]++;
    quorum.moving.push({ site, age: 0, accepted });
    if (quorum.counts[site] >= quorum.threshold) { quorum.decision = site; pauseQuorum(); }
  }
  function advanceQuorum(dt) {
    quorum.time += dt; quorum.next += dt; quorum.moving.forEach((ant) => { ant.age += dt; }); quorum.moving = quorum.moving.filter((ant) => ant.age < 3);
    if (quorum.next >= 0.7) { quorum.next = 0; assessment(); }
  }
  function drawQuorum() {
    forestFloor(qctx,300);
    const textScale=Math.min(1.5,Math.max(1,750/($('quorumCanvas').getBoundingClientRect().width||1000)));
    const sites=[[190,125,0],[810,125,1]];
    qctx.strokeStyle='#c5b997';qctx.lineWidth=17;qctx.lineCap='round';qctx.beginPath();qctx.moveTo(490,225);qctx.lineTo(190,138);qctx.moveTo(490,225);qctx.lineTo(810,138);qctx.stroke();
    sites.forEach(([x,y,index])=>{
      qctx.save();qctx.translate(x,y);
      qctx.fillStyle=index===0?'#bca582':'#879576';qctx.beginPath();qctx.roundRect(-100,-53,200,106,32);qctx.fill();
      qctx.strokeStyle=index===0?'#997e5e':'#627455';qctx.lineWidth=2;
      for(let i=0;i<4;i++){qctx.beginPath();qctx.roundRect(-94+i*7,-47+i*5,188-i*14,94-i*10,29);qctx.stroke();}
      qctx.fillStyle=index===0?'#797560':'#344c39';qctx.beginPath();qctx.ellipse(0,0,index===0?68:57,index===0?22:29,0,0,Math.PI*2);qctx.fill();
      if(quorum.decision===index){qctx.strokeStyle='#a13f27';qctx.lineWidth=4;qctx.beginPath();qctx.roundRect(-107,-60,214,120,35);qctx.stroke();}
      for(let i=0;i<quorum.counts[index];i++){const xx=-42+(i%4)*27,yy=-12+Math.floor(i/4)*13;drawAnt(qctx,xx,yy,(i%2)*Math.PI,'#1c2e22',.51);}
      qctx.restore();
      label(qctx,index===0?'Near / exposed':'Far / sheltered',x,35,23*textScale);
      label(qctx,quorum.counts[index]+' / '+quorum.threshold+' scouts',x,212,25*textScale);
    });
    nest(qctx,490,227,.9);label(qctx,'Old nest',490,287,22*textScale);
    for(const ant of quorum.moving){const p=Math.min(1,ant.age/2.5),tx=ant.site===0?190:810;drawAnt(qctx,490+(tx-490)*p,227-102*p,Math.atan2(-102,tx-490),ant.accepted?'#293b2e':'#84442d',.8,ant.age*19);}
    let decision='Searching';
    if(quorum.decision!==null){
      decision='Threshold reached: '+(quorum.decision===0?'near / exposed':'far / sheltered')+' · '+(quorum.running?'Transport illustration running':'Transport ready');
      // Transport is a separate explanatory animation, started by the presenter.
      if(quorum.time && quorum.running){const tx=quorum.decision===0?190:810;for(let i=0;i<8;i++){const p=(quorum.time*.13+i/8)%1;drawAnt(qctx,490+(tx-490)*p,227-102*p+8,Math.atan2(-102,tx-490),'#293b2e',.82,quorum.time*19+i,true);}}
    }
    $('quorumStatus').textContent='Near / exposed: '+quorum.counts[0]+' · Far / sheltered: '+quorum.counts[1]+' · '+decision;
    $('quorumPlay').disabled=false;$('quorumStep').disabled=quorum.decision!==null;
  }
  $('quorumPlay').onclick=()=>{quorum.running=!quorum.running;$('quorumPlay').textContent=quorum.decision!==null?(quorum.running?'Pause transport':'Show transport'):(quorum.running?'Pause scouts':'Start scouts');drawQuorum();};
  $('quorumStep').onclick = () => { pauseQuorum(); quorum.moving.forEach((ant) => { ant.age = 3; }); assessment(); drawQuorum(); };
  $('quorumReset').onclick = resetQuorum; $('threshold').oninput = resetQuorum;
  let seedStage = 0;
  const seedLabels = ['1 / 3 · Seed with an oily attachment', '2 / 3 · Ant carries the seed toward the nest', '3 / 3 · Attachment removed; seed left behind'];
  function drawSeed() {
    $('seedAnt').setAttribute('transform', seedStage === 0 ? 'translate(75 215)' : seedStage === 1 ? 'translate(510 215)' : 'translate(560 275)');
    $('seedCargo').setAttribute('transform', seedStage === 0 ? 'translate(48 207)' : seedStage === 1 ? 'translate(483 207)' : 'translate(485 277)');
    $('elaiosome').style.display = seedStage === 2 ? 'none' : '';
    $('seedStatus').textContent = seedLabels[seedStage]; $('seedNext').textContent = seedStage === 0 ? 'Carry the seed' : seedStage === 1 ? 'Remove the attachment' : 'Sequence complete'; $('seedNext').disabled = seedStage === 2;
  }
  $('seedNext').onclick = () => { seedStage=Math.min(2,seedStage+1); drawSeed(); }; $('seedReset').onclick=()=>{seedStage=0;drawSeed();};
  const cards=[...document.querySelectorAll('.head-card')];
  const jobs=[...document.querySelectorAll('[data-job]')];
  let selectedJob=null; const matched=new Set();
  function flipCard(card,flipped) {
    card.querySelector('.front').hidden=flipped;card.querySelector('.back').hidden=!flipped;
    card.querySelector('.card-flip').setAttribute('aria-expanded',String(flipped));
  }
  function gameStatus(message) {$('matchStatus').textContent=matched.size+' of 3 matched · '+message;}
  jobs.forEach(button=>{button.onclick=()=>{
    if(matched.has(button.dataset.job))return;
    selectedJob=selectedJob===button.dataset.job?null:button.dataset.job;
    jobs.forEach(job=>job.setAttribute('aria-pressed',String(job.dataset.job===selectedJob)));
    gameStatus(selectedJob?'Choose a head for “'+button.textContent+'.”':'No job selected.');
  };});
  cards.forEach(card=>{card.querySelector('.card-flip').onclick=()=>{
    if(selectedJob && !matched.has(card.dataset.answer)){
      if(selectedJob!==card.dataset.answer){gameStatus('Take another look. Try a different head.');return;}
      matched.add(selectedJob);card.classList.add('matched');flipCard(card,true);
      jobs.find(job=>job.dataset.job===selectedJob).classList.add('matched');selectedJob=null;
      jobs.forEach(job=>job.setAttribute('aria-pressed','false'));
      gameStatus(matched.size===3?'All matched! Each shape has a story.':'A match! Choose the next job.');
    } else {flipCard(card,card.querySelector('.card-flip').getAttribute('aria-expanded')!=='true');}
  };});
  $('revealHeads').onclick=()=>{cards.forEach(card=>flipCard(card,true));selectedJob=null;jobs.forEach(job=>job.setAttribute('aria-pressed','false'));gameStatus('Answers revealed. Start again to play.');};
  $('resetHeads').onclick=()=>{matched.clear();selectedJob=null;cards.forEach(card=>{card.classList.remove('matched');flipCard(card,false);});jobs.forEach(job=>{job.classList.remove('matched');job.setAttribute('aria-pressed','false');});gameStatus('No job selected.');};
  let last = 0;
  function frame(now) {
    const dt = last ? Math.min((now-last)/1000,0.08) : 0; last = now;
    if (!document.hidden && !notes.open && !menu.open) {
      if (trail.running && slides[current].contains($('trailCanvas'))) { advanceTrail(dt); drawTrail(); }
      if (quorum.running && slides[current].contains($('quorumCanvas'))) { advanceQuorum(dt); drawQuorum(); }
    }
    requestAnimationFrame(frame);
  }
  window.addEventListener('resize', () => { drawTrail(); drawQuorum(); });
  resetTrail(); resetQuorum(); drawSeed(); show(Number(location.hash.slice(1)||1)-1,false); requestAnimationFrame(frame);
})();
