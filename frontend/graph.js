(()=>{
  const NS="http://www.w3.org/2000/svg";
  const canvas=document.querySelector("#graph-canvas");
  const placeholder=document.querySelector("#graph-placeholder");
  const inspector=document.querySelector("#inspector-content");

  const X_STEP=205;
  const Y_STEP=190;
  const PAD_X=170;
  const PAD_Y=155;
  const NODE_R=19;

  const svg=(name,attrs={})=>{
    const element=document.createElementNS(NS,name);
    Object.entries(attrs).forEach(([key,value])=>element.setAttribute(key,String(value)));
    return element;
  };
  const edgeKey=(a,b)=>a<b?`${a}::${b}`:`${b}::${a}`;
  const kindOf=(zone,map)=>zone.name===map.start?"start":zone.name===map.end?"end":zone.kind;
  const kindColor=(kind)=>({
    start:"#06b6d4",end:"#10b981",normal:"#3b82f6",
    priority:"#f59e0b",restricted:"#8b5cf6",blocked:"#64748b"
  }[kind]||"#3b82f6");
  const kindGlyph=(kind)=>({start:"S",end:"E",normal:"N",priority:"P",restricted:"R",blocked:"×"}[kind]||"N");
  const kindLabel=(kind)=>({start:"START",end:"END",normal:"NORMAL",priority:"PRIORITY",restricted:"RESTRICTED",blocked:"BLOCKED"}[kind]||kind.toUpperCase());
  const safeColor=(value,fallback)=>value&&value!=="rainbow"&&CSS.supports("color",value)?value:fallback;

  function layout(zones){
    const xs=zones.map(zone=>zone.x),ys=zones.map(zone=>zone.y);
    const minX=Math.min(...xs),maxX=Math.max(...xs),minY=Math.min(...ys),maxY=Math.max(...ys);
    const width=Math.max(1200,PAD_X*2+(maxX-minX)*X_STEP);
    const height=Math.max(760,PAD_Y*2+(maxY-minY)*Y_STEP);
    return {
      width,
      height,
      points:new Map(zones.map(zone=>[
        zone.name,
        {x:PAD_X+(zone.x-minX)*X_STEP,y:PAD_Y+(maxY-zone.y)*Y_STEP}
      ]))
    };
  }

  function showInspector(title,rows,color){
    inspector.className="inspector-popover";
    inspector.replaceChildren();
    const shell=document.createElement("div");
    const stripe=document.createElement("span");
    const body=document.createElement("div");
    const heading=document.createElement("strong");
    const list=document.createElement("dl");
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
    const hit=svg("line",{x1:left.x,y1:left.y,x2:right.x,y2:right.y,stroke:"transparent","stroke-width":22});
    const line=svg("line",{
      x1:left.x,y1:left.y,x2:right.x,y2:right.y,
      stroke:transit.length?"#12b8d2":"#a8c3df",
      "stroke-width":transit.length?6:3,
      "stroke-linecap":"round","vector-effect":"non-scaling-stroke"
    });
    group.append(hit,line);

    if(connection.capacity>1||transit.length){
      const x=(left.x+right.x)/2,y=(left.y+right.y)/2;
      const badge=svg("g",{transform:`translate(${x} ${y})`});
      const circle=svg("circle",{r:12,fill:transit.length?"#0f91ad":"#ffffff",stroke:"#9dbbd9","stroke-width":1.5});
      const text=svg("text",{x:0,y:3.5,"text-anchor":"middle","font-size":8.5,"font-weight":900,fill:transit.length?"#fff":"#315d96"});
      text.textContent=transit.length?String(transit.length):`×${connection.capacity}`;
      badge.append(circle,text);group.append(badge);
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

  function renderBadge(group,x,y,text,fill){
    const badge=svg("g",{transform:`translate(${x} ${y})`});
    const circle=svg("circle",{r:10,fill,stroke:"#fff","stroke-width":2});
    const label=svg("text",{x:0,y:3.5,"text-anchor":"middle",fill:"#fff","font-size":8,"font-weight":900});
    label.textContent=text;badge.append(circle,label);group.append(badge);
  }

  function renderZone(layer,zone,point,projection,map){
    const kind=kindOf(zone,map),semantic=kindColor(kind),metadata=safeColor(zone.color,semantic);
    const drones=projection.zones.get(zone.name)||[];
    const group=svg("g",{class:"graph-zone",transform:`translate(${point.x} ${point.y})`,tabindex:0,role:"button"});
    const halo=svg("circle",{r:NODE_R+6,fill:metadata,opacity:.18});
    const outer=svg("circle",{r:NODE_R+2,fill:"#fff",stroke:metadata,"stroke-width":4});
    const core=svg("circle",{r:NODE_R-4,fill:semantic});
    const glyph=svg("text",{x:0,y:4.5,"text-anchor":"middle","font-size":11,"font-weight":950,fill:"#fff"});
    glyph.textContent=kindGlyph(kind);
    const name=svg("text",{x:0,y:NODE_R+19,"text-anchor":"middle","font-size":10.5,"font-weight":800,fill:"#264f82"});
    name.textContent=zone.name;
    group.append(halo,outer,core,glyph,name);

    if(zone.capacity>1&&zone.name!==map.start&&zone.name!==map.end){
      renderBadge(group,NODE_R+8,-NODE_R-5,String(zone.capacity),"#496f9e");
    }
    if(drones.length){
      renderBadge(group,NODE_R+8,NODE_R+4,String(drones.length),"#0eaf76");
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

  function dronePoint(position,points,index,count){
    if(position.type==="transit"){
      const a=points.get(position.origin),b=points.get(position.destination);
      const dx=b.x-a.x,dy=b.y-a.y,length=Math.max(1,Math.hypot(dx,dy));
      const offset=(index-(count-1)/2)*18;
      return {x:(a.x+b.x)/2-dy/length*offset,y:(a.y+b.y)/2+dx/length*offset};
    }
    const point=points.get(position.zone);
    const columns=Math.min(4,Math.ceil(Math.sqrt(count)));
    const row=Math.floor(index/columns),column=index%columns;
    return {x:point.x+(column-(Math.min(columns,count-row*columns)-1)/2)*18,y:point.y+42+row*17};
  }

  function droneIcon(position,map){
    if(position.type==="delivered")return"happy";
    if(position.type==="zone"&&position.zone===map.start)return"sad";
    return"normal";
  }

  function renderDrones(layer,projection,points,map){
    const groups=new Map();
    projection.positions.forEach((position,id)=>{
      const key=position.type==="transit"?`t:${edgeKey(position.origin,position.destination)}`:`z:${position.zone}`;
      const entries=groups.get(key)||[];entries.push({id,position});groups.set(key,entries);
    });
    groups.forEach(entries=>{
      if(entries.length>4){
        const point=dronePoint(entries[0].position,points,0,1);
        const icon=svg("image",{href:`img/${droneIcon(entries[0].position,map)}.svg`,x:point.x-12,y:point.y-12,width:24,height:24});
        const bubble=svg("circle",{cx:point.x+12,cy:point.y-9,r:9,fill:"#153b71",stroke:"#fff","stroke-width":2});
        const count=svg("text",{x:point.x+12,y:point.y-6,"text-anchor":"middle",fill:"#fff","font-size":7,"font-weight":900});
        count.textContent=`×${entries.length}`;layer.append(icon,bubble,count);return;
      }
      entries.forEach((entry,index)=>{
        const point=dronePoint(entry.position,points,index,entries.length);
        const icon=svg("image",{href:`img/${droneIcon(entry.position,map)}.svg`,x:point.x-10,y:point.y-10,width:20,height:20});
        const id=svg("text",{x:point.x,y:point.y+17,"text-anchor":"middle","font-size":7.5,"font-weight":900,fill:"#14366a",stroke:"#fff","stroke-width":2.5,"paint-order":"stroke"});
        id.textContent=`D${entry.id}`;layer.append(icon,id);
      });
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
    window.uiLog?.("graph:layout",{
      width:geometry.width,height:geometry.height,zones:map.zones.length,
      connections:map.connections.length,x_step:X_STEP,y_step:Y_STEP,renderer:"native-compact"
    });
  }

  function resetInspector(){
    inspector.className="inspector-popover inspector-empty";
    inspector.textContent="Select a zone or connection to inspect it.";
  }
  window.FlyInGraph={render,resetInspector,edgeKey};
})();