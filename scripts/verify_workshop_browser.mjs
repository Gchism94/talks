// Serve docs at 127.0.0.1:8765, then run with playwright-cli run-code --filename.
// All poll calls are intercepted: this suite never writes to the live classroom.
async (page) => {
  const assert=(value,message)=>{if(!value)throw Error(message);};
  const base='http://127.0.0.1:8765/design-what-you-know/';
  const errors=[],layouts=[],saved=new Map();
  page.on('pageerror',e=>errors.push(e.message));
  await page.emulateMedia({reducedMotion:'reduce'});
  await page.route('https://techbytes-sketch-gallery.gchism.chatgpt.site/api/**',async route=>{
    const req=route.request(),url=req.url();
    assert(url.split('?')[0]==='https://techbytes-sketch-gallery.gchism.chatgpt.site/api/poll','No gallery mutation in layout suite');
    const body=req.method()==='POST'?req.postDataJSON():null;
    const question=body?.question||/[?&]question=([^&]*)/.exec(url)?.[1];
    if(body)saved.set(question,body.score);
    await route.fulfill({contentType:'application/json',body:JSON.stringify({open:true,revealed:false,total:saved.has(question)?1:0,mine:saved.get(question)??null,bins:null})});
  });
  for(const route of ['collective','wildcard']){
    for(const [width,height] of [[320,568],[375,667],[390,844],[430,932],[844,390],[932,430],[1280,720],[1440,900]]){
      await page.setViewportSize({width,height});
      await page.goto(base+'?route='+route+'#1');
      for(let n=1;n<=13;n++){
        await page.evaluate(n=>location.hash='#'+n+'.99',n);
        await page.waitForFunction(n=>document.querySelector('#counter').textContent.startsWith(String(n).padStart(2,'0')),n);
        const compact=width<=900||height<=540;
        const layout=await page.locator('.slide.active').evaluate(el=>{
          const f=el.querySelector('.frame').getBoundingClientRect();
          return {top:f.top,bottom:f.bottom,overflow:el.scrollWidth>el.clientWidth+1,scrollable:['auto','scroll'].includes(getComputedStyle(el).overflowY)};
        });
        assert(!layout.overflow,`Horizontal overflow ${route}/${n} ${width}×${height}`);
        if(compact){
          assert(layout.scrollable,`Compact slide cannot scroll ${width}×${height}`);
          await page.locator('.slide.active').evaluate(el=>el.scrollTop=el.scrollHeight);
          const bottom=await page.locator('.slide.active .frame').evaluate(el=>el.getBoundingClientRect().bottom);
          const footer=await page.locator('.footer').boundingBox();
          assert(bottom<=footer.y+1,`Content trapped beneath footer ${route}/${n} ${width}×${height}`);
        }else if(!(layout.top>=60&&layout.bottom<=height-60))errors.push(`Desktop slide clipping ${route}/${n} ${width}×${height}: ${layout.top}–${layout.bottom}`);
        layouts.push({route,n,width,height,...layout});
      }
    }
  }
  await page.setViewportSize({width:390,height:844});
  await page.goto(base+'#3');
  const poll=page.locator('[data-native-poll=maps]');
  await poll.getByRole('radio',{name:'Both',exact:true}).check();
  await page.keyboard.press('ArrowRight');
  assert(page.url().split('#')[1]==='3','Poll keys must not advance slides');
  assert(await poll.getByRole('radio',{name:'Leans epistēmē',exact:true}).isChecked(),'Radio keyboard navigation');
  await poll.getByRole('button',{name:'Save response',exact:true}).click();
  await page.waitForFunction(()=>document.querySelector('[data-native-poll=maps] .poll-status').textContent.includes('saved'));
  assert(saved.get('maps-google')===3,'Response uses intercepted API fixture');
  await poll.getByRole('button',{name:'Apple Maps',exact:true}).click();
  assert(await poll.locator('input:checked').count()===0,'Comparison has no default answer');
  await page.getByRole('button',{name:'Open workshop menu'}).click();
  assert(await page.getByRole('link',{name:'All talks',exact:true}).isVisible(),'Collection link available');
  assert(await page.locator('.talk-outline a').count()===13,'Complete outline');
  await page.getByRole('button',{name:'Close workshop menu'}).click();
  await page.locator('#routeSelect').selectOption('wildcard');await page.reload();
  assert(await page.locator('#routeSelect').inputValue()==='wildcard','Route survives reload');
  assert(await page.locator('#notesBtn').isHidden(),'Public notes control hidden');
  await page.keyboard.press('n');
  assert(!await page.locator('#notes').evaluate(el=>el.open),'Public notes keyboard gate');
  assert(errors.length===0,errors.join('\n'));
  return {layouts:layouts.length,checks:'routes, landscape reachability, native poll fixture, menu, notes',errors};
}
