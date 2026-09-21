(() => {
  'use strict';
  const KEY = 'techbytes-links-v1';
  const localHost = ['localhost', '127.0.0.1', '[::1]'].includes(location.hostname);
  const defaults = { ...window.WORKSHOP_DEFAULTS };
  // Rehearsal and published slides both use the public MVP by default.
  // A localhost app can still be selected explicitly in Links during development.
  let config = { ...defaults }, expanded = null, restoreFocus = null, inertState = [];
  const scriptURL = new URL(document.currentScript.src);
  const asset = name => new URL('images/' + name, scriptURL).href;
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const hostMatches = (host, domain) => host === domain || host.endsWith('.' + domain);
  function validate(key, value) {
    if (!value.trim()) return '';
    if (value.length > 4000) throw new Error('That link is too long. Use its public share URL.');
    const url = new URL(value.trim());
    const loopback = ['127.0.0.1', 'localhost', '[::1]'].includes(url.hostname);
    if (url.username || url.password || (url.protocol !== 'https:' && !(key === 'collective' && localHost && loopback && url.protocol === 'http:'))) throw new Error('Use a public HTTPS link without embedded credentials.');
    if (/token|secret|password|moderator|admin|auth|bypass/i.test(url.search + url.pathname)) throw new Error('Use a participant or public preview link, not a private access or moderator link.');
    if (key === 'maps' && !(url.hostname === 'www.google.com' && url.pathname.startsWith('/maps/embed'))) throw new Error('Maps needs the src URL from Share → Embed a map.');
    if (key === 'spotify' && !(url.hostname === 'open.spotify.com' && /^\/(?:embed\/)?(playlist|album|track|artist|episode|show)\/[A-Za-z0-9]+\/?$/.test(url.pathname))) throw new Error('Use a Spotify playlist, album, track, artist, show or episode link.');
    if (key === 'figma' && !((hostMatches(url.hostname, 'figma.com') && /^\/(proto|design|file|make)\//.test(url.pathname)) || hostMatches(url.hostname, 'figma.site'))) throw new Error('Use a Figma design/prototype link or a published figma.site link.');
    if (key === 'gallery' && !(url.hostname === 'techbytes-sketch-gallery.gchism.chatgpt.site' && url.pathname === '/' && (!url.searchParams.has('room') || /^[a-f0-9]{32}$/.test(url.searchParams.get('room'))) && !url.hash)) throw new Error('Use the classroom link copied from the TechBytes Sketch Gallery, without a private browser-identity fragment.');
    if (key.endsWith('Poll')) {
      const responseLink = url.host === 'pe.app' && /^\/response_links\/[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}\/start$/.test(url.pathname) && !url.search && !url.hash;
      const legacyProvider = ['slido.com', 'sli.do', 'mentimeter.com', 'menti.com', 'polleverywhere.com', 'pollev.com', 'pollev-embeds.com'].some(d => hostMatches(url.hostname,d));
      if (!responseLink && !legacyProvider) throw new Error('Use a public participant embed URL from Slido, Mentimeter or Poll Everywhere. For pe.app, use Share → Participants → Response link.');
    }
    return url.href;
  }
  function validConfig(raw) {
    const result = {};
    for (const key of Object.keys(defaults)) if (typeof raw?.[key] === 'string') result[key] = validate(key,raw[key]);
    return result;
  }
  let startupNotice = '';
  try { config = { ...config, ...validConfig(JSON.parse(localStorage.getItem(KEY) || '{}')) }; }
  catch (_) { startupNotice = 'Saved links could not be read. Defaults are in use; the saved record was not changed.'; }
  try {
    const encoded = new URL(location.href).searchParams.get('session');
    if (encoded) config = { ...config, ...validConfig(JSON.parse(decodeURIComponent(escape(atob(encoded.replace(/-/g,'+').replace(/_/g,'/')))))) };
  } catch (_) { startupNotice = 'The shared link settings could not be read. Defaults are in use.'; }
  function providerURL(kind, fullApp = false) {
    if (['collective', 'practice', 'birds'].includes(kind)) {
      const u = new URL(config.collective || defaults.collective);
      u.searchParams.set('embed',kind === 'birds' && !fullApp ? 'title' : '1');
      if (kind === 'practice') u.searchParams.set('experience','practice');
      if (kind === 'birds') u.searchParams.set('experience','original');
      return u.href;
    }
    if (kind === 'spotify') {
      const u = new URL(config.spotify || defaults.spotify);
      return 'https://open.spotify.com/embed/' + u.pathname.replace(/^\/(embed\/)?/,'') + '?utm_source=generator&theme=0';
    }
    if (kind === 'figma' && config.figma) {
      const u = new URL(config.figma);
      if (hostMatches(u.hostname,'figma.site')) return u.href;
      if(u.pathname.startsWith('/proto/')) {
        u.hostname='embed.figma.com';
        u.searchParams.set('embed-host','techbytes');
        u.searchParams.set('footer','false');
        u.searchParams.set('viewport-controls','false');
        u.searchParams.set('device-frame','false');
        u.searchParams.set('scaling','contain');
        return u.href;
      }
      return 'https://www.figma.com/embed?embed_host=share&url=' + encodeURIComponent(u.href);
    }
    return config[kind] || '';
  }
  function openURL(kind) {
    if (kind === 'maps') return 'https://www.google.com/maps/search/?api=1&query=Willamette+University+Salem';
    if (kind === 'practice' || kind === 'birds') return providerURL(kind,true);
    return config[kind] || '';
  }
  const names = {maps:'Google Maps', spotify:'Spotify', collective:'Collective', birds:'Collective · Salem swifts', practice:'Contributor practice', figma:'Student prototype', mapsPoll:'Google Maps audience poll', spotifyPoll:'Spotify audience poll'};
  const posters = {maps:'maps.png',spotify:'spotify.png',collective:'collective.png',birds:'collective-scene.png',practice:'practice.png',figma:'figma-template.png'};
  const devices = [...document.querySelectorAll('[data-embed]')];
  function deviceMarkup(device) {
    const kind = device.dataset.embed, name = names[kind], isPoll = kind.endsWith('Poll');
    device.classList.add('device');
    if(isPoll) device.classList.add('poll-device');
    device.innerHTML = `<div class="device-shell"><div class="device-head"><span></span><span>WEB VIEW</span></div><div class="embed-screen"><div class="embed-cover"><span class="cover-title"></span><span class="cover-detail"></span><button class="load-embed" type="button"></button></div></div></div><span class="device-exit-label">Back to the discussion</span><button class="device-exit" type="button" aria-label="Close interactive view">×</button><div class="device-actions"><button class="expand-embed" type="button">Explore full screen</button><a class="external-embed" target="_blank" rel="noopener noreferrer">Open separately ↗</a></div><p class="embed-caption"></p>`;
    device.querySelector('.device-head span').textContent = name;
    const cover = device.querySelector('.embed-cover');
    if(posters[kind]) {
      const img = new Image(); img.src = asset(posters[kind]); img.alt = name + ' preview'; img.loading = 'lazy';
      img.onerror = () => { img.remove(); cover.querySelector('.cover-title').textContent = name; };
      cover.prepend(img);
    } else {
      cover.querySelector('.cover-title').textContent = isPoll ? 'Where would you place it?' : 'Your app. One task.';
      cover.querySelector('.cover-detail').textContent = isPoll ? 'Use a shared poll to compare the room’s reasoning.' : 'A three-screen Figma workshop template.';
    }
    device.querySelector('.load-embed').onclick = () => {
      if (!providerURL(kind)) { settings.showModal(); settings.querySelector(`[name="${kind}"]`)?.focus(); return; }
      if(matchMedia('(max-width:900px)').matches) expand(device);
      startDevice(device);
    };
    device.querySelector('.expand-embed').onclick = () => {
      if (!providerURL(kind)) { settings.showModal(); settings.querySelector(`[name="${kind}"]`)?.focus(); return; }
      expand(device); startDevice(device);
    };
    if (kind === 'birds') {
      const toggle=document.createElement('button'); toggle.type='button'; toggle.className='preview-toggle';
      toggle.onclick=()=>{
        if(device.querySelector('iframe')){device.dataset.previewPaused='true';pauseDevice(device);}
        else startDevice(device);
      };
      device.querySelector('.device-actions').prepend(toggle);
      device.querySelector('.expand-embed').textContent='Explore';
    }
    device.querySelector('.device-exit').onclick = closeExpanded;
    refreshDevice(device);
  }
  function refreshDevice(device) {
    const kind=device.dataset.embed, connected=!!providerURL(kind), poll=kind.endsWith('Poll');
    device.classList.toggle('connected',connected);
    const link=device.querySelector('.external-embed');
    link.hidden=!openURL(kind); if(!link.hidden) link.href=openURL(kind);
    device.querySelector('.load-embed').textContent = connected ? 'Open ' + (poll ? 'live poll' : names[kind]) : (poll ? 'Connect a live poll' : 'Connect Figma');
    device.querySelector('.expand-embed').textContent = connected ? 'Explore full screen' : 'Set up link';
    device.querySelector('.embed-caption').textContent = poll ? (connected ? 'Votes go to the polling provider. If blank, open separately.' : 'No live poll connected. Use the discussion fallback below.') : kind==='spotify' ? 'Official player, not the full app. For personal recommendations, open Spotify separately.' : kind==='maps' ? 'Interactive Google map. Full route planning opens separately.' : kind==='figma' ? 'Shared Figma preview. Viewing depends on the file’s sharing settings.' : 'Live app. If sign-in or a blank screen appears, open separately. Salem footage needs internet.';
    if(kind==='birds') {
      device.querySelector('.expand-embed').textContent='Explore';
      device.querySelector('.embed-caption').textContent='Live illustrative model. Replaying starts a fresh flock.';
      refreshPreviewControl(device);
    }
  }
  function refreshPreviewControl(device) {
    const toggle=device.querySelector('.preview-toggle');
    if(toggle)toggle.textContent=device.querySelector('iframe')?'Pause preview':'Replay birds';
  }
  function startDevice(device) {
    if(device.dataset.embed==='birds'){device.dataset.previewPaused='false';device.dataset.previewRequested='true';}
    loadDevice(device);
  }
  function loadDevice(device) {
    const src=providerURL(device.dataset.embed,device.classList.contains('expanded')); if(!src)return;
    let iframe=device.querySelector('iframe');
    if(!iframe) {
      iframe=document.createElement('iframe'); iframe.title=names[device.dataset.embed]+' interactive web view';
      iframe.referrerPolicy='strict-origin-when-cross-origin';
      iframe.allow = device.dataset.embed==='spotify' ? 'autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture' : 'fullscreen; clipboard-write';
      iframe.setAttribute('allowfullscreen','');
      device.querySelector('.embed-screen').prepend(iframe);
    }
    if(iframe.getAttribute('src')!==src) iframe.src=src;
    device.querySelector('.embed-cover').hidden=true;
    refreshPreviewControl(device);
  }
  function pauseDevice(device) {
    const iframe=device.querySelector('iframe'); if(!iframe)return;
    if(['collective','practice','birds'].includes(device.dataset.embed)) {
      iframe.contentWindow?.postMessage({type:'collective:pause'},new URL(iframe.src).origin);
    }
    if(['spotify','birds'].includes(device.dataset.embed)) {
      iframe.remove(); device.querySelector('.embed-cover').hidden=false;
      refreshPreviewControl(device);
    }
  }
  function expand(device) {
    if(expanded)closeExpanded();
    restoreFocus=document.activeElement; expanded=device;
    device.classList.add('expanded'); device.setAttribute('role','dialog'); device.setAttribute('aria-modal','true'); device.setAttribute('aria-label',names[device.dataset.embed]);
    document.body.classList.add('embed-open');
    let branch=device;
    while(branch.parentElement && branch.parentElement!==document.documentElement) {
      for(const sibling of branch.parentElement.children) if(sibling!==branch && sibling instanceof HTMLElement) { inertState.push([sibling,sibling.inert]); sibling.inert=true; }
      branch=branch.parentElement;
    }
    device.querySelector('.device-exit').focus({preventScroll:true});
  }
  function closeExpanded() {
    if(!expanded)return;
    const device=expanded; expanded=null;
    if(device.dataset.embed==='birds')device.dataset.previewPaused='true';
    device.classList.remove('expanded'); device.removeAttribute('role');device.removeAttribute('aria-modal');device.removeAttribute('aria-label');
    document.body.classList.remove('embed-open');
    for(const [el,value] of inertState)el.inert=value; inertState=[];
    pauseDevice(device); restoreFocus?.focus({preventScroll:true});
  }
  document.addEventListener('keydown', e=>{
    if(!expanded)return;
    if(e.key==='Escape'){e.preventDefault();e.stopImmediatePropagation();closeExpanded();return;}
    if(e.key==='Tab') {
      // The iframe participates in the native tab order, including its inner controls.
      const close=expanded.querySelector('.device-exit'),frame=expanded.querySelector('iframe');
      if(e.shiftKey && document.activeElement===close){e.preventDefault();frame?.focus();}
      else if(!e.shiftKey && document.activeElement===close){e.preventDefault();frame?.focus();}
    }
  },true);
  document.addEventListener('focusin',e=>{if(expanded && !expanded.contains(e.target)) expanded.querySelector('.device-exit').focus();});
  document.addEventListener('deck:beforechange',closeExpanded);
  const settings=document.createElement('dialog'); settings.id='workshopSettings';settings.className='workshop-dialog';settings.setAttribute('aria-labelledby','workshopSettingsTitle');
  settings.innerHTML=`<button class="close" type="button" aria-label="Close workshop links">Close</button><h2 id="workshopSettingsTitle">Workshop links</h2><p>Public previews and participant links only. These settings stay in this browser unless you explicitly copy a session link.</p><form><div class="link-fields"></div><div class="settings-actions"><button type="submit" class="interaction-button primary">Save links</button><button type="button" class="interaction-button" data-share-session>Copy session link</button><button type="button" class="interaction-button" data-reset-links>Use defaults</button></div></form><p class="settings-status" role="status"></p><small>Spotify sign-in happens on Spotify, never in this form. Figma must allow the intended audience to view. Native polls save through the classroom gallery database. Reveal or close them in the gallery’s presenter controls. External poll URLs below are optional backups.</small>`;
  const fields=[['maps','Google Maps embed URL','From Maps: Share → Embed a map → copy only the iframe src.'],['spotify','Spotify playlist or other content URL','Replace the public example with your chosen playlist.'],['collective','Collective app URL','Use a learner-accessible deployment. localhost is only for rehearsal on this computer.'],['figma','Figma prototype / published Make URL','Use Share in the prototype. Students need view access, not editing access.'],['mapsPoll','Google Maps external poll backup URL','Use the polling service’s public embed URL, never its host/moderator URL.'],['spotifyPoll','Spotify external poll backup URL','A separate question using the same five-point knowledge spectrum.'],['gallery','Classroom sketch gallery link','Create a room in the gallery, then paste its classroom link here. Submissions go to this room only after students choose Submit.']];
  for(const [key,label,hint]of fields){
    const l=document.createElement('label');l.htmlFor='link-'+key;l.textContent=label;
    const input=document.createElement('input');input.id=l.htmlFor;input.name=key;input.type='url';input.value=config[key];input.autocomplete='off';input.spellcheck=false;
    const small=document.createElement('small');small.id='hint-'+key;small.textContent=hint;input.setAttribute('aria-describedby',small.id);
    settings.querySelector('.link-fields').append(l,input,small);
  }
  document.body.append(settings);
  const setup=document.createElement('button');setup.id='workshopLinksBtn';setup.textContent='Links';setup.setAttribute('aria-label','Open workshop links');setup.onclick=()=>{settings.showModal();};
  document.querySelector('.tools').insertBefore(setup,document.querySelector('#helpBtn'));
  settings.querySelector('.close').onclick=()=>settings.close();
  settings.querySelector('.settings-status').textContent=startupNotice;
  function applySettings(next){
    config=next;
    for(const device of devices){pauseDevice(device);device.querySelector('iframe')?.remove();device.querySelector('.embed-cover').hidden=false;refreshDevice(device);}
    for(const [key] of fields)settings.querySelector(`[name="${key}"]`).value=config[key];
    updatePrototypeLinks();
    publishGalleryLink();
    updateActive();
  }
  settings.querySelector('form').onsubmit=e=>{
    e.preventDefault();
    try {
      const next={...defaults,...validConfig(Object.fromEntries(new FormData(e.target)))};
      localStorage.setItem(KEY,JSON.stringify(next));applySettings(next);
      settings.querySelector('.settings-status').textContent='Saved in this browser. Copy a session link to share these public settings.';
    }catch(error){settings.querySelector('.settings-status').textContent=error.message;}
  };
  settings.querySelector('[data-reset-links]').onclick=()=>{try{localStorage.removeItem(KEY);}catch(_){} applySettings({...defaults});settings.querySelector('.settings-status').textContent='Default links restored in this browser.';};
  async function copyText(text,status) {
    try{await navigator.clipboard.writeText(text);status.textContent='Link copied.';}
    catch(_){status.textContent='Copy this link: '+text;status.classList.add('share-url');}
  }
  settings.querySelector('[data-share-session]').onclick=async()=>{
    const status=settings.querySelector('.settings-status');
    if(localHost || location.protocol==='file:'){status.textContent='This deck is local to this computer. Publish it or serve it on a classroom-accessible address before sharing a session link. Figma’s own link can still be shared.';return;}
    const publicConfig={...config};
    try{validConfig(publicConfig);}catch(error){status.textContent=error.message;return;}
    const u=new URL(location.href);u.searchParams.set('session',btoa(unescape(encodeURIComponent(JSON.stringify(publicConfig)))).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,''));
    await copyText(u.href,status);
  };
  function updatePrototypeLinks(){
    document.querySelectorAll('[data-figma-link]').forEach(a=>{a.hidden=!config.figma;if(config.figma)a.href=config.figma;});
    document.querySelectorAll('[data-copy-figma]').forEach(b=>{b.onclick=()=>{
      if(!config.figma){settings.showModal();settings.querySelector('[name="figma"]').focus();return;}
      copyText(config.figma,b.parentElement.querySelector('[role="status"]'));
    };});
  }
  function publishGalleryLink(){window.TECHBYTES_GALLERY=config.gallery||'';document.dispatchEvent(new CustomEvent('workshop:links',{detail:{gallery:window.TECHBYTES_GALLERY}}));}
  devices.forEach(deviceMarkup); updatePrototypeLinks(); publishGalleryLink();
  function shouldPlayPreview(device) {
    return !document.hidden && !!device.closest('.slide.active') && !device.closest('[data-route][hidden]')
      && device.dataset.previewPaused!=='true' && (!reducedMotion.matches || device.dataset.previewRequested==='true');
  }
  function updateActive(){
    for(const device of devices){
      if(device.dataset.embed==='birds') {
        if(shouldPlayPreview(device))loadDevice(device);else pauseDevice(device);
      } else if(document.hidden || !device.closest('.slide.active') || device.closest('[data-route][hidden]'))pauseDevice(device);
    }
  }
  document.addEventListener('deck:change',updateActive);
  document.addEventListener('visibilitychange',updateActive);
  reducedMotion.addEventListener('change',()=>{
    devices.filter(d=>d.dataset.embed==='birds').forEach(d=>{delete d.dataset.previewRequested;});
    updateActive();
  });
  updateActive();
  // Sketch persistence and explicit submission are handled by sketch.js.
})();
