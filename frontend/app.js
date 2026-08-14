const UI_PREFIX = "[Fly-In UI]";
const API_BASE_URL = "http://127.0.0.1:8000";
const mapSelect = document.querySelector("#map-select");
const simulateButton = document.querySelector("#simulate-button");
const simulateLabel = document.querySelector("#simulate-label");
const apiStatus = document.querySelector("#api-status");
const uiMessage = document.querySelector("#ui-message");
const selectedMapName = document.querySelector("#selected-map-name");
let maps = [];

function uiLog(action, details = {}) {
  console.log(`${UI_PREFIX} ${action}`, details);
}
function uiError(action, error, details = {}) {
  console.error(`${UI_PREFIX} ${action}`, { ...details, error });
}
function setStatus(state, label) {
  apiStatus.dataset.state = state;
  apiStatus.textContent = label;
}
function setMessage(text) { uiMessage.textContent = text; }
function selectedMap() {
  return maps.find((map) => map.index === Number(mapSelect.value)) ?? null;
}
function setBusy(busy) {
  mapSelect.disabled = busy || maps.length === 0;
  simulateButton.disabled = busy || !selectedMap();
  simulateLabel.textContent = busy ? "Simulating…" : "Simulate";
}
function renderSelection() {
  const map = selectedMap();
  selectedMapName.textContent = map ? `#${map.index} · ${map.display_path}` : "No map selected";
  simulateButton.disabled = !map;
}
function renderCatalog(catalog) {
  maps = catalog;
  mapSelect.replaceChildren();
  if (!maps.length) {
    mapSelect.innerHTML = "<option>No official maps available</option>";
    setBusy(true);
    setStatus("error", "No maps");
    setMessage("The API returned an empty catalog.");
    return;
  }
  maps.forEach((map) => {
    const option = document.createElement("option");
    option.value = String(map.index);
    option.textContent = `${map.index}. ${map.display_path}`;
    mapSelect.append(option);
  });
  setBusy(false);
  setStatus("ready", `${maps.length} maps ready`);
  setMessage("Catalog loaded. Choose a map and press Simulate.");
  renderSelection();
}
async function loadCatalog() {
  const endpoint = `${API_BASE_URL}/api/v1/maps`;
  uiLog("catalog:request", { method: "GET", endpoint });
  try {
    const response = await fetch(endpoint, { headers: { Accept: "application/json" } });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const payload = await response.json();
    if (!Array.isArray(payload.maps)) throw new Error("Invalid catalog response");
    uiLog("catalog:success", { count: payload.maps.length });
    renderCatalog(payload.maps);
  } catch (error) {
    uiError("catalog:failure", error, { endpoint });
    mapSelect.innerHTML = "<option>Unable to load maps</option>";
    setBusy(true);
    setStatus("error", "API unavailable");
    setMessage("Could not load maps. Check that the API is running on port 8000.");
  }
}
async function runSimulation() {
  const map = selectedMap();
  if (!map) return;
  const endpoint = `${API_BASE_URL}/api/v1/maps/${map.index}/simulate`;
  setBusy(true);
  setStatus("loading", "Solving…");
  setMessage(`Requesting ${map.display_path}.`);
  uiLog("simulate:request", { method: "POST", endpoint, map });
  try {
    const response = await fetch(endpoint, { method: "POST", headers: { Accept: "application/json" } });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload?.error?.message ?? `HTTP ${response.status}`);
    window.FlyInSimulation.load(payload, map);
    setStatus("ready", "Simulation ready");
    setMessage(`Solved ${map.display_path} in ${payload.turn_count} turns.`);
    uiLog("simulate:success", { turns: payload.turn_count, drones: payload.map.drone_count });
  } catch (error) {
    uiError("simulate:failure", error, { endpoint, map });
    setStatus("error", "Simulation failed");
    setMessage(`Simulation failed: ${error.message}`);
  } finally { setBusy(false); }
}
mapSelect.addEventListener("change", () => {
  window.FlyInSimulation.clear();
  renderSelection();
  uiLog("selection:change", selectedMap() ?? {});
});
simulateButton.addEventListener("click", runSimulation);
window.uiLog = uiLog;
uiLog("bootstrap", { frontend: location.origin, api: API_BASE_URL, renderer: "native-compact-svg" });
loadCatalog();
