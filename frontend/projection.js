(() => {
  const state = { result: null, mapOption: null, turn: 0 };
  function clear() {
    state.result = null;
    state.mapOption = null;
    state.turn = 0;
    document.querySelector("#simulation-workspace").classList.add("is-hidden");
    window.FlyInGraph.resetInspector();
  }
  window.FlyInProjection = { state, clear };
})();
