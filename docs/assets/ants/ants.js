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
    if (groups.length) builds.set(scope, { groups, visible: 0 });
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
    if (slide.classList.contains('cover') || slide.classList.contains('section-break') || slide.dataset.time === 'Reference appendix' || ['Two groups to get to know', 'A regional ant field guide'].includes(slide.dataset.title)) return;
    const title = slide.dataset.title;
    const panels = [...slide.querySelectorAll('.example-panel')];
    const scopes = panels.length ? panels : [slide];
    scopes.forEach(scope => {
      // Models, games and the seed sequence already expose information through
      // their own controls. Their controls must always remain operable.
      if (scope.querySelector('canvas, .head-game, #seedNext')) return;
      let groups = [];
      if (['pollinationCase', 'pollinationOregon', 'pollinationSmokebush'].includes(scope.id)) {
        groups = [[scope.querySelector('.lead')]];
      } else if (title === 'Names our neighbors use') {
        groups = [...scope.querySelectorAll('.neighbor-copy')].map(copy => [copy]);
      } else if (title === 'Other ant eaters') {
        const copy = [...scope.querySelectorAll('.ant-eater-copy')];
        groups = [copy.slice(0, 2), copy.slice(2, 4)];
      } else if (title === 'An ant, up close') {
        const paths = guideLines(scope, '.anatomy-board svg path');
        const labels = [...scope.querySelectorAll('.parts-label text')];
        const mobile = [...scope.querySelectorAll('.parts-mobile span')];
        groups = [[0, 1], [2, 3], [4, 5]].map(indices => indices.flatMap(i => [paths[i], labels[i], mobile[i]]));
      } else if (title === 'The work of a colony') {
        groups = [...scope.querySelectorAll('.worker-task-copy')].map(copy => [copy]);
      } else if (title === 'Pollen moves. Then seeds move.' && scope.querySelector('.ecology-pair')) {
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
      } else if (scope.querySelector('.lead')) {
        groups = [[scope.querySelector('.lead')]];
        if (scope.querySelector('.watch-cue')) groups.push([scope.querySelector('.watch-cue')]);
      }
      if (groups.length) {
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
    const canRewind = build && build.visible > 0;
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
    const text = visible ? build.groups[visible - 1].map(element => element.textContent.trim()).filter(Boolean).join('. ') : 'Image and heading. Explanations are hidden.';
    $('slideAnnounce').textContent = 'Text ' + visible + ' of ' + build.groups.length + ': ' + text;
  }
  function forward() {
    const build = builds.get(context());
    if (build && build.visible < build.groups.length) changeBuild(build.visible + 1);
    else show(current + 1);
  }
  function backward() {
    const build = builds.get(context());
    if (build && build.visible > 0) changeBuild(build.visible - 1);
    else show(current - 1, true, true);
  }
  revealAll.onclick = () => {
    const build = builds.get(context());
    if (build) changeBuild(build.visible < build.groups.length ? build.groups.length : 0);
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
    document.body.classList.toggle('flyer-view', slides[index].classList.contains('flyer-slide'));
    slides.forEach((s, i) => { s.classList.toggle('active', i === index); s.inert = i !== index; });
    [slides[index], ...slides[index].querySelectorAll('.example-panel')].forEach(scope => {
      const build = builds.get(scope);
      if (build) build.visible = complete ? build.groups.length : 0;
      paintBuild(scope);
    });
    updateBuildControls();
    $('timing').textContent = slides[index].dataset.time;
    $('progressBar').style.width = ((index + 1) / slides.length * 100) + '%';
    $('slideAnnounce').textContent = 'Slide ' + (index + 1) + ': ' + slides[index].dataset.title;
    if (updateHash) history.replaceState(null, '', '#' + (index + 1));
    window.scrollTo(0, 0);
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
    if (card.querySelector('.card-return')) {
      card.querySelector('.card-flip').hidden=flipped;
      if (!flipped) pauseAll();
    }
  }
  function gameStatus(message) {$('matchStatus').textContent=matched.size+' of 3 matched · '+message;}
  jobs.forEach(button=>{button.onclick=()=>{
    if(matched.has(button.dataset.job))return;
    selectedJob=selectedJob===button.dataset.job?null:button.dataset.job;
    jobs.forEach(job=>job.setAttribute('aria-pressed',String(job.dataset.job===selectedJob)));
    gameStatus(selectedJob?'Choose a head for “'+button.textContent+'.”':'No job selected.');
  };});
  document.querySelectorAll('.card-return').forEach(button=>{
    button.onclick=()=>flipCard(button.closest('.head-card'),false);
  });
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
  drawSeed(); show(Number(location.hash.slice(1)||1)-1,false);
})();
