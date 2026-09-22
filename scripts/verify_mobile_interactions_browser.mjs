// Browser regression for the reported phone failures. All remote writes are mocked.
async (page) => {
  const check=(ok,message)=>{if(!ok)throw Error(message);};
  const base='http://127.0.0.1:8765/design-what-you-know/';
  const errors=[],submissions=[];page.on('pageerror',e=>errors.push(e.message));
  await page.emulateMedia({reducedMotion:'reduce'});
  await page.route('https://techbytes-sketch-gallery.gchism.chatgpt.site/api/**',async r=>{
    if(r.request().method()==='POST')submissions.push(r.request().postDataJSON());
    await r.fulfill({contentType:'application/json',body:JSON.stringify({open:true,revealed:false,total:0,mine:null,ok:true})});
  });
  for(const pattern of ['https://collective-movement.vercel.app/**','https://www.google.com/maps/embed**','https://open.spotify.com/embed/**'])await page.route(pattern,r=>r.fulfill({contentType:'text/html',body:'<h1>App fixture</h1><button>Pause</button>'}));
  for(const [width,height] of [[320,568],[390,844],[412,915],[932,430]]){
    await page.setViewportSize({width,height});await page.goto(base+'#1');await page.reload();
    const birds=page.locator('[data-embed=birds]');
    await birds.scrollIntoViewIfNeeded();
    check(await birds.locator('iframe').count()===0,'No automatic phone simulation');
    for(const [n,kind] of [[1,'birds'],[3,'maps'],[4,'spotify'],[6,'collective'],[9,'practice'],[10,'figma'],[11,'figma']]){
      await page.goto(base+'#'+n);
      const device=page.locator('.slide.active [data-embed='+kind+']');
      await device.locator('.load-embed').click();
      check(await device.evaluate(e=>e.classList.contains('expanded')),'Launch card opens full screen');
      const frame=device.locator('iframe'),box=await frame.boundingBox();
      check(box.width>=width-40&&box.height>=height-180,`Usable app viewport ${kind}/${width}`);
      if(kind==='birds')check((await frame.getAttribute('src')).includes('embed=title'),'Bird scene stays storage-free');
      check(await device.locator('.overlay-external').isVisible(),'Escape link available');
      await device.getByRole('button',{name:'Close interactive view'}).click();
      check(await device.locator('.load-embed').isVisible(),'Launch card restored');
      check(await device.locator('.load-embed').evaluate(e=>e===document.activeElement),'Focus returns to visible launch button');
      check(!await frame.isVisible(),'No squashed live iframe after close');
    }
    await page.goto(base+'#5');
    const fits=await page.locator('.choice-flow').evaluate(el=>{
      const r=el.getBoundingClientRect();return [...el.children].every(c=>{const b=c.getBoundingClientRect();return b.left>=r.left-1&&b.right<=r.right+1&&c.scrollWidth<=c.clientWidth+1;});
    });check(fits,'Wildcard diagram children fit their card');
    if(width<=600){const cards=await page.locator('.route-choices button').evaluateAll(es=>es.map(e=>e.getBoundingClientRect().toJSON()));check(cards[1].top>=cards[0].bottom,'Phone choices are stacked');}
    await page.goto(base+'#10');
    check(await page.locator('.slide.active .mobile-task-action').evaluate(e=>getComputedStyle(e).color!==getComputedStyle(e).backgroundColor),'Slide 10 button text contrasts with background');
  }
  await page.setViewportSize({width:390,height:844});await page.goto(base+'#8');await page.reload();
  const canvas=page.locator('[data-sketch] canvas');
  check(await canvas.evaluate(e=>getComputedStyle(e).touchAction.includes('pan-y')),'Canvas scrolls before opting in');
  await page.getByRole('button',{name:'Draw',exact:true}).click();
  await canvas.scrollIntoViewIfNeeded();
  check(await canvas.evaluate(e=>getComputedStyle(e).touchAction)==='none','Drawing mode owns only the canvas gesture');
  await canvas.evaluate(e=>{window.sketchResizeCount=0;new MutationObserver(ms=>window.sketchResizeCount+=ms.length).observe(e,{attributes:true,attributeFilter:['width','height']});});
  const box=await canvas.boundingBox();
  await page.mouse.move(box.x+20,box.y+30);await page.mouse.down();
  await page.mouse.move(box.x+box.width-20,box.y+box.height-30,{steps:200});await page.mouse.up();
  await page.getByRole('button',{name:'Done drawing',exact:true}).click();
  check(await canvas.evaluate(e=>getComputedStyle(e).touchAction.includes('pan-y')),'Done restores scrolling');
  check(await page.evaluate(()=>window.sketchResizeCount)<5,'No bitmap reset for each pointer move');
  const saved=await page.evaluate(()=>JSON.parse(localStorage.getItem(Object.keys(localStorage).find(k=>k.startsWith('techbytes-sketch-v2')))));
  check(saved.strokes.length===1&&saved.strokes[0].length>100,'Drawing persisted after pointer release');
  await page.reload();
  check(await page.getByRole('button',{name:'Draw',exact:true}).isVisible(),'Reload restores safe scroll mode');
  check(await page.evaluate(()=>JSON.parse(localStorage.getItem(Object.keys(localStorage).find(k=>k.startsWith('techbytes-sketch-v2')))).strokes[0].length)===saved.strokes[0].length,'Reload preserves all drawing points');
  await page.getByRole('textbox',{name:'A short title',exact:true}).fill('Browser fixture sketch');
  await page.getByRole('textbox',{name:'The idea, and why it might help',exact:true}).fill('Keep phone drawing optional and easy to exit.');
  await page.getByRole('checkbox').check();
  await page.getByRole('button',{name:'Submit idea',exact:true}).click();
  await page.getByText('Saved to the classroom gallery.',{exact:false}).waitFor();
  check(submissions.length===1&&submissions[0].sketch.strokes.length===1,'Mocked submission preserves the sketch');
  await page.getByRole('button',{name:'Undo',exact:true}).click();
  check(await page.evaluate(()=>JSON.parse(localStorage.getItem(Object.keys(localStorage).find(k=>k.startsWith('techbytes-sketch-v2')))).strokes.length)===0,'Undo remains responsive');
  await page.locator('#next').click();check(page.url().endsWith('#9'),'Slide navigation works after drawing');
  check(errors.length===0,errors.join('\n'));
  return {appViews:28,checks:'launch cards, no phone autoplay, wildcard fit, slide 10 contrast, drawing, recovery, mocked submit, undo, navigation',errors};
}
