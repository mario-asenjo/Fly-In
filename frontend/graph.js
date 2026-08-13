(() => {
  const NS = "http://www.w3.org/2000/svg";
  const canvas = document.querySelector("#graph-canvas");
  const placeholder = document.querySelector("#graph-placeholder");
  const inspector = document.querySelector("#inspector-content");
  const X_STEP = 142;
  const Y_STEP = 156;
  const PAD_X = 190;
  const PAD_Y = 170;
  const NODE_W = 104;
  const NODE_H = 42;

  const svg = (name, attrs = {}) => {
    const node = document.createElementNS(NS, name);
    Object.entries(attrs).forEach(([key, value]) => node.setAttribute(key, String(value)));
    return node;
  };
  const edgeKey = (a, b) => a < b ? `${a}::${b}` : `${b}::${a}`;
  const zoneKind = (zone, map) => zone.name === map.start ? "start" : zone.name === map.end ? "end" : zone.kind;
  const kindLabel = (kind) => ({start:"START",end:"END",normal:"NORMAL",priority:"PRIORITY",restricted:"RESTRICTED",blocked:"BLOCKED"}[kind] ?? kind.toUpperCase());
  const kindColor = (kind) => ({start:"#06b6d4",end:"#10b981",normal:"#3b82f6",priority:"#f59e0b",restricted:"#8b5cf6",blocked:"#64748b"}[kind] ?? "#3b82f6");
  const displayColor = (value, fallback) => value && value !== "rainbow" && window.CSS?.supports?.("color", value) ? value : fallback;
  const shortName = (name) => name.length > 14 ? `${name.slice(0, 12)}…` : name;

  function layout(zones) {
    const xs = zones.map((zone) => zone.x);
    const ys = zones.map((zone) => zone.y);
    const minX = Math.min(...xs), maxX = Math.max(...xs);
    const minY = Math.min(...ys), maxY = Math.max(...ys);
    const width = Math.max(1200, PAD_X * 2 + (maxX - minX) * X_STEP);
    const height = Math.max(760, PAD_Y * 2 + (maxY - minY) * Y_STEP);
    const points = new Map(zones.map((zone) => [zone.name, {
      x: PAD_X + (zone.x - minX) * X_STEP,
      y: PAD_Y + (maxY - zone.y) * Y_STEP,
    }]));
    return { points, width, height };
  }

  function inspect(title, rows, kind) {
    inspector.className = "inspector-popover inspector-content";
    inspector.replaceChildren();
    const card = document.createElement("div");
    card.className = "inspector-native-card";
    const marker = document.createElement("span");
    marker.className = "inspector-native-marker";
    marker.style.background = kind;
    const body = document.createElement("div");
    const heading = document.createElement("strong");
    const dl = document.createElement("dl");
    heading.textContent = title;
    rows.forEach(([label, value]) => {
      const dt = document.createElement("dt");
      const dd = document.createElement("dd");
      dt.textContent = label;
      dd.textContent = value;
      dl.append(dt, dd);
    });
    body.append(heading, dl);
    card.append(marker, body);
    inspector.append(card);
  }

  function connection(layer, item, pts, projection) {
    const a = pts.get(item.left), b = pts.get(item.right);
    const occupied = projection.links.get(edgeKey(item.left, item.right)) ?? [];
    const g = svg("g", {class:`graph-connection${occupied.length ? " is-active" : ""}`, tabindex:0, role:"button"});
    g.setAttribute("aria-label", `Connection ${item.left} to ${item.right}, capacity ${item.capacity}, ${occupied.length} drones in transit`);
    const hit = svg("line", {class:"connection-hitbox", x1:a.x, y1:a.y, x2:b.x, y2:b.y});
    const line = svg("line", {class:"connection-line", x1:a.x, y1:a.y, x2:b.x, y2:b.y});
    if (occupied.length) line.classList.add("is-active");
    g.append(hit, line);

    if (item.capacity > 1 || occupied.length) {
      const mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2;
      const badge = svg("g", {class:"connection-badge", transform:`translate(${mx} ${my})`});
      const bg = svg("rect", {x:-18,y:-10,width:36,height:20,rx:10});
      const text = svg("text", {x:0,y:4});
      text.textContent = occupied.length ? `✈${occupied.length}` : `×${item.capacity}`;
      badge.append(bg, text);
      g.append(badge);
    }

    const open = () => {
      inspect(`${item.left} ↔ ${item.right}`, [
        ["Capacity", item.capacity],
        ["In transit", occupied.length],
        ["Drones", occupied.length ? occupied.map((id) => `D${id}`).join(", ") : "none"],
      ], "#38bdf8");
      window.uiLog?.("connection:select", {connection:[item.left,item.right], occupied});
    };
    g.addEventListener("click", open);
    g.addEventListener("keydown", (event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); open(); } });
    layer.append(g);
  }

  function zone(layer, item, point, projection, map) {
    const kind = zoneKind(item, map);
    const semantic = kindColor(kind);
    const accent = displayColor(item.color, semantic);
    const occupied = projection.zones.get(item.name) ?? [];
    const g = svg("g", {class:`graph-zone graph-zone-${kind}`, transform:`translate(${point.x} ${point.y})`, tabindex:0, role:"button"});
    g.setAttribute("aria-label", `${kindLabel(kind)} zone ${item.name}, capacity ${item.capacity}, ${occupied.length} drones`);

    const shadow = svg("rect", {class:"zone-shadow", x:-NODE_W/2, y:-NODE_H/2, width:NODE_W, height:NODE_H, rx:14});
    const shape = svg("rect", {class:"zone-shape", x:-NODE_W/2, y:-NODE_H/2, width:NODE_W, height:NODE_H, rx:14, fill:accent});
    const inner = svg("rect", {class:"zone-inner", x:-NODE_W/2+4, y:-NODE_H/2+4, width:NODE_W-8, height:NODE_H-8, rx:11});
    const marker = svg("circle", {class:"zone-kind-marker", cx:-NODE_W/2+12, cy:0, r:5, fill:semantic});
    const name = svg("text", {class:"zone-name-compact", x:4, y:4});
    name.textContent = shortName(item.name);
    g.append(shadow, shape, inner, marker, name);

    if (item.capacity > 1 || occupied.length) {
      const badge = svg("g", {class:"zone-count-badge", transform:`translate(${NODE_W/2-4} ${-NODE_H/2+3})`});
      const circle = svg("circle", {r:12});
      const text = svg("text", {x:0,y:4});
      text.textContent = occupied.length ? occupied.length : item.capacity;
      badge.append(circle, text);
      g.append(badge);
    }

    const open = () => {
      inspect(`${kindLabel(kind)} · ${item.name}`, [
        ["Coordinates", `(${item.x}, ${item.y})`],
        ["Capacity", item.capacity],
        ["Color", item.color ?? "default"],
        ["Drones", occupied.length ? occupied.map((id) => `D${id}`).join(", ") : "none"],
      ], semantic);
      window.uiLog?.("zone:select", {zone:item.name, occupied});
    };
    g.addEventListener("click", open);
    g.addEventListener("keydown", (event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); open(); } });
    layer.append(g);
  }

  function dronePoint(position, pts, index, count) {
    if (position.type === "transit") {
      const a = pts.get(position.origin), b = pts.get(position.destination);
      const dx = b.x-a.x, dy = b.y-a.y, length = Math.max(1, Math.hypot(dx,dy));
      const offset = (index-(count-1)/2) * 24;
      return {x:(a.x+b.x)/2-dy/length*offset, y:(a.y+b.y)/2+dx/length*offset};
    }
    const center = pts.get(position.zone);
    const columns = Math.min(4, Math.ceil(Math.sqrt(count)));
    const row = Math.floor(index / columns), column = index % columns;
    const rowCount = Math.min(columns, count-row*columns);
    return {x:center.x+(column-(rowCount-1)/2)*28, y:center.y+34+row*28};
  }

  function droneIcon(layer, item, p, map) {
    const icon = item.position.type === "delivered" ? "happy" : item.position.type === "zone" && item.position.zone === map.start ? "sad" : "normal";
    const image = svg("image", {class:"drone-node", href:`img/${icon}.svg`, x:p.x-14, y:p.y-14, width:28, height:28});
    const label = svg("text", {class:"drone-id", x:p.x, y:p.y+19});
    label.textContent = `D${item.id}`;
    layer.append(image, label);
  }

  function droneGroup(layer, list, pts, map) {
    const p = dronePoint(list[0].position, pts, 0, 1);
    const icon = list[0].position.type === "delivered" ? "happy" : list[0].position.type === "zone" && list[0].position.zone === map.start ? "sad" : "normal";
    const image = svg("image", {class:"drone-node", href:`img/${icon}.svg`, x:p.x-17, y:p.y+23, width:34, height:34});
    const badge = svg("g", {class:"drone-count-badge", transform:`translate(${p.x+16} ${p.y+25})`});
    const circle = svg("circle", {r:11});
    const text = svg("text", {x:0,y:4});
    text.textContent = `×${list.length}`;
    badge.append(circle, text);
    layer.append(image, badge);
  }

  function drones(layer, projection, pts, map) {
    const buckets = new Map();
    projection.positions.forEach((position, id) => {
      const key = position.type === "transit" ? `t:${edgeKey(position.origin,position.destination)}` : `z:${position.zone}`;
      const list = buckets.get(key) ?? [];
      list.push({id, position});
      buckets.set(key, list);
    });
    buckets.forEach((list) => {
      if (list.length > 5) { droneGroup(layer, list, pts, map); return; }
      list.forEach((item, index) => droneIcon(layer, item, dronePoint(item.position, pts, index, list.length), map));
    });
  }

  function render(map, projection) {
    const {points, width, height} = layout(map.zones);
    canvas.setAttribute("viewBox", `0 0 ${width} ${height}`);
    canvas.replaceChildren();
    placeholder.classList.add("is-hidden");
    window.FlyInCanvas?.setBaseSize(width, height);
    const title = svg("title");
    title.textContent = "Fly-In map";
    const links = svg("g", {class:"connections-layer"});
    const zones = svg("g", {class:"zones-layer"});
    const fleet = svg("g", {class:"fleet-layer"});
    canvas.append(title, links, zones, fleet);
    map.connections.forEach((item) => connection(links, item, points, projection));
    map.zones.forEach((item) => zone(zones, item, points.get(item.name), projection, map));
    drones(fleet, projection, points, map);
    window.uiLog?.("graph:layout", {width, height, zones:map.zones.length, connections:map.connections.length, x_step:X_STEP, y_step:Y_STEP});
  }

  function resetInspector() {
    inspector.className = "inspector-popover inspector-empty";
    inspector.textContent = "Select a zone or connection to inspect it.";
  }
  window.FlyInGraph = {render, resetInspector, edgeKey};
})();
