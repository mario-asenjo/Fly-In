const UI_PREFIX = "[Fly-In UI]";

const mapSelect = document.querySelector("#map-select");
const simulateButton = document.querySelector("#simulate-button");
const apiStatus = document.querySelector("#api-status");
const uiMessage = document.querySelector("#ui-message");
const selectedMapName = document.querySelector("#selected-map-name");

let maps = [];

function logAction(action, details = {}) {
  console.log(`${UI_PREFIX} ${action}`, details);
}

function setStatus(state, label) {
  apiStatus.dataset.state = state;
  apiStatus.textContent = label;
}

function setMessage(message) {
  uiMessage.textContent = message;
}

function selectedMap() {
  const index = Number(mapSelect.value);
  return maps.find((map) => map.index === index) ?? null;
}

function renderSelection() {
  const map = selectedMap();

  if (!map) {
    selectedMapName.textContent = "No map selected";
    simulateButton.disabled = true;
    return;
  }

  selectedMapName.textContent = `#${map.index} · ${map.display_path}`;
  simulateButton.disabled = false;
}

function renderCatalog(catalog) {
  maps = catalog;
  mapSelect.replaceChildren();

  if (maps.length === 0) {
    const option = document.createElement("option");
    option.textContent = "No official maps available";
    option.value = "";
    mapSelect.append(option);
    mapSelect.disabled = true;
    simulateButton.disabled = true;
    selectedMapName.textContent = "The catalog is empty";
    setStatus("error", "No maps");
    setMessage("The API responded correctly, but no selectable maps were returned.");
    logAction("catalog:empty");
    return;
  }

  maps.forEach((map) => {
    const option = document.createElement("option");
    option.value = String(map.index);
    option.textContent = `${map.index}. ${map.display_path}`;
    mapSelect.append(option);
  });

  mapSelect.disabled = false;
  setStatus("ready", `${maps.length} maps ready`);
  setMessage("Catalog loaded. Choose a map and press Simulate.");
  renderSelection();
}

async function loadCatalog() {
  const endpoint = "/api/v1/maps";
  logAction("catalog:request", { method: "GET", endpoint });

  try {
    const response = await fetch(endpoint, {
      headers: { Accept: "application/json" },
    });

    if (!response.ok) {
      throw new Error(`Catalog request failed with HTTP ${response.status}`);
    }

    const payload = await response.json();
    if (!Array.isArray(payload.maps)) {
      throw new Error("Catalog response does not contain a maps array");
    }

    logAction("catalog:success", { count: payload.maps.length, maps: payload.maps });
    renderCatalog(payload.maps);
  } catch (error) {
    console.error(`${UI_PREFIX} catalog:failure`, error);
    mapSelect.replaceChildren();
    const option = document.createElement("option");
    option.textContent = "Unable to load maps";
    mapSelect.append(option);
    mapSelect.disabled = true;
    simulateButton.disabled = true;
    selectedMapName.textContent = "Catalog unavailable";
    setStatus("error", "API unavailable");
    setMessage("Could not load the official catalog. Check the browser console for details.");
  }
}

mapSelect.addEventListener("change", () => {
  renderSelection();
  const map = selectedMap();
  logAction("selection:change", map ?? { index: null });
});

simulateButton.addEventListener("click", () => {
  const map = selectedMap();

  if (!map) {
    logAction("simulate:ignored", { reason: "no-map-selected" });
    return;
  }

  logAction("simulate:intent", {
    map_index: map.index,
    display_path: map.display_path,
    note: "M8.1 intentionally does not call POST /simulate yet.",
  });
  setMessage(`Simulation intent registered for ${map.display_path}. See the browser console.`);
});

logAction("bootstrap", {
  architecture: "native-html-css-js",
  catalog_endpoint: "/api/v1/maps",
});
loadCatalog();
