window.projectFlyInTurn = function (result, turn) {
  const map = result.map;
  const positions = new Map();
  for (let id = 1; id <= map.drone_count; id += 1) {
    positions.set(id, { type: "zone", zone: map.start });
  }
  for (let index = 0; index < turn; index += 1) {
    result.turns[index].movements.forEach((move) => {
      if (move.path_cost === 2) {
        positions.set(move.drone_id, {
          type: "transit",
          origin: move.origin,
          destination: move.destination,
        });
      } else if (move.destination === map.end) {
        positions.set(move.drone_id, { type: "delivered", zone: map.end });
      } else {
        positions.set(move.drone_id, { type: "zone", zone: move.destination });
      }
    });
  }
  const zones = new Map(map.zones.map((zone) => [zone.name, []]));
  const links = new Map();
  let waiting = 0;
  let active = 0;
  let delivered = 0;
  positions.forEach((position, id) => {
    if (position.type === "transit") {
      const edge = window.FlyInGraph.edgeKey(position.origin, position.destination);
      const drones = links.get(edge) ?? [];
      drones.push(id);
      links.set(edge, drones);
      active += 1;
      return;
    }
    const drones = zones.get(position.zone) ?? [];
    drones.push(id);
    zones.set(position.zone, drones);
    if (position.type === "delivered") delivered += 1;
    else if (position.zone === map.start) waiting += 1;
    else active += 1;
  });
  return { positions, zones, links, waiting, active, delivered };
};
