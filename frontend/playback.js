(() => {
  const s={result:null,turn:0,timer:null};
  const q=(id)=>document.querySelector(id);
  const slider=q("#turn-slider"),reset=q("#reset-button"),prev=q("#previous-button"),play=q("#play-button"),next=q("#next-button"),speed=q("#speed-select"),workspace=q("#simulation-workspace");
  function stop(){if(s.timer!==null){clearInterval(s.timer);s.timer=null}play.textContent="▶";play.setAttribute("aria-label","Play simulation")}
  function render(turn){if(!s.result)return;s.turn=Math.max(0,Math.min(turn,s.result.turn_count));slider.value=String(s.turn);prev.disabled=s.turn===0;reset.disabled=s.turn===0;next.disabled=s.turn>=s.result.turn_count;window.renderFlyInTurn(s.result,s.turn)}
  function load(result,map){stop();s.result=result;s.turn=0;q("#workspace-map-name").textContent=`#${map.index} · ${map.display_path}`;slider.min="0";slider.max=String(result.turn_count);slider.value="0";slider.disabled=false;speed.disabled=false;play.disabled=result.turn_count===0;next.disabled=result.turn_count===0;window.renderFlyInOutput(result);render(0);workspace.classList.remove("is-hidden");workspace.scrollIntoView({behavior:"smooth",block:"start"});requestAnimationFrame(()=>window.FlyInCanvas?.fit())}
  function clear(){stop();s.result=null;s.turn=0;workspace.classList.add("is-hidden");window.FlyInGraph.resetInspector();window.uiLog?.("simulation:cleared")}
  function toggle(){if(!s.result)return;if(s.timer!==null){stop();window.uiLog?.("playback:pause",{turn:s.turn});return}if(s.turn>=s.result.turn_count)render(0);const delay=Number(speed.value);play.textContent="Ⅱ";play.setAttribute("aria-label","Pause simulation");s.timer=setInterval(()=>{if(s.turn>=s.result.turn_count){stop();window.uiLog?.("playback:complete",{turn:s.turn});return}render(s.turn+1)},delay);window.uiLog?.("playback:play",{turn:s.turn,delay_ms:delay})}
  reset.addEventListener("click",()=>{stop();render(0);window.uiLog?.("playback:reset")});prev.addEventListener("click",()=>{stop();render(s.turn-1);window.uiLog?.("playback:previous",{turn:s.turn})});next.addEventListener("click",()=>{stop();render(s.turn+1);window.uiLog?.("playback:next",{turn:s.turn})});play.addEventListener("click",toggle);slider.addEventListener("input",()=>{stop();render(Number(slider.value));window.uiLog?.("playback:seek",{turn:s.turn})});speed.addEventListener("change",()=>{const running=s.timer!==null;stop();if(running)toggle();window.uiLog?.("playback:speed-change",{delay_ms:Number(speed.value)})});
  window.FlyInSimulation={load,clear};
})();

(() => {
  const q=(id)=>document.querySelector(id),viewport=q("#graph-viewport"),surface=q("#graph-surface"),plus=q("#zoom-in-button"),minus=q("#zoom-out-button"),fitButton=q("#fit-button");
  const baseWidth=1600,baseHeight=940,min=.65,max=1.8,step=.15;let scale=1,drag=false,startX=0,startY=0,left=0,top=0;
  function apply(){surface.style.width=`${Math.round(baseWidth*scale)}px`;surface.style.height=`${Math.round(baseHeight*scale)}px`;minus.disabled=scale<=min;plus.disabled=scale>=max}
  function zoom(next){scale=Math.max(min,Math.min(max,next));apply();window.uiLog?.("canvas:zoom",{scale:Number(scale.toFixed(2))})}
  function fit(){scale=Math.max(min,Math.min(1,(viewport.clientWidth-24)/baseWidth,(viewport.clientHeight-24)/baseHeight));apply();viewport.scrollLeft=Math.max(0,(surface.offsetWidth-viewport.clientWidth)/2);viewport.scrollTop=Math.max(0,(surface.offsetHeight-viewport.clientHeight)/2);window.uiLog?.("canvas:fit",{scale:Number(scale.toFixed(2))})}
  plus.addEventListener("click",()=>zoom(scale+step));minus.addEventListener("click",()=>zoom(scale-step));fitButton.addEventListener("click",fit);
  viewport.addEventListener("mousedown",(event)=>{if(event.button!==0||event.target.closest(".graph-zone,.graph-connection"))return;drag=true;startX=event.clientX;startY=event.clientY;left=viewport.scrollLeft;top=viewport.scrollTop;viewport.classList.add("is-panning")});
  window.addEventListener("mousemove",(event)=>{if(!drag)return;viewport.scrollLeft=left-(event.clientX-startX);viewport.scrollTop=top-(event.clientY-startY)});
  window.addEventListener("mouseup",()=>{if(!drag)return;drag=false;viewport.classList.remove("is-panning");window.uiLog?.("canvas:pan",{left:Math.round(viewport.scrollLeft),top:Math.round(viewport.scrollTop)})});
  window.FlyInCanvas={fit};apply();
})();
