(() => {
  const state={result:null,turn:0,playing:false,frame:null,transition:null};
  const q=(id)=>document.querySelector(id);
  const slider=q("#turn-slider"),reset=q("#reset-button"),prev=q("#previous-button"),play=q("#play-button"),next=q("#next-button"),speed=q("#speed-select"),workspace=q("#simulation-workspace");
  const reducedMotion=window.matchMedia("(prefers-reduced-motion: reduce)");

  function duration(){return Number(speed.value)||850;}
  function updatePlayButton(){play.textContent=state.playing?"Ⅱ":"▶";play.setAttribute("aria-label",state.playing?"Pause simulation":"Play simulation");}
  function cancelFrame(){if(state.frame!==null){cancelAnimationFrame(state.frame);state.frame=null;}}
  function clearTransition(){cancelFrame();state.transition=null;}

  function stop(reason="pause"){
    if(state.transition?.startedAt!==null){
      state.transition.elapsed=Math.min(state.transition.duration,performance.now()-state.transition.startedAt);
      state.transition.startedAt=null;
    }
    cancelFrame();state.playing=false;updatePlayButton();
    window.uiLog?.("animation:cancel",{reason,turn:state.turn});
  }

  function render(turn){
    if(!state.result)return;
    clearTransition();
    state.turn=Math.max(0,Math.min(turn,state.result.turn_count));
    slider.value=String(state.turn);prev.disabled=state.turn===0;reset.disabled=state.turn===0;next.disabled=state.turn>=state.result.turn_count;
    window.renderFlyInTurn(state.result,state.turn);
  }

  function completeTransition(){
    if(!state.transition)return;
    const target=state.transition.toTurn;
    window.uiLog?.("animation:complete",{from_turn:state.transition.fromTurn,to_turn:target});
    state.transition=null;state.turn=target;slider.value=String(target);prev.disabled=target===0;reset.disabled=target===0;next.disabled=target>=state.result.turn_count;
    window.renderFlyInTurn(state.result,target);
  }

  function prepareTransition(){
    if(!state.result||state.turn>=state.result.turn_count)return false;
    const fromTurn=state.turn,toTurn=state.turn+1;
    state.transition={
      fromTurn,toTurn,duration:duration(),elapsed:0,startedAt:null,
      fromProjection:window.projectFlyInTurn(state.result,fromTurn),
      toProjection:window.projectFlyInTurn(state.result,toTurn),
    };
    window.uiLog?.("animation:start",{from_turn:fromTurn,to_turn:toTurn,duration_ms:state.transition.duration});
    return true;
  }

  function frame(timestamp){
    state.frame=null;
    if(!state.playing||!state.transition)return;
    const transition=state.transition;
    if(transition.startedAt===null)transition.startedAt=timestamp-transition.elapsed;
    const elapsed=Math.max(0,timestamp-transition.startedAt);
    transition.elapsed=Math.min(elapsed,transition.duration);
    const progress=transition.duration===0?1:transition.elapsed/transition.duration;
    window.renderFlyInTransition(
      state.result,
      transition.fromTurn,
      transition.toTurn,
      progress,
      transition.fromProjection,
      transition.toProjection,
    );
    if(progress>=1){
      completeTransition();
      if(state.turn>=state.result.turn_count){state.playing=false;updatePlayButton();window.uiLog?.("playback:complete",{turn:state.turn});return;}
      if(!prepareTransition())return;
    }
    state.frame=requestAnimationFrame(frame);
  }

  function advanceReducedMotion(){
    if(!state.playing||!state.result)return;
    if(state.turn>=state.result.turn_count){state.playing=false;updatePlayButton();window.uiLog?.("playback:complete",{turn:state.turn});return;}
    render(state.turn+1);
    if(state.playing)window.setTimeout(advanceReducedMotion,duration());
  }

  function playAnimation(){
    if(!state.result)return;
    if(state.turn>=state.result.turn_count)render(0);
    state.playing=true;updatePlayButton();window.uiLog?.("playback:play",{turn:state.turn,duration_ms:duration()});
    if(reducedMotion.matches){window.uiLog?.("animation:reduced-motion",{enabled:true});window.setTimeout(advanceReducedMotion,duration());return;}
    if(!state.transition&&!prepareTransition())return;
    state.frame=requestAnimationFrame(frame);
  }

  function toggle(){
    if(state.playing){stop("pause");window.uiLog?.("playback:pause",{turn:state.turn});return;}
    playAnimation();
  }

  function load(result,map){
    stop("load");state.result=result;state.turn=0;q("#workspace-map-name").textContent=`#${map.index} · ${map.display_path}`;
    slider.min="0";slider.max=String(result.turn_count);slider.value="0";slider.disabled=false;speed.disabled=false;play.disabled=result.turn_count===0;next.disabled=result.turn_count===0;
    window.renderFlyInOutput(result);workspace.classList.remove("is-hidden");render(0);workspace.scrollIntoView({behavior:"smooth",block:"start"});requestAnimationFrame(()=>window.FlyInCanvas?.fit());
  }

  function clear(){stop("clear");state.result=null;state.turn=0;workspace.classList.add("is-hidden");window.FlyInGraph.resetInspector();window.uiLog?.("simulation:cleared");}

  reset.addEventListener("click",()=>{stop("reset");render(0);window.uiLog?.("playback:reset");});
  prev.addEventListener("click",()=>{stop("previous");render(state.turn-1);window.uiLog?.("playback:previous",{turn:state.turn});});
  next.addEventListener("click",()=>{stop("next");render(state.turn+1);window.uiLog?.("playback:next",{turn:state.turn});});
  play.addEventListener("click",toggle);
  slider.addEventListener("input",()=>{stop("seek");render(Number(slider.value));window.uiLog?.("playback:seek",{turn:state.turn});});
  speed.addEventListener("change",()=>{
    if(state.transition){const fraction=state.transition.duration===0?0:state.transition.elapsed/state.transition.duration;state.transition.duration=duration();state.transition.elapsed=fraction*state.transition.duration;state.transition.startedAt=null;}
    window.uiLog?.("playback:speed-change",{duration_ms:duration()});
  });

  window.FlyInSimulation={load,clear};
})();

