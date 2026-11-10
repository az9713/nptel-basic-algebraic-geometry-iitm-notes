document.addEventListener('DOMContentLoaded',()=>{
  const chart=document.querySelector('#curve-chart');if(!chart)return;
  const mode=document.querySelector('#curve-mode'), slider=document.querySelector('#curve-parameter'),out=document.querySelector('#curve-output');
  const point=(kind,t)=>kind==='cusp'?[t*t,t*t*t]:[t*t-1,t*(t*t-1)];
  function draw(){
    const kind=mode.value,t=Number(slider.value),width=680,height=420;
    const X=x=>70+(x+1.4)*160,Y=y=>210-y*55;
    const values=Array.from({length:301},(_,i)=>-1.5+i/100);
    const points=values.map(z=>point(kind,z).map((v,j)=>(j?Y(v):X(v)).toFixed(3)).join(',')).join(' ');
    const [x,y]=point(kind,t),dx=2*t,dy=kind==='cusp'?3*t*t:3*t*t-1;
    const gx=kind==='cusp'?-3*x*x:-(3*x*x+2*x),gy=2*y;
    const singular=Math.abs(gx)+Math.abs(gy)<1e-9;
    let tangent='';
    if(Math.abs(dx)+Math.abs(dy)>1e-9){
      const scale=0.3/Math.hypot(dx,dy),a=[x-scale*dx,y-scale*dy],b=[x+scale*dx,y+scale*dy];
      tangent='<line x1="'+X(a[0])+'" y1="'+Y(a[1])+'" x2="'+X(b[0])+'" y2="'+Y(b[1])+'" stroke="#f3c76d" stroke-width="3"/>';
    }
    chart.innerHTML='<title>Real '+kind+' with parametrized point and tangent direction</title><desc>The cyan curve is sampled from its polynomial parametrization. A gold segment shows its parametrized tangent direction when the velocity is nonzero.</desc><line x1="30" y1="210" x2="650" y2="210" stroke="#617184"/><line x1="'+X(0)+'" y1="20" x2="'+X(0)+'" y2="400" stroke="#617184"/><text x="646" y="232" fill="currentColor">x</text><text x="'+(X(0)+10)+'" y="25" fill="currentColor">y</text><polyline points="'+points+'" fill="none" stroke="#7ed9c5" stroke-width="2.5"/>'+tangent+'<circle cx="'+X(x)+'" cy="'+Y(y)+'" r="6" fill="#f3c76d"/>';
    const fmt=v=>Math.abs(v)<0.0000005?'0':v.toFixed(3);
    out.textContent='t = '+fmt(t)+'. Point ('+fmt(x)+', '+fmt(y)+'). Parametrized velocity ('+fmt(dx)+', '+fmt(dy)+'). Gradient of defining equation ('+fmt(gx)+', '+fmt(gy)+'). '+(singular?'Singular point: the Zariski tangent space has dimension 2.':'Nonsingular point: the Zariski tangent space has dimension 1.');
  }
  slider.addEventListener('input',draw);mode.addEventListener('change',()=>{slider.value='0';draw()});draw();
});
