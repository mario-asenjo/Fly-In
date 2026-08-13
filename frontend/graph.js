(() => {
  const NS = "http://www.w3.org/2000/svg";
  const canvas = document.querySelector("#graph-canvas");
  const placeholder = document.querySelector("#graph-placeholder");
  const inspector = document.querySelector("#inspector-content");
  const svg = (name, attrs = {}) => {
    const node = document.createElementNS(NS, name);
    Object.entries(attrs).forEach(([key, value]) => node.setAttribute(key, String(value)));
    return node;
  };
  const edgeKey = (a, b) => a < b ? `${a}::${b}` : `${b}::${a}`;
  const zoneKind = (zone, map) => zone.name === map.start ? "start" : zone.name === map.end ? "end" : zone.kind;
  const kindLabel = (kind) => ({start:"START",end:"END",normal:"NORMAL",priority:"PRIORITY",restricted:"RESTRICTED",blocked:"BLOCKED"}[kind] ?? kind.toUpperCase());
  const kindColor = (kind) => ({start:"#06b6d4",end:"#10b981",normal:"#3b82f6",priority:"#f59e0b",restricted:"#8b5cf6",blocked:"#64748b"}[kind] ?? "#3b82f6");

  function points(zones) {
    const xs = zones.map((z) => z.x), ys = zones.map((z) => z.y);
    const minX = Math.min(...xs), maxX = Math.max(...xs), minY = Math.min(...ys), maxY = Math.max(...ys);
    const sx = Math.max(1, maxX - minX), sy = Math.max(1, maxY - minY);
    const scale = Math.min(950 / sx, 500 / sy), usedX = sx * scale, usedY = sy * scale;
    return new Map(zones.map((z) => [z.name, {
      x: (1200 - usedX) / 2 + (z.x - minX) * scale,
      y: 700 - ((700 - usedY) / 2 + (z.y - minY) * scale),
    }]));
  }

  function inspect(image, title, rows) {
    inspector.className = "inspector-content";
    inspector.replaceChildren();
    const card = document.createElement("div"); card.className = "inspector-card";
    const img = document.createElement("img"); img.src = image; img.alt = "";
    const body = document.createElement("div"), heading = document.createElement("strong"), dl = document.createElement("dl");
    heading.textContent = title;
    rows.forEach(([label, value]) => {
      const dt = document.createElement("dt"), dd = document.createElement("dd");
      dt.textContent = label; dd.textContent = value; dl.append(dt, dd);
    });
    body.append(heading, dl); card.append(img, body); inspector.append(card);
  }

  function connection(layer, item, pts, projection) {
    const a = pts.get(item.left), b = pts.get(item.right), dx = b.x-a.x, dy = b.y-a.y;
    const distance = Math.max(90, Math.hypot(dx,dy)), angle = Math.atan2(dy,dx)*180/Math.PI;
    const occupied = projection.links.get(edgeKey(item.left,item.right)) ?? [];
    const g = svg("g", {class:`graph-connection${occupied.length?" is-active":""}`,transform:`translate(${(a.x+b.x)/2} ${(a.y+b.y)/2}) rotate(${angle})`,tabindex:0,role:"button"});
    const image = svg("image", {href:"img/conn.svg",x:-distance/2,y:-24,width:distance,height:48,preserveAspectRatio:"none"});
    const label = svg("text", {class:"connection-label",x:0,y:-31}); label.textContent=`↔ ${item.capacity}${occupied.length?` · ${occupied.length} flying`:""}`;
    const open = () => { inspect("img/conn.svg",`${item.left} ↔ ${item.right}`,[['Capacity',item.capacity],['In transit',occupied.length],['Drones',occupied.length?occupied.map((id)=>`D${id}`).join(', '):'none']]); window.uiLog?.("connection:select",{connection:[item.left,item.right],occupied}); };
    g.addEventListener("click",open); g.addEventListener("keydown",(e)=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();open();}});
    g.append(image,label); layer.append(g);
  }

  function zone(layer, item, point, projection, map) {
    const kind = zoneKind(item,map), occupied = projection.zones.get(item.name) ?? [];
    const g=svg("g",{class:"graph-zone",transform:`translate(${point.x} ${point.y})`,tabindex:0,role:"button"});
    const halo=svg("rect",{x:-82,y:-41,width:164,height:78,rx:21,fill:kindColor(kind),opacity:.14});
    const image=svg("image",{href:"img/zone.svg",x:-78,y:-34,width:156,height:67});
    const badge=svg("rect",{x:-34,y:-39,width:68,height:16,rx:8,fill:kindColor(kind)});
    const name=svg("text",{class:"zone-name",x:0,y:-4}); name.textContent=item.name.length>16?`${item.name.slice(0,14)}…`:item.name;
    const meta=svg("text",{class:"zone-meta",x:0,y:16}); meta.textContent=`${item.capacity} cap · ${occupied.length} here`;
    const type=svg("text",{class:"zone-kind-badge",x:0,y:-27}); type.textContent=kindLabel(kind);
    const open=()=>{inspect("img/zone.svg",`${kindLabel(kind)} · ${item.name}`,[['Coordinates',`(${item.x}, ${item.y})`],['Capacity',item.capacity],['Color',item.color??'default'],['Drones',occupied.length?occupied.map((id)=>`D${id}`).join(', '):'none']]);window.uiLog?.("zone:select",{zone:item.name,occupied});};
    g.addEventListener("click",open);g.addEventListener("keydown",(e)=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();open();}});
    g.append(halo,image,badge,name,meta,type);layer.append(g);
  }

  function dronePoint(position, pts, index, count) {
    if(position.type==="transit") { const a=pts.get(position.origin),b=pts.get(position.destination),dx=b.x-a.x,dy=b.y-a.y,l=Math.max(1,Math.hypot(dx,dy)),o=(index-(count-1)/2)*24; return{x:(a.x+b.x)/2-dy/l*o,y:(a.y+b.y)/2+dx/l*o}; }
    const c=pts.get(position.zone),cols=Math.min(5,Math.ceil(Math.sqrt(count))),row=Math.floor(index/cols),col=index%cols,rowCount=Math.min(cols,count-row*cols);
    return{x:c.x+(col-(rowCount-1)/2)*34,y:c.y+48+row*34};
  }

  function drones(layer, projection, pts, map) {
    const buckets=new Map(); projection.positions.forEach((position,id)=>{const k=position.type==="transit"?`t:${edgeKey(position.origin,position.destination)}`:`z:${position.zone}`,list=buckets.get(k)??[];list.push({id,position});buckets.set(k,list);});
    buckets.forEach((list)=>list.forEach(({id,position},index)=>{const p=dronePoint(position,pts,index,list.length),icon=position.type==="delivered"?"happy":position.type==="zone"&&position.zone===map.start?"sad":"normal";const image=svg("image",{class:"drone-node",href:`img/${icon}.svg`,x:p.x-18,y:p.y-18,width:36,height:36}),label=svg("text",{class:"drone-id",x:p.x,y:p.y+25});label.textContent=`D${id}`;layer.append(image,label);}));
  }

  function render(map, projection) {
    const pts=points(map.zones); canvas.replaceChildren(); placeholder.classList.add("is-hidden");
    const title=svg("title");title.textContent="Fly-In map";const links=svg("g"),zones=svg("g"),fleet=svg("g");canvas.append(title,links,zones,fleet);
    map.connections.forEach((item)=>connection(links,item,pts,projection));map.zones.forEach((item)=>zone(zones,item,pts.get(item.name),projection,map));drones(fleet,projection,pts,map);
  }
  function resetInspector(){inspector.className="inspector-empty";inspector.textContent="Select a zone or connection to inspect its current capacity and occupancy.";}
  window.FlyInGraph={render,resetInspector,edgeKey};
})();
