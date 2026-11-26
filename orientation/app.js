import {slides,sections,ui} from './content.js';
const $=id=>document.getElementById(id);
const read=(key,fallback)=>{try{return localStorage.getItem(key)||fallback}catch{return fallback}};
const save=(key,value)=>{try{localStorage.setItem(key,value)}catch{}};
let lang=document.documentElement.lang;
if(!['ko','en'].includes(lang))lang='ko';
let theme=read('vux-orientation-theme','system');
if(!['system','light','dark'].includes(theme))theme='system';
let current=Math.max(0,Math.min(slides.length-1,(parseInt(location.hash.slice(1))||1)-1));
const mode=new URLSearchParams(location.search).get('mode');
let reading=mode!=='present',dialogKind='',observer;
document.body.classList.toggle('reading',reading);
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const t=x=>typeof x==='object'?x[lang]:x;
const text=x=>esc(t(x)).replace(/\n/g,'<br>');
const list=items=>`<ul>${items.map(x=>`<li>${text(x)}</li>`).join('')}</ul>`;
const columns=items=>`<div class="columns">${items.map(([n,title,body])=>`<div class="column"><span class="item-number">${n}</span><h2>${text(title)}</h2><p>${text(body)}</p></div>`).join('')}</div>`;
const rows=items=>`<div class="rows">${items.map(([title,body])=>`<div class="row"><h2>${text(title)}</h2><p>${text(body)}</p></div>`).join('')}</div>`;
function content(s){
 switch(s.type){
 case 'cover':return `<div class="cover-layout"><div><p class="cover-subtitle">${text(s.subtitle)}</p><p class="lead">${text(s.lead)}</p><p class="cover-note">${text(s.note)}</p></div><div class="eight" aria-hidden="true"><span>08</span><small>WEEKS</small><svg viewBox="0 0 300 70"><path d="M0 35h35l8-7 9 14 10-25 10 38 10-44 10 48 10-53 10 58 10-48 10 35 10-23 10 15 10-8h113" fill="none" stroke="currentColor" stroke-width="1.5"/></svg></div></div><div class="slide-bottom">${text(s.meta)}</div>`;
 case 'columns':case 'scope':return `${s.lead?`<p class="lead">${text(s.lead)}</p>`:''}${columns(s.items)}${bottom(s)}`;
 case 'credits':return `<p class="lead">${text(s.lead)}</p><div class="credit-grid">${[s.left,s.right].map(c=>`<div><h2>${text(c.title)}</h2><p class="credit-amount">${text(c.amount)}</p>${list(c.items)}</div>`).join('')}</div><p class="credit-clarification">${text(s.clarification)}</p>${bottom(s)}<div class="credit-source"><span>${text(s.sourceLabel)}</span><span>${s.sources.map(x=>`<a href="${esc(x.url)}" target="_blank" rel="noopener">${text(x.label)} ↗</a>`).join(' · ')}</span></div>`;
 case 'contrast':return `<p class="lead">${text(s.lead)}</p><div class="contrast"><div><h2>${text(s.left.title)}</h2>${list(s.left.items)}</div><div><h2>${text(s.right.title)}</h2>${list(s.right.items)}</div></div>`;
 case 'prompt':case 'question':return `<p class="lead">${text(s.lead)}</p><div class="prompts">${s.items.map((x,i)=>`<div><span>0${i+1}</span><p>${text(x)}</p></div>`).join('')}</div>${bottom(s)}`;
 case 'concept':case 'workflow':return `<p class="lead">${text(s.lead)}</p><div class="flow">${s.items.map((x,i)=>`<div><span>0${i+1}</span><h2>${text(x)}</h2></div>`).join('')}</div>${bottom(s)}`;
 case 'ladder':return `<p class="quote">${text(s.lead)}</p><ol class="ladder">${s.items.map((x,i)=>`<li><span>0${i+1}</span><h2>${text(x)}</h2></li>`).join('')}</ol>${bottom(s)}`;
 case 'rows':case 'agreements':case 'evaluation':case 'premortem':return `${s.lead?`<p class="lead">${text(s.lead)}</p>`:''}${rows(s.items)}${bottom(s)}`;
 case 'weeks':return `<p class="lead">${text(s.lead)}</p><div class="weeks">${s.items.map(([n,title,body])=>`<div><span class="week">Week ${n}</span><h2>${text(title)}</h2><p>${text(body)}</p></div>`).join('')}</div>`;
 case 'gates':return `<div class="gates">${s.items.map(([n,title,body])=>`<div><span>${n}</span><h2>${text(title)}</h2><p>${text(body)}</p></div>`).join('')}</div>${bottom(s)}`;
 case 'checklist':return `<ol class="checklist">${s.items.map((x,i)=>`<li><span>0${i+1}</span><p>${text(x)}</p></li>`).join('')}</ol>${bottom(s)}`;
 case 'close':return `<p class="lead">${text(s.lead)}</p><div class="closing-items">${s.items.map((x,i)=>`<span><small>0${i+1}</small>${text(x)}</span>`).join('')}</div>${bottom(s)}`;
 }
}
function bottom(s){return s.bottom?`<div class="slide-bottom">${text(s.bottom)}</div>`:''}
function render(){
 document.documentElement.lang=lang;
 document.title=lang==='ko'?'Voice UX Lab — 팀 오리엔테이션':'Voice UX Lab — Team Orientation';
 $('main').innerHTML=(reading ? $('archive-intro').innerHTML : '')+slides.map((s,i)=>`<article class="slide slide-${s.type}" id="slide-${i+1}" aria-labelledby="title-${i+1}" ${!reading&&i!==current?'hidden':''}><div class="eyebrow"><span>${String(i+1).padStart(2,'0')} / ${text(s.label)}</span>${['concept','weeks','gates'].includes(s.type)?`<span class="proposal">${text(ui.status)}</span>`:''}</div><h2 class="slide-title" id="title-${i+1}">${text(s.title)}</h2>${content(s)}</article>`).join('')+(reading ? $('archive-links').innerHTML : '');
 $('sections').innerHTML=sections.map((s,i)=>`<button data-section="${i}"><span>0${i+1}</span>${text(s)}</button>`).join('');
 document.querySelectorAll('[data-section]').forEach(b=>b.onclick=()=>go(slides.findIndex(s=>s.section===Number(b.dataset.section))));
 for(const id of ['ko','en']){if(id===lang)$(id).setAttribute('aria-current','page');else $(id).removeAttribute('aria-current')}

 $('prev').textContent='← '+t(ui.prev);$('next').textContent=t(ui.next)+' →';
 $('notes').textContent=t(ui.notes);$('help').textContent=t(ui.help);$('view').textContent=t(reading?ui.present:ui.read);
 $('overview').setAttribute('aria-label',t(ui.overview));$('overview').title=t(ui.overview);
 $('fullscreen').setAttribute('aria-label',t(ui.fullscreen));$('fullscreen').title=t(ui.fullscreen);
 $('dialog-close').textContent=t(ui.close)+' ×';
 applyTheme();update();observe();
 if($('drawer').open)openDialog(dialogKind);
}
function update(){
 document.querySelectorAll('.slide').forEach((el,i)=>{el.hidden=!reading&&i!==current});
 document.querySelectorAll('[data-section]').forEach(b=>{if(Number(b.dataset.section)===slides[current].section)b.setAttribute('aria-current','step');else b.removeAttribute('aria-current')});
 $('counter').textContent=`${String(current+1).padStart(2,'0')} / ${slides.length}`;
 $('progress').style.width=`${(current+1)/slides.length*100}%`;
 $('prev').disabled=current===0;$('next').disabled=current===slides.length-1;
 const url=new URL(location.href); if(reading) url.searchParams.delete('mode'); else url.searchParams.set('mode','present'); url.hash=current===0?'':String(current+1);
 history.replaceState(null,'',url);
 for(const [id,path] of [['ko','orientation.ko.html'],['en','orientation.html']]) $(id).href=path+url.search+url.hash;
}
function go(i){current=Math.max(0,Math.min(slides.length-1,i));update();if(reading)$(`slide-${current+1}`).scrollIntoView({behavior:'instant'});else $(`slide-${current+1}`).scrollTop=0;}
function observe(){observer?.disconnect();if(!reading)return;observer=new IntersectionObserver(entries=>{for(const e of entries){if(e.isIntersecting){current=Number(e.target.id.split('-')[1])-1;update()}}},{rootMargin:'-15% 0px -70% 0px'});document.querySelectorAll('.slide').forEach(el=>observer.observe(el))}
function applyTheme(){const mode=theme==='system'?(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light'):theme;document.documentElement.dataset.theme=mode;$('theme').textContent=(theme==='system'?'◐':theme==='dark'?'●':'○')+' '+t(ui[theme]);$('theme').setAttribute('aria-label',t(ui.appearance)+': '+t(ui[theme]));}
function cycleTheme(){theme=['system','light','dark'][(['system','light','dark'].indexOf(theme)+1)%3];save('vux-orientation-theme',theme);applyTheme();}
function setLang(value){if(value!==lang)location.assign($(value).href)}
function toggleView(){reading=!reading;document.body.classList.toggle('reading',reading);render();if(reading)$(`slide-${current+1}`).scrollIntoView({behavior:'instant'});else window.scrollTo(0,0)}
function openDialog(kind){dialogKind=kind;$('dialog-title').textContent=t(ui[kind]);if(kind==='overview'){
 $('dialog-content').innerHTML=`<div class="overview-grid">${slides.map((s,i)=>`<button data-jump="${i}" ${i===current?'aria-current="true"':''}><span>${String(i+1).padStart(2,'0')}</span><strong>${text(s.label)}</strong><small>${text(s.title)}</small></button>`).join('')}</div><button id="print">${text(ui.print)}</button>`;
 document.querySelectorAll('[data-jump]').forEach(b=>b.onclick=()=>{$('drawer').close();go(Number(b.dataset.jump))});$('print').onclick=()=>{$('drawer').close();window.print()};
 }else{$('dialog-content').innerHTML=`<p class="note-slide">${String(current+1).padStart(2,'0')} / ${text(slides[current].label)}</p><p class="speaker-copy">${text(slides[current].notes)}</p><p class="note-hint">${lang==='ko'?'발표자 노트는 이 창에서만 보입니다. 화면을 공유할 때 확인하세요.':'These notes are visible in this window. Check before sharing your screen.'}</p>`}
 if(!$('drawer').open)$('drawer').showModal();
}
async function fullscreen(){try{if(document.fullscreenElement)await document.exitFullscreen();else await document.documentElement.requestFullscreen()}catch{$('fullscreen').title=lang==='ko'?'브라우저의 전체 화면 기능을 사용하세요.':'Use the browser fullscreen control.'}}
 $('theme').onclick=cycleTheme;$('view').onclick=toggleView;$('prev').onclick=()=>go(current-1);$('next').onclick=()=>go(current+1);$('notes').onclick=()=>openDialog('notes');$('overview').onclick=()=>openDialog('overview');$('dialog-close').onclick=()=>$('drawer').close();$('fullscreen').onclick=fullscreen;
 $('drawer').addEventListener('click',e=>{if(e.target===$('drawer')){const r=$('drawer').getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)$('drawer').close()}});
 addEventListener('hashchange',()=>{const n=parseInt(location.hash.slice(1));if(n>=1&&n<=slides.length)go(n-1)});
 addEventListener('keydown',e=>{if($('drawer').open||e.ctrlKey||e.metaKey||e.altKey||['INPUT','TEXTAREA','SELECT'].includes(e.target.tagName)||e.target.isContentEditable)return;
 const key=e.key.toLowerCase();
 if(reading && ['arrowright','arrowleft','pagedown','pageup','home','end',' '].includes(key))return;
 if(['arrowright','pagedown'].includes(key)||(key===' '&&!['BUTTON','A'].includes(e.target.tagName))){e.preventDefault();go(current+1)}
 else if(['arrowleft','pageup'].includes(key)){e.preventDefault();go(current-1)}
 else if(key==='home'){e.preventDefault();go(0)}else if(key==='end'){e.preventDefault();go(slides.length-1)}
 else if(key==='o')openDialog('overview');else if(key==='n')openDialog('notes');else if(key==='t')cycleTheme();else if(key==='l')setLang(lang==='ko'?'en':'ko');else if(key==='f')fullscreen();
 });
 matchMedia('(prefers-color-scheme:dark)').addEventListener('change',()=>{if(theme==='system')applyTheme()});
 render();
 if(reading && current>0)requestAnimationFrame(()=>$(`slide-${current+1}`).scrollIntoView());
