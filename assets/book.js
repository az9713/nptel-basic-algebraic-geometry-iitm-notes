document.addEventListener('DOMContentLoaded',()=>{
  const narrow=matchMedia('(max-width:760px)');
  const collapse=()=>{if(narrow.matches)document.querySelector('aside details')?.removeAttribute('open')};
  collapse();narrow.addEventListener('change',collapse);
  const stored=localStorage.getItem('ag-theme');if(stored==='light')document.documentElement.classList.add('light');
  document.querySelector('[data-action="theme"]')?.addEventListener('click',()=>{document.documentElement.classList.toggle('light');localStorage.setItem('ag-theme',document.documentElement.classList.contains('light')?'light':'dark')});
  document.querySelector('[data-action="print"]')?.addEventListener('click',()=>window.print());
  document.querySelectorAll('pre').forEach(pre=>{const wrap=document.createElement('div');wrap.className='codewrap';pre.before(wrap);wrap.append(pre);const b=document.createElement('button');b.className='copybtn';b.textContent='Copy';b.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(pre.textContent);b.textContent='Copied';setTimeout(()=>b.textContent='Copy',1500)}catch{b.textContent='Select text to copy'}});wrap.append(b)});
  const field=document.querySelector('#search');field?.addEventListener('input',()=>{const query=field.value.toLowerCase().trim();document.querySelectorAll('[data-search]').forEach(item=>item.hidden=!item.dataset.search.includes(query))});
  let printState=[];
  window.addEventListener('beforeprint',()=>{printState=[...document.querySelectorAll('details')].map(d=>[d,d.open]);printState.forEach(([d])=>d.open=true)});
  window.addEventListener('afterprint',()=>{printState.forEach(([d,open])=>d.open=open)});
});
