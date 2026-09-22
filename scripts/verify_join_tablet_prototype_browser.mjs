// Playwright CLI browser regression. No live classroom writes.
async (page) => {
  const check=(v,m)=>{if(!v)throw Error(m);},base='http://127.0.0.1:8765/design-what-you-know/';
  const errors=[],tablets=[];page.on('pageerror',e=>errors.push(e.message));
  await page.emulateMedia({reducedMotion:'reduce'});
  await page.route('https://techbytes-sketch-gallery.gchism.chatgpt.site/api/**',r=>r.fulfill({contentType:'application/json',body:JSON.stringify({open:true,revealed:false,total:0,mine:null})}));
  for(const route of ['collective','wildcard'])for(const [width,height] of [[320,568],[390,844],[768,1024],[1440,900]]){
    await page.setViewportSize({width,height});await page.goto(base+'?route='+route);await page.reload();
    check(await page.locator('.slide.active').getAttribute('data-title')==='Join the workshop','Join is the first screen on both routes');
    const qr=await page.locator('.slide.active .join-code img').boundingBox(),footer=await page.locator('.footer').boundingBox();
    check(qr.width>=190&&qr.y>=60&&qr.y+qr.height<=footer.y,'Whole QR is visible without scrolling');
    await page.locator('#next').click();check(page.url().endsWith('#2'),'Title is after QR');
    if(width<=900)check(await page.locator('[data-embed=birds] iframe').count()===0,'No phone/tablet autoplay');
  }
  for(const [width,height] of [[768,1024],[820,1180],[1024,768],[1180,820]]){
    await page.setViewportSize({width,height});await page.goto(base+'#9');await page.reload();
    const canvas=page.locator('[data-sketch] canvas'),toolbar=page.locator('.sketch-toolbar');
    const box=await canvas.boundingBox();check(box.width>=width-145&&box.height>=360,'Tablet canvas is broad and tall');
    check(await canvas.evaluate(e=>getComputedStyle(e).touchAction.includes('pan-y')),'Tablet starts in scroll mode');
    await canvas.scrollIntoViewIfNeeded();
    const c=await canvas.boundingBox(),t=await toolbar.boundingBox();check(t.y+t.height<=c.y+1,'Toolbar never overlays the canvas');
    await page.locator('.slide.active').evaluate(e=>e.scrollTop=e.scrollHeight);
    const bottom=await page.locator('.slide.active .frame').evaluate(e=>e.getBoundingClientRect().bottom),footer=await page.locator('.footer').boundingBox();
    check(bottom<=footer.y,'Tablet form bottom stays reachable above navigation');tablets.push({width,height,canvas:{width:box.width,height:box.height}});
  }
  await page.setViewportSize({width:820,height:1180});await page.goto(base+'#9');await page.reload();
  const canvas=page.locator('[data-sketch] canvas');
  await page.getByRole('button',{name:'Draw',exact:true}).click();await canvas.scrollIntoViewIfNeeded();
  const c=await canvas.boundingBox();await page.mouse.move(c.x+30,c.y+30);await page.mouse.down();await page.mouse.move(c.x+200,c.y+100,{steps:30});await page.mouse.up();
  const saved=await page.evaluate(()=>localStorage.getItem(Object.keys(localStorage).find(k=>k.startsWith('techbytes-sketch-v2'))));
  await page.setViewportSize({width:1180,height:820});
  await page.waitForFunction(()=>getComputedStyle(document.querySelector('[data-sketch] canvas')).touchAction.includes('pan-y'));
  check(await canvas.evaluate(e=>getComputedStyle(e).touchAction.includes('pan-y')),'Rotation exits drawing mode');
  check(await page.evaluate(()=>localStorage.getItem(Object.keys(localStorage).find(k=>k.startsWith('techbytes-sketch-v2'))))===saved,'Rotation preserves the normalized sketch');
  await page.setViewportSize({width:390,height:844});await page.goto(base+'?route=collective#11');
  await page.getByRole('button',{name:'Open Student prototype',exact:true}).click();
  let frame=page.frameLocator('.device.expanded iframe');
  check(await page.locator('.device.expanded iframe').getAttribute('src').then(s=>s.endsWith('collective-prototype.html')),'Collective embeds the concrete starter');
  await frame.getByRole('button',{name:'Record one observation',exact:true}).click();
  await frame.getByRole('button',{name:'Use the sample note',exact:true}).click();
  await frame.getByRole('radio',{name:'Need another look',exact:true}).check();
  await frame.getByRole('button',{name:'Review practice note',exact:true}).click();
  check(await frame.getByText('Sample observation',{exact:true}).isVisible(),'Sample provenance retained');
  check(await frame.locator('#reviewClarity').textContent()==='Need another look','Uncertainty reaches review');
  await frame.getByRole('button',{name:'Edit observation',exact:true}).click();
  await frame.getByRole('textbox',{name:'Describe one visible change',exact:true}).fill('The group moved to the left.');
  await frame.getByRole('radio',{name:'Clear enough to describe',exact:true}).check();
  await frame.getByRole('button',{name:'Review practice note',exact:true}).click();
  check(await frame.locator('#reviewObservation').textContent()==='The group moved to the left.','Own note survives review');
  check(await frame.getByText('Your practice observation',{exact:true}).isVisible(),'Edited note is not labeled sample');
  await frame.getByRole('button',{name:'Start again',exact:true}).click();
  await frame.getByRole('button',{name:'Record one observation',exact:true}).click();
  check(await frame.getByRole('textbox',{name:'Describe one visible change',exact:true}).inputValue()==='','Restart clears the practice note');
  check(await frame.locator('input:checked').count()===0,'Restart clears certainty');
  await page.getByRole('button',{name:'Close interactive view'}).click();
  await page.locator('#routeSelect').selectOption('wildcard');
  check(await page.locator('.slide.active [data-figma-link]').getAttribute('href').then(s=>s.includes('4-129')),'Wildcard keeps its original Figma entry');
  await page.getByRole('button',{name:'Open Student prototype',exact:true}).click();
  frame=page.frameLocator('.device.expanded iframe');
  check(await frame.getByRole('heading',{name:'What are you trying to do?'}).isVisible(),'Route switch loads the wildcard starter');
  await page.getByRole('button',{name:'Close interactive view'}).click();await page.locator('#routeSelect').selectOption('collective');
  check(await page.locator('.slide.active [data-figma-link]').getAttribute('href').then(s=>s.includes('26-11')),'Collective points to the new Figma flow');
  check(errors.length===0,errors.join('\n'));
  return {joinScreens:8,tablets,checks:'QR before title, canvas size and overlap, rotation, both prototype routes, observation and uncertainty, edit and restart',errors};
}
