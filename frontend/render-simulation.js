window.renderFlyInOutput = function (result) {
  const panel = document.querySelector("#warning-panel");
  const warnings = document.querySelector("#warning-output");
  warnings.replaceChildren();
  panel.classList.toggle("is-hidden", result.warnings.length === 0);
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
};

window.renderFlyInTurn = function (result, turn) {
  const projection = window.projectFlyInTurn(result, turn);
  const current = turn > 0 ? result.turns[turn - 1] : null;
  document.querySelector("#turn-badge").textContent = `Turn ${turn} / ${result.turn_count}`;
  document.querySelector("#completion-badge").textContent = `${projection.delivered} delivered`;
  document.querySelector("#current-turn-label").textContent = String(turn);
  document.querySelector("#current-turn-line").hidden = true;
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
