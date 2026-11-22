/*__TIMELINE_CONFIG__*/
/*__GIF_ACCENTS__*/
/*__SOUND_CONFIG__*/
(() => {
  'use strict';
  const svg=document.getElementById('story-svg'), grow=document.getElementById('grow-svg');
  const clock=document.getElementById('clock'), seek=document.getElementById('seek');
  const play=document.getElementById('btn-play'), restart=document.getElementById('btn-restart');
  const follow=document.getElementById('btn-follow'), debug=document.getElementById('btn-debug');
  const markers=document.getElementById('anchor-debug');
  const roots=[svg,grow]; let paused=false, followOn=true, dragging=false, debugOn=false, previousTime=0;
  let syncTransport=()=>{}, tickSound=()=>{};
  const reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let reducedHold=false;
  // GIF frame decoding is not governed by SMIL pause/seek. Treat it as disposable
  // decorative playback: create a fresh in-memory Blob at the arrival cue, detach
  // on pause/exit, restart from frame 1 on resume or timeline seek.
  const gifNodes=new Map(), gifLive=new Map();
  for(const d of GIF_ACCENTS){
    const node=document.getElementById('gif-image-'+d.id);
    if(node) gifNodes.set(d.id,node);
  }
  function stopGif(d){
    const node=gifNodes.get(d.id), url=gifLive.get(d.id);
    if(!url) return;
    if(node) node.removeAttribute('href');
    URL.revokeObjectURL(url);gifLive.delete(d.id);
  }
  function startGif(d){
    const node=gifNodes.get(d.id);
    if(!node)return;
    // A new Blob URL is necessary: changing opacity on a preloaded <image>
    // would not guarantee the GIF starts at its first frame.
    const decoded=atob(d.base64), bytes=new Uint8Array(decoded.length);
    for(let i=0;i<decoded.length;i++)bytes[i]=decoded.charCodeAt(i);
    const url=URL.createObjectURL(new Blob([bytes],{type:'image/gif'}));
    node.setAttribute('href',url);
    gifLive.set(d.id,url);
  }
  function syncGifs(t,restart=false){
    for(const d of GIF_ACCENTS){
      if(restart)stopGif(d);
      const active=!paused && t>=d.begin && t<d.end;
      if(active && !gifLive.has(d.id))startGif(d);
      if(!active)stopGif(d);
    }
  }
  const clamped=t=>Math.min(TIMELINE.duration,Math.max(0,Number(t)||0));
  const toClock=t=>`${Math.floor(t/60).toString().padStart(2,'0')}:${Math.floor(t%60).toString().padStart(2,'0')}`;
  const time=()=>clamped(svg.getCurrentTime());
  function setTime(t){ t=clamped(t); for(const root of roots) root.setCurrentTime(t); syncGifs(t,true);refresh(t); }
  function refresh(t){ clock.textContent=`${toClock(t)} / ${toClock(TIMELINE.duration)}`;
    if(!dragging) seek.value=t;
  }
  function changePlayState(next){ paused=next;for(const root of roots){next?root.pauseAnimations():root.unpauseAnimations();}
    play.textContent=next?'▶ 继续':'Ⅱ 暂停';syncGifs(time(),true);syncTransport();
  }
  function yAt(t){ const index=clamped(t)*4,i=Math.floor(index),f=index-i;
    return TIMELINE.tipYs[Math.min(i,TIMELINE.tipYs.length-1)]*(1-f)+TIMELINE.tipYs[Math.min(i+1,TIMELINE.tipYs.length-1)]*f;
  }
  function followTip(t){ if(!followOn)return;
    const paper=document.getElementById('paper'), stage=document.getElementById('stage');
    const paperTop=paper.getBoundingClientRect().top+window.scrollY;
    const step=paper.clientWidth/TIMELINE.width;
    const storyY=paperTop+yAt(t)*step;
    const desired=Math.max(0,storyY-window.innerHeight*.68);
    const maxScroll=Math.max(0,document.documentElement.scrollHeight-window.innerHeight);
    window.scrollTo(0,Math.min(maxScroll,desired));
  }
  play.addEventListener('click',()=>{
    if(reducedHold){ reducedHold=false; setTime(0); window.scrollTo(0,0); changePlayState(false); return; }
    changePlayState(!paused);
  });
  restart.addEventListener('click',()=>{reducedHold=false;setTime(0);changePlayState(false);window.scrollTo(0,0);});
  seek.addEventListener('pointerdown',()=>dragging=true);
  seek.addEventListener('input',()=>{reducedHold=false;setTime(seek.value);followTip(+seek.value);});
  seek.addEventListener('change',()=>{dragging=false;});
  follow.addEventListener('click',()=>{followOn=!followOn;follow.classList.toggle('selected',followOn);follow.textContent=followOn?'◉ 自动跟随':'◎ 自由滚动';});
  debug.addEventListener('click',()=>{debugOn=!debugOn;if(markers)markers.setAttribute('visibility',debugOn?'visible':'hidden');debug.classList.toggle('selected',debugOn);});
  ['wheel','touchstart'].forEach(event=>window.addEventListener(event,()=>{
    if(followOn){followOn=false;follow.classList.remove('selected');follow.textContent='◎ 自由滚动';}
  },{passive:true}));
  function frame(){let t=time();refresh(t);syncGifs(t);tickSound(t);if(!paused && t<TIMELINE.duration && Math.abs(t-previousTime)>.0001)followTip(t);
    // Do not pause SMIL at the end — looping motifs (e.g. finale fireworks) keep playing.
    previousTime=t;requestAnimationFrame(frame);
  }
  const dockSlot=document.querySelector('.dock-slot');
  const dock=dockSlot?dockSlot.querySelector('.dock'):null;
  const dockPeek=document.getElementById('dock-peek');
  const DOCK_IDLE_MS=2400;
  let dockTimer=0, dockHover=false;
  function dockOpen(){
    if(!dockSlot)return;
    dockSlot.classList.remove('is-collapsed');
    if(dock)dock.removeAttribute('inert');
    if(dockPeek){dockPeek.tabIndex=-1;dockPeek.setAttribute('aria-hidden','true');}
  }
  function dockShut(){
    if(!dockSlot||dockHover||dragging)return;
    if(dock&&dock.contains(document.activeElement))return;
    dockSlot.classList.add('is-collapsed');
    if(dock)dock.setAttribute('inert','');
    if(dockPeek){dockPeek.tabIndex=0;dockPeek.removeAttribute('aria-hidden');}
  }
  function dockArm(){clearTimeout(dockTimer);dockTimer=setTimeout(dockShut,DOCK_IDLE_MS);}
  function dockEnter(){dockHover=true;clearTimeout(dockTimer);dockOpen();}
  function dockLeave(event){
    const next=event.relatedTarget;
    if(next&&dockSlot.contains(next))return;
    dockHover=false;
    if(!dragging)dockArm();
  }
  if(dock&&dockPeek){
    dock.addEventListener('pointerenter',dockEnter);
    dockPeek.addEventListener('pointerenter',dockEnter);
    dockPeek.addEventListener('pointerdown',dockEnter);
    dock.addEventListener('pointerleave',dockLeave);
    dockPeek.addEventListener('pointerleave',dockLeave);
    dock.addEventListener('focusin',()=>{clearTimeout(dockTimer);dockOpen();});
    dock.addEventListener('focusout',event=>{
      if(dock.contains(event.relatedTarget))return;
      if(!dockHover)dockArm();
    });
    dockPeek.addEventListener('focus',()=>{clearTimeout(dockTimer);dockOpen();});
    dockPeek.addEventListener('blur',()=>{if(!dockHover)dockArm();});
    window.addEventListener('pointerup',()=>{if(dragging&&!dockHover)dockArm();});
    if(dock.matches(':hover')||dockPeek.matches(':hover'))dockHover=true;
    else dockArm();
  }
  installSound();
  if(reduced){
    reducedHold=true; followOn=false; follow.classList.remove('selected'); follow.textContent='◎ 自由滚动';
    setTime(TIMELINE.duration); changePlayState(true); play.textContent='▶ 从头播放';
  }
  refresh(reduced ? TIMELINE.duration : 0);requestAnimationFrame(frame);
  function installSound(){
    const soundBtn=document.getElementById('btn-sound');
    if(typeof SOUND==='undefined'||!SOUND||!soundBtn) return;
    let soundOn=false, unlocked=false, skipClick=false, cursor=null;
    const live=[], audio={};
    function paint(){
      soundBtn.setAttribute('aria-pressed',soundOn?'true':'false');
      soundBtn.textContent=soundOn?'♪ 静音':'♪ 声音';
    }
    function noiseBuffer(ctx){
      const n=Math.floor(ctx.sampleRate*2), buf=ctx.createBuffer(1,n,ctx.sampleRate), d=buf.getChannelData(0);
      let b0=0,b1=0,b2=0;
      for(let i=0;i<n;i++){
        const w=Math.random()*2-1;
        b0=0.997*b0+0.029*w; b1=0.985*b1+0.02*w; b2=0.95*b2+0.05*w;
        d[i]=(b0+b1*0.6+b2*0.3)*1.6;
      }
      return buf;
    }
    function ensure(){
      if(audio.ctx) return;
      const Ctx=window.AudioContext||window.webkitAudioContext;
      if(!Ctx) return;
      const ctx=new Ctx();
      audio.ctx=ctx;
      const master=ctx.createGain();
      master.gain.value=0.85;
      master.connect(ctx.destination);
      audio.master=master;
      audio.noise=noiseBuffer(ctx);
      const src=ctx.createBufferSource();
      src.buffer=audio.noise; src.loop=true;
      const filter=ctx.createBiquadFilter();
      filter.type='bandpass'; filter.frequency.value=1300; filter.Q.value=0.4;
      const bed=ctx.createGain(); bed.gain.value=0;
      src.connect(filter); filter.connect(bed); bed.connect(master);
      src.start();
      audio.bed=bed;
    }
    function stopLive(){
      for(const node of live){ try{node.stop();}catch(e){} }
      live.length=0;
    }
    function tone(freq, at, dur, peak, slide){
      const ctx=audio.ctx, o=ctx.createOscillator(), g=ctx.createGain();
      o.type='sine';
      o.frequency.setValueAtTime(freq, at);
      if(slide) o.frequency.exponentialRampToValueAtTime(Math.max(40,slide), at+dur);
      g.gain.setValueAtTime(0.0001, at);
      g.gain.exponentialRampToValueAtTime(peak, at+Math.min(0.03,dur*0.3));
      g.gain.exponentialRampToValueAtTime(0.0001, at+dur);
      o.connect(g); g.connect(audio.master);
      o.start(at); o.stop(at+dur+0.03);
      live.push(o);
    }
    function burst(at, dur, peak, freq, q, slide){
      const ctx=audio.ctx, src=ctx.createBufferSource(), f=ctx.createBiquadFilter(), g=ctx.createGain();
      src.buffer=audio.noise;
      f.type='bandpass'; f.Q.value=q;
      f.frequency.setValueAtTime(freq, at);
      if(slide) f.frequency.exponentialRampToValueAtTime(Math.max(40,slide), at+dur);
      g.gain.setValueAtTime(0.0001, at);
      g.gain.exponentialRampToValueAtTime(peak, at+Math.min(0.03,dur*0.25));
      g.gain.exponentialRampToValueAtTime(0.0001, at+dur);
      src.connect(f); f.connect(g); g.connect(audio.master);
      src.start(at); src.stop(at+dur+0.03);
      live.push(src);
    }
    function play(id){
      if(!audio.ctx) return;
      const at=audio.ctx.currentTime+0.01;
      if(id==='paper') burst(at,0.5,0.08,1700,0.55);
      else if(id==='key'){ burst(at,0.04,0.2,2400,2.2); tone(160,at,0.06,0.07); }
      else if(id==='bell'){ tone(1318,at,1.25,0.06); tone(1976,at,1.05,0.025); }
      else if(id==='gear'){ burst(at,0.07,0.16,360,1.1); burst(at+0.09,0.07,0.14,280,1); }
      else if(id==='pen') burst(at,0.42,0.07,2400,0.7,1000);
      else if(id==='hum'){ tone(58,at,4.6,0.045); tone(116,at,4.6,0.02); }
      else if(id==='wing'){ for(let i=0;i<6;i++) burst(at+i*0.07,0.045,0.045,3400,5); }
      else if(id==='tick') tone(2480,at,0.045,0.07);
      else if(id==='blip'){ tone(523,at,0.1,0.07); tone(784,at+0.13,0.1,0.07); }
      else if(id==='click') burst(at,0.03,0.18,1800,0.8);
      else if(id==='beep') tone(880,at,0.14,0.07);
      else if(id==='beep2') tone(1175,at,0.14,0.07);
      else if(id==='connect'){ tone(440,at,0.16,0.06); tone(554,at+0.16,0.16,0.06); tone(659,at+0.32,0.22,0.05); }
      else if(id==='switch'){ burst(at,0.03,0.16,900,0.8); tone(196,at,0.12,0.05); }
      else if(id==='train') burst(at,1.25,0.075,200,0.45,680);
      else if(id==='notify'){ tone(1568,at,0.1,0.055); tone(2093,at+0.11,0.14,0.04); }
      else if(id==='radio'){ burst(at,0.55,0.12,980,0.35,240); tone(1100,at,0.5,0.04,180); }
      else if(id==='humback'){ tone(62,at,2.2,0.05); tone(124,at,2.2,0.02); }
      else if(id==='gpu') tone(320,at,0.5,0.07,980);
      else if(id==='glass'){ tone(1568,at,1.5,0.04); tone(2093,at,1.35,0.028); tone(2637,at,1.2,0.018); }
      else if(id==='keys'){ for(let i=0;i<4;i++) burst(at+i*0.11,0.035,0.12,2000+i*180,2); }
      else if(id==='rocket') burst(at,1.45,0.09,130,0.4,560);
      else if(id==='warm'){ tone(392,at,1.8,0.05); tone(494,at,1.7,0.038); tone(587,at,1.6,0.03); }
    }
    function bedLevel(t){
      const b=SOUND.bed;
      if(!b) return 0;
      if(t<b.start) return 0;
      let level=Math.min(1,(t-b.start)/0.8);
      if(t>=b.silence[0] && t<b.silence[1]) level=0;
      if(t>=b.fadeOut) level*=Math.max(0,1-(t-b.fadeOut)/b.fadeDur);
      return level*0.03;
    }
    function updateBed(t){
      if(!audio.bed) return;
      const now=audio.ctx.currentTime, g=audio.bed.gain;
      g.cancelScheduledValues(now);
      g.setValueAtTime(g.value, now);
      g.linearRampToValueAtTime(soundOn&&!paused?bedLevel(t):0, now+0.12);
    }
    syncTransport=function(){
      if(!audio.ctx) return;
      if(soundOn && !paused){ if(audio.ctx.state==='suspended') audio.ctx.resume(); }
      else if(audio.ctx.state==='running') audio.ctx.suspend();
      updateBed(time());
    };
    tickSound=function(t){
      if(!soundOn||!audio.ctx) return;
      if(cursor==null){ cursor=t; updateBed(t); return; }
      const delta=t-cursor;
      if(!paused && !dragging && delta>0 && delta<0.5){
        for(const cue of SOUND.cues){ if(cue.t>cursor && cue.t<=t) play(cue.id); }
      }else if(Math.abs(delta)>=0.5 || delta<0) stopLive();
      cursor=t;
      updateBed(t);
    };
    function turnOn(){
      ensure();
      if(!audio.ctx) return;
      soundOn=true; cursor=time(); paint(); syncTransport();
    }
    function turnOff(){ soundOn=false; stopLive(); paint(); syncTransport(); }
    if(dockSlot) dockSlot.addEventListener('pointerdown',event=>{
      if(unlocked) return;
      unlocked=true;
      if(event.target===soundBtn||soundBtn.contains(event.target)) skipClick=true;
      turnOn();
    });
    soundBtn.addEventListener('click',()=>{
      unlocked=true;
      if(skipClick){ skipClick=false; return; }
      if(soundOn) turnOff(); else turnOn();
    });
    paint();
  }
})();
