(() => {
  const viewport=document.querySelector("#graph-viewport");
  const surface=document.querySelector("#graph-surface");
  const zoomIn=document.querySelector("#zoom-in-button");
  const zoomOut=document.querySelector("#zoom-out-button");
  const fitButton=document.querySelector("#fit-button");
  const baseWidth=1600,baseHeight=940,min=.65,max=1.8,step=.15;
  let scale=1,dragging=false,startX=0,startY=0,left=0,top=0;
  function apply(){surface.style.width=`${baseWidth*scale}px`;surface.style.height=`${baseHeight*scale}px`;zoomOut.disabled=scale<=min;zoomIn.disabled=scale>=max;}
  function zoom(next){scale=Math.max(min,Math.min(max,next));apply();window.uiLog?.("canvas:zoom",{scale});}
  function fit(){scale=Math.max(min,Math.min(1,(viewport.clientWidth-24)/baseWidth,(viewport.clientHeight-24)/baseHeight));apply();viewport.scrollLeft=Math.max(0,(surface.offsetWidth-viewport.clientWidth)/2);viewport.scrollTop=Math.max(0,(surface.offsetHeight-viewport.clientHeight)/2);window.uiLog?.("canvas:fit",{scale});}
  zoomIn.addEventListener("click",()=>zoom(scale+step));
  zoomOut.addEventListener("click",()=>zoom(scale-step));
  fitButton.addEventListener("click",fit);
  viewport.addEventListener("mousedown",(event)=>{if(event.button!==0||event.target.closest(".graph-zone,.graph-connection"))return;dragging=true;startX=event.clientX;startY=event.clientY;left=viewport.scrollLeft;top=viewport.scrollTop;viewport.classList.add("is-panning");});
  window.addEventListener("mousemove",(event)=>{if(!dragging)return;viewport.scrollLeft=left-(event.clientX-startX);viewport.scrollTop=top-(event.clientY-startY);});
  window.addEventListener("mouseup",()=>{if(!dragging)return;dragging=false;viewport.classList.remove("is-panning");window.uiLog?.("canvas:pan",{left:viewport.scrollLeft,top:viewport.scrollTop});});
  apply();window.FlyInCanvas={fit};
})();
