(()=>{
  const NS="http://www.w3.org/2000/svg";
  const canvas=document.querySelector("#graph-canvas");
  const placeholder=document.querySelector("#graph-placeholder");
  const inspector=document.querySelector("#inspector-content");
  const X_STEP=142,Y_STEP=156,PAD_X=190,PAD_Y=170,NODE_W=104,NODE_H=42;
  let droneLayer=null,currentPoints=null,currentMap=null;

  const svg=(name,attrs={})=>{
    const node=document.createElementNS(NS,name);
    Object.entries(attrs).forEach(([key,value])=>node.setAttribute(key,String(value)));
    return node;
  };
  const edgeKey=(a,b)=>a<b?`${a}::${b}`:`${b}::${a}`;
  const kindOf=(zone,map)=>zone.name===map.start?"start":zone.name===map.end?"end":zone.kind;
  const kindColor=(kind)=>({start:"#06b6d4",end:"#10b981",normal:"#3b82f6",priority:"#f59e0b",restricted:"#8b5cf6",blocked:"#64748b"}[kind]||"#3b82f6");
  const kindLabel=(kind)=>({start:"START",end:"END",normal:"NORMAL",priority:"PRIORITY",restricted:"RESTRICTED",blocked:"BLOCKED"}[kind]||kind.toUpperCase());
  const safeColor=(value,fallback)=>value&&value!=="rainbow"&&CSS.supports("color",value)?value:fallback;
  const clamp01=(value)=>Math.max(0,Math.min(1,value));
  const lerp=(from,to,progress)=>from+(to-from)*progress;

  function layout(zones){
    const xs=zones.map(zone=>zone.x),ys=zones.map(zone=>zone.y);
    const minX=Math.min(...xs),maxX=Math.max(...xs),minY=Math.min(...ys),maxY=Math.max(...ys);
    const width=Math.max(1200,PAD_X*2+(maxX-minX)*X_STEP);
    const height=Math.max(760,PAD_Y*2+(maxY-minY)*Y_STEP);
    return {
      width,height,
      points:new Map(zones.map(zone=>[
        zone.name,
        {x:PAD_X+(zone.x-minX)*X_STEP,y:PAD_Y+(maxY-zone.y)*Y_STEP}
      ]))
    };
  }

  function showInspector(title,rows,color){
    inspector.className="inspector-popover";
    inspector.replaceChildren();
    const shell=document.createElement("div"),stripe=document.createElement("span"),body=document.createElement("div"),heading=document.createElement("strong"),list=document.createElement("dl");
    shell.style.cssText="display:grid;grid-template-columns:10px 1fr;gap:12px";
    stripe.style.cssText=`border-radius:9px;background:${color}`;
    heading.textContent=title;
    list.style.cssText="display:grid;grid-template-columns:auto 1fr;gap:4px 10px;margin:7px 0 0;font-size:.75rem";
    rows.forEach(([key,value])=>{
      const dt=document.createElement("dt"),dd=document.createElement("dd");
      dt.textContent=key;dt.style.color="#7890ad";
      dd.textContent=String(value);dd.style.cssText="margin:0;text-align:right;font-weight:750";
      list.append(dt,dd);
    });
    body.append(heading,list);shell.append(stripe,body);inspector.append(shell);
  }

  function renderConnection(layer,connection,points,projection){
    const left=points.get(connection.left),right=points.get(connection.right);
    const transit=projection.links.get(edgeKey(connection.left,connection.right))||[];
    const group=svg("g",{class:"graph-connection",tabindex:0,role:"button"});
    group.dataset.edge=edgeKey(connection.left,connection.right);
    const hit=svg("line",{x1:left.x,y1:left.y,x2:right.x,y2:right.y,stroke:"transparent","stroke-width":24});
    const line=svg("line",{x1:left.x,y1:left.y,x2:right.x,y2:right.y,stroke:transit.length?"#19bddd":"#9ebfdf","stroke-width":transit.length?8:5,"stroke-linecap":"round","vector-effect":"non-scaling-stroke"});
    group.append(hit,line);
    if(connection.capacity>1||transit.length){
      const x=(left.x+right.x)/2,y=(left.y+right.y)/2;
      const badge=svg("g",{transform:`translate(${x} ${y})`}),background=svg("rect",{x:-18,y:-10,width:36,height:20,rx:10,fill:"#fff",stroke:"#b9cfe7"}),text=svg("text",{x:0,y:4,"text-anchor":"middle","font-size":10,"font-weight":900,fill:"#315d96"});
      text.textContent=transit.length?`✈${transit.length}`:`×${connection.capacity}`;
      badge.append(background,text);group.append(badge);
    }
    const inspect=()=>{
      showInspector(`${connection.left} ↔ ${connection.right}`,[
        ["Capacity",connection.capacity],["In transit",transit.length],
        ["Drones",transit.length?transit.map(id=>`D${id}`).join(", "):"none"]
      ],"#38bdf8");
      window.uiLog?.("connection:select",{connection:[connection.left,connection.right],occupied:transit});
    };
    group.addEventListener("click",inspect);
    group.addEventListener("keydown",event=>{if(event.key==="Enter"||event.key===" "){event.preventDefault();inspect();}});
    layer.append(group);
  }

  function renderZone(layer,zone,point,projection,map){
    const kind=kindOf(zone,map),semantic=kindColor(kind),metadata=safeColor(zone.color,semantic),drones=projection.zones.get(zone.name)||[];
    const group=svg("g",{class:"graph-zone",transform:`translate(${point.x} ${point.y})`,tabindex:0,role:"button"});
    const shadow=svg("rect",{x:-NODE_W/2,y:-NODE_H/2+3,width:NODE_W,height:NODE_H,rx:14,fill:"rgba(19,55,109,.14)"});
    const outer=svg("rect",{x:-NODE_W/2,y:-NODE_H/2,width:NODE_W,height:NODE_H,rx:14,fill:metadata,opacity:.88});
    const inner=svg("rect",{x:-NODE_W/2+4,y:-NODE_H/2+4,width:NODE_W-8,height:NODE_H-8,rx:11,fill:"#fff"});
    const marker=svg("circle",{cx:-NODE_W/2+12,cy:0,r:5,fill:semantic,stroke:"#fff","stroke-width":2});
    const text=svg("text",{x:4,y:4,"text-anchor":"middle","font-size":12,"font-weight":850,fill:"#153b71"});
    text.textContent=zone.name.length>14?`${zone.name.slice(0,12)}…`:zone.name;
    group.append(shadow,outer,inner,marker,text);
    if(zone.capacity>1||drones.length){
      const badge=svg("g",{transform:`translate(${NODE_W/2-4} ${-NODE_H/2+3})`}),circle=svg("circle",{r:12,fill:"#12376d",stroke:"#fff","stroke-width":2}),count=svg("text",{x:0,y:4,"text-anchor":"middle",fill:"#fff","font-size":9,"font-weight":900});
      count.textContent=drones.length?drones.length:zone.capacity;badge.append(circle,count);group.append(badge);
    }
    const inspect=()=>{
      showInspector(`${kindLabel(kind)} · ${zone.name}`,[
        ["Coordinates",`(${zone.x}, ${zone.y})`],["Capacity",zone.capacity],
        ["Color",zone.color||"default"],["Drones",drones.length?drones.map(id=>`D${id}`).join(", "):"none"]
      ],semantic);
      window.uiLog?.("zone:select",{zone:zone.name,occupied:drones});
    };
    group.addEventListener("click",inspect);
    group.addEventListener("keydown",event=>{if(event.key==="Enter"||event.key===" "){event.preventDefault();inspect();}});
    layer.append(group);
  }

  function bucketKey(position){
    return position.type==="transit"?`t:${edgeKey(position.origin,position.destination)}`:`z:${position.zone}`;
  }

  function bucketIndexes(projection){
    const buckets=new Map(),indexes=new Map();
    projection.positions.forEach((position,id)=>{
      const key=bucketKey(position),list=buckets.get(key)||[];
      list.push(id);buckets.set(key,list);
    });
    buckets.forEach(ids=>ids.forEach((id,index)=>indexes.set(id,{index,count:ids.length})));
    return indexes;
  }

  function positionPoint(position,points,index,count){
    if(position.type==="transit"){
      const left=points.get(position.origin),right=points.get(position.destination);
      const dx=right.x-left.x,dy=right.y-left.y,length=Math.max(1,Math.hypot(dx,dy));
      const offset=(index-(count-1)/2)*24;
      return {x:(left.x+right.x)/2-dy/length*offset,y:(left.y+right.y)/2+dx/length*offset};
    }
    const point=points.get(position.zone),columns=Math.min(4,Math.ceil(Math.sqrt(count))),row=Math.floor(index/columns),column=index%columns,rowCount=Math.min(columns,count-row*columns);
    return {x:point.x+(column-(rowCount-1)/2)*28,y:point.y+34+row*28};
  }

  function droneIcon(position,map,moving=false){
    if(position.type==="delivered")return"happy";
    if(!moving&&position.type==="zone"&&position.zone===map.start)return"sad";
    return"normal";
  }

  function appendDrone(layer,id,position,point,map,moving=false){
    const icon=svg("image",{href:`img/${droneIcon(position,map,moving)}.svg`,x:point.x-14,y:point.y-14,width:28,height:28});
    const label=svg("text",{x:point.x,y:point.y+19,"text-anchor":"middle","font-size":9,"font-weight":900,fill:"#14366a",stroke:"#fff","stroke-width":3,"paint-order":"stroke"});
    label.textContent=`D${id}`;layer.append(icon,label);
  }

  function renderDrones(layer,projection,points,map){
    const buckets=new Map();
    projection.positions.forEach((position,id)=>{
      const key=bucketKey(position),list=buckets.get(key)||[];
      list.push({id,position});buckets.set(key,list);
    });
    buckets.forEach(entries=>{
      if(entries.length>5){
        const point=positionPoint(entries[0].position,points,0,1);
        const icon=svg("image",{href:`img/${droneIcon(entries[0].position,map)}.svg`,x:point.x-17,y:point.y+23,width:34,height:34});
        const bubble=svg("circle",{cx:point.x+16,cy:point.y+25,r:11,fill:"#12376d",stroke:"#fff","stroke-width":2});
        const count=svg("text",{x:point.x+16,y:point.y+29,"text-anchor":"middle",fill:"#fff","font-size":8,"font-weight":900});
        count.textContent=`×${entries.length}`;layer.append(icon,bubble,count);return;
      }
      entries.forEach((entry,index)=>appendDrone(layer,entry.id,entry.position,positionPoint(entry.position,points,index,entries.length),map));
    });
  }

  function renderMovingDrones(fromProjection,toProjection,progress){
    if(!droneLayer||!currentPoints||!currentMap)return;
    droneLayer.replaceChildren();
    const fromIndexes=bucketIndexes(fromProjection),toIndexes=bucketIndexes(toProjection),t=clamp01(progress);
    fromProjection.positions.forEach((fromPosition,id)=>{
      const toPosition=toProjection.positions.get(id)||fromPosition;
      const fromIndex=fromIndexes.get(id)||{index:0,count:1},toIndex=toIndexes.get(id)||{index:0,count:1};
      const start=positionPoint(fromPosition,currentPoints,fromIndex.index,fromIndex.count);
      const end=positionPoint(toPosition,currentPoints,toIndex.index,toIndex.count);
      const moving=bucketKey(fromPosition)!==bucketKey(toPosition);
      const point={x:lerp(start.x,end.x,t),y:lerp(start.y,end.y,t)};
      const visualPosition=t>=1?toPosition:(moving?{...toPosition,type:toPosition.type}:fromPosition);
      appendDrone(droneLayer,id,visualPosition,point,currentMap,moving&&t<1);
    });
  }

  function render(map,projection){
    const geometry=layout(map.zones);
    canvas.setAttribute("viewBox",`0 0 ${geometry.width} ${geometry.height}`);
    canvas.replaceChildren();placeholder.classList.add("is-hidden");
    window.FlyInCanvas?.setBaseSize(geometry.width,geometry.height);
    const edges=svg("g"),zones=svg("g"),drones=svg("g");
    canvas.append(edges,zones,drones);
    map.connections.forEach(connection=>renderConnection(edges,connection,geometry.points,projection));
    map.zones.forEach(zone=>renderZone(zones,zone,geometry.points.get(zone.name),projection,map));
    renderDrones(drones,projection,geometry.points,map);
    droneLayer=drones;currentPoints=geometry.points;currentMap=map;
    window.uiLog?.("graph:layout",{width:geometry.width,height:geometry.height,zones:map.zones.length,connections:map.connections.length,x_step:X_STEP,y_step:Y_STEP});
  }

  function renderTransition(map,fromProjection,toProjection,progress){
    if(currentMap!==map||!droneLayer){
      render(map,fromProjection);
    }
    renderMovingDrones(fromProjection,toProjection,progress);
  }

  function resetInspector(){
    inspector.className="inspector-popover inspector-empty";
    inspector.textContent="Select a zone or connection to inspect it.";
  }

  window.FlyInGraph={render,renderTransition,resetInspector,edgeKey};
})();