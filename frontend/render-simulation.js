window.renderFlyInOutput = function (result) {
  const output = document.querySelector("#movement-output");
  output.replaceChildren();
  result.movement_lines.forEach((line, index) => {
    const item = document.createElement("li");
    item.dataset.turn = String(index + 1);
    const number = document.createElement("span");
    number.className = "turn-number";
    number.textContent = `T${index + 1}`;
    const text = document.createElement("span");
    text.textContent = line || "—";
    item.append(number, text);
    output.append(item);
  });
  const warnings = document.querySelector("#warning-output");
  warnings.replaceChildren();
  if (!result.warnings.length) {
    const empty = document.createElement("p");
    empty.className = "empty-copy";
    empty.textContent = "No solver warnings for this map.";
    warnings.append(empty);
  } else {
    result.warnings.forEach((warning) => {
      const item = document.createElement("article");
      item.className = "warning-item";
      const code = document.createElement("strong");
      code.textContent = warning.code;
      const text = document.createElement("span");
      text.textContent = warning.zone_name
        ? `${warning.message} · ${warning.zone_name}`
        : warning.message;
      item.append(code, text);
      warnings.append(item);
    });
  }
};

window.renderFlyInTurn = function (result, turn) {
  const projection = window.projectFlyInTurn(result, turn);
  const current = turn > 0 ? result.turns[turn - 1] : null;
  document.querySelector("#turn-badge").textContent = `Turn ${turn} / ${result.turn_count}`;
  document.querySelector("#completion-badge").textContent = `${projection.delivered} delivered`;
  document.querySelector("#current-turn-label").textContent = String(turn);
  document.querySelector("#current-turn-line").textContent = current?.line || "Initial fleet state.";
  document.querySelector("#fleet-waiting").textContent = String(projection.waiting);
  document.querySelector("#fleet-active").textContent = String(projection.active);
  document.querySelector("#fleet-delivered").textContent = String(projection.delivered);
  const output = document.querySelector("#movement-output");
  output.querySelectorAll("li").forEach((item) => {
    item.classList.toggle("is-current", Number(item.dataset.turn) === turn);
  });
  output.querySelector("li.is-current")?.scrollIntoView({ block: "nearest" });
  window.FlyInGraph.resetInspector();
  window.FlyInGraph.render(result.map, projection);
  window.uiLog?.("turn:render", {
    turn,
    waiting: projection.waiting,
    active: projection.active,
    delivered: projection.delivered,
    movements: current?.movements.length ?? 0,
  });
  return projection;
};
