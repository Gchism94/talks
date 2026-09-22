// Serve docs at 127.0.0.1:8765; run with playwright-cli run-code --filename.
// External apps/polls use fixtures. Test real providers separately.
async (page) => {
  const check=(value,message)=>{if(!value)throw Error(message);};
  const base='http://127.0.0.1:8765/design-what-you-know/';
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.emulateMedia({reducedMotion:'reduce'});
  await page.route('https://techbytes-sketch-gallery.gchism.chatgpt.site/api/**',r=>r.fulfill({contentType:'application/json',body:JSON.stringify({open:true,revealed:false,total:0,mine:null})}));
  await page.route('https://collective-movement.vercel.app/**',r=>r.fulfill({contentType:'text/html',body:`<h1>Local simulation fixture</h1><button>Pause</button><script>addEventListener('message',e=>{if(e.data.type==='collective:pause')document.querySelector('button').textContent='Play'});<\/script>`}));
  for(const [width,height] of [[320,568],[390,844],[932,430]]){
    await page.setViewportSize({width,height});await page.goto(base+'#6');await page.reload();
    await page.getByRole('button',{name:'Open Collective',exact:true}).click();
    const device=page.locator('.device.expanded'),close=device.getByRole('button',{name:'Close interactive view'});
    await page.frameLocator('.device.expanded iframe').getByRole('heading',{name:'Local simulation fixture'}).waitFor();
    const rect=await close.boundingBox();
    check(rect.width>=44&&rect.height>=44&&rect.y>=0&&rect.x+rect.width<=width,'Visible close control');
    check(await device.getByRole('link',{name:'Open separately ↗'}).isVisible(),'Fallback inside overlay');
    check(await page.locator('header.chrome').evaluate(e=>e.inert),'Background inert');
    await close.click();
    check(await page.locator('[data-embed=collective] .load-embed').evaluate(e=>e===document.activeElement),'First-open focus return');
    await page.frameLocator('[data-embed=collective] iframe').getByRole('button',{name:'Play',exact:true,includeHidden:true}).waitFor({state:'attached'});
    check(await page.locator('[data-embed=collective] iframe').count()===1,'App frame retained');
    await page.locator('#next').click();check(page.url().split('#')[1]==='7','Compact navigation skips reveals');
  }
  await page.setViewportSize({width:390,height:844});await page.goto(base+'?route=wildcard#6');
  await page.getByRole('button',{name:'Open Student prototype',exact:true}).click();
  const starter=page.frameLocator('.device.expanded iframe');
  await starter.getByRole('button',{name:'Try the next step'}).click();
  await starter.getByRole('radio',{name:'A quieter place'}).check();
  await starter.getByRole('button',{name:'See the outcome'}).click();
  check(await starter.getByRole('heading',{name:'Did that help?'}).isVisible(),'Outcome reachable');
  await starter.getByRole('button',{name:'Change my choice'}).click();
  check(await starter.getByRole('radio',{name:'A quieter place'}).isChecked(),'Choice retained');
  await starter.getByRole('button',{name:'See the outcome'}).click();
  await starter.getByRole('button',{name:'Start again'}).click();
  check(await starter.getByRole('heading',{name:'What are you trying to do?'}).isVisible(),'Restart works');
  check(await page.locator('.device.expanded').getByRole('link',{name:'Open Figma ↗'}).isVisible(),'Figma link retained');
  await page.getByRole('button',{name:'Close interactive view'}).click();
  check(await page.locator('.slide.active [data-route=wildcard] .load-embed').evaluate(e=>e===document.activeElement),'Starter focus return');
  check(errors.length===0,errors.join('\n'));
  return {checks:'overlay, fallback, pause, focus, landscape, accessible starter complete flow',errors};
}