(() => {
  const q=(id)=>document.querySelector(id),viewport=q("#graph-viewport"),surface=q("#graph-surface"),plus=q("#zoom-in-button"),minus=q("#zoom-out-button"),fitButton=q("#fit-button");
  const min=.28,max=2.2,step=.15;
  let baseWidth=1600,baseHeight=940,scale=1,drag=false,startX=0,startY=0,left=0,top=0;
  function apply(){surface.style.width=`${Math.round(baseWidth*scale)}px`;surface.style.height=`${Math.round(baseHeight*scale)}px`;minus.disabled=scale<=min;plus.disabled=scale>=max;}
  function zoom(next){const centerX=(viewport.scrollLeft+viewport.clientWidth/2)/(baseWidth*scale),centerY=(viewport.scrollTop+viewport.clientHeight/2)/(baseHeight*scale);scale=Math.max(min,Math.min(max,next));apply();viewport.scrollLeft=Math.max(0,centerX*baseWidth*scale-viewport.clientWidth/2);viewport.scrollTop=Math.max(0,centerY*baseHeight*scale-viewport.clientHeight/2);window.uiLog?.("canvas:zoom",{scale:Number(scale.toFixed(2))});}
  function fit(){if(!viewport.clientWidth||!viewport.clientHeight)return;scale=Math.max(min,Math.min(1,(viewport.clientWidth-36)/baseWidth,(viewport.clientHeight-36)/baseHeight));apply();viewport.scrollLeft=Math.max(0,(surface.offsetWidth-viewport.clientWidth)/2);viewport.scrollTop=Math.max(0,(surface.offsetHeight-viewport.clientHeight)/2);window.uiLog?.("canvas:fit",{scale:Number(scale.toFixed(2)),base_width:baseWidth,base_height:baseHeight});}
  function setBaseSize(width,height){baseWidth=Math.max(1200,Number(width)||1200);baseHeight=Math.max(760,Number(height)||760);apply();}
  plus.addEventListener("click",()=>zoom(scale+step));minus.addEventListener("click",()=>zoom(scale-step));fitButton.addEventListener("click",fit);
  viewport.addEventListener("wheel",(event)=>{if(!event.ctrlKey)return;event.preventDefault();zoom(scale+(event.deltaY<0?step:-step));},{passive:false});
  viewport.addEventListener("mousedown",(event)=>{if(event.button!==0||event.target.closest(".graph-zone,.graph-connection"))return;drag=true;startX=event.clientX;startY=event.clientY;left=viewport.scrollLeft;top=viewport.scrollTop;viewport.classList.add("is-panning");});
  window.addEventListener("mousemove",(event)=>{if(!drag)return;viewport.scrollLeft=left-(event.clientX-startX);viewport.scrollTop=top-(event.clientY-startY);});
  window.addEventListener("mouseup",()=>{if(!drag)return;drag=false;viewport.classList.remove("is-panning");window.uiLog?.("canvas:pan",{left:Math.round(viewport.scrollLeft),top:Math.round(viewport.scrollTop)});});
  window.FlyInCanvas={fit,setBaseSize};apply();
})();