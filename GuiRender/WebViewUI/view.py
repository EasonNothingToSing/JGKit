HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>JGKit</title>
  <style>
    :root {
      --bg: #101418;
      --panel: #151b21;
      --panel-2: #1b232b;
      --line: #29333d;
      --text: #dce4ec;
      --muted: #8795a1;
      --accent: #47b6a6;
      --accent-2: #8bb7ff;
      --danger: #f17272;
      --warn: #e6b45c;
      --input: #0e1318;
      --shadow: rgba(0, 0, 0, 0.28);
      color-scheme: dark;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    * { box-sizing: border-box; }
    html, body, #app { width: 100%; height: 100%; margin: 0; }
    body { background: var(--bg); color: var(--text); overflow: hidden; }
    button, input, select { font: inherit; }
    button {
      height: 30px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--panel-2);
      color: var(--text);
      padding: 0 10px;
      cursor: pointer;
    }
    button:hover:not(:disabled) { border-color: var(--accent); color: #ffffff; }
    button:disabled { opacity: 0.42; cursor: default; }
    button.primary { background: #1d6f66; border-color: #2d9286; }
    button.danger:hover:not(:disabled) { border-color: var(--danger); }
    button.icon { min-width: 28px; width: 28px; padding: 0; }
    input, select {
      height: 30px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--input);
      color: var(--text);
      padding: 0 8px;
      outline: none;
    }
    input:focus, select:focus { border-color: var(--accent); }
    .app-shell { height: 100%; display: flex; flex-direction: column; min-width: 980px; }
    .topbar {
      height: 48px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 12px;
      border-bottom: 1px solid var(--line);
      background: #121820;
      box-shadow: 0 2px 18px var(--shadow);
    }
    .brand { display: flex; align-items: center; gap: 10px; min-width: 280px; }
    .mark {
      width: 24px;
      height: 24px;
      border: 2px solid var(--accent);
      border-radius: 6px;
      position: relative;
    }
    .mark:after {
      content: "";
      position: absolute;
      left: 5px;
      right: 5px;
      top: 10px;
      border-top: 2px solid var(--accent-2);
    }
    .brand-title { font-weight: 700; letter-spacing: 0; }
    .brand-sub { color: var(--muted); font-size: 12px; }
    .toolbar { display: flex; align-items: center; gap: 6px; }
    .status { display: inline-flex; align-items: center; gap: 8px; color: var(--muted); font-size: 12px; }
    .dot { width: 8px; height: 8px; border-radius: 50%; background: var(--danger); display: inline-block; }
    .dot.on { background: var(--accent); }
    .startup {
      flex: 1;
      display: grid;
      place-items: center;
      padding: 40px;
    }
    .start-panel {
      width: min(720px, 100%);
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      box-shadow: 0 24px 80px var(--shadow);
      padding: 28px;
    }
    .start-title { font-size: 28px; font-weight: 750; margin: 0 0 6px; }
    .start-copy { margin: 0 0 24px; color: var(--muted); }
    .start-grid { display: grid; grid-template-columns: 1fr 220px; gap: 12px; margin-bottom: 18px; }
    .field label { display: block; color: var(--muted); font-size: 12px; margin-bottom: 6px; }
    .field select, .field input { width: 100%; }
    .workspace {
      flex: 1;
      min-height: 0;
      display: grid;
      grid-template-columns: 390px 1fr;
      grid-template-rows: minmax(0, 1fr) 238px;
    }
    .pane {
      min-height: 0;
      border-right: 1px solid var(--line);
      border-bottom: 1px solid var(--line);
      background: var(--panel);
      display: flex;
      flex-direction: column;
    }
    .pane.modify { border-right: 0; }
    .pane-bottom {
      min-height: 0;
      border-right: 1px solid var(--line);
      background: #11171d;
      display: flex;
      flex-direction: column;
    }
    .pane-bottom.memory { grid-column: span 1; border-right: 0; }
    .pane-head {
      height: 38px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 10px;
      border-bottom: 1px solid var(--line);
      background: var(--panel-2);
    }
    .pane-title { font-weight: 700; font-size: 13px; }
    .pane-meta { color: var(--muted); font-size: 12px; }
    .scroll { overflow: auto; min-height: 0; flex: 1; }
    .tree { padding: 6px; }
    details { border-bottom: 1px solid rgba(41, 51, 61, 0.55); }
    summary {
      list-style: none;
      cursor: pointer;
      min-height: 30px;
      display: grid;
      grid-template-columns: 1fr auto auto;
      gap: 8px;
      align-items: center;
      padding: 3px 4px;
    }
    summary::-webkit-details-marker { display: none; }
    .row {
      min-height: 30px;
      display: grid;
      grid-template-columns: 1fr auto auto;
      gap: 8px;
      align-items: center;
      padding: 3px 4px;
      border-bottom: 1px solid rgba(41, 51, 61, 0.35);
    }
    .row:hover, summary:hover { background: rgba(71, 182, 166, 0.08); }
    .name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .node-label { display: flex; align-items: center; gap: 7px; min-width: 0; }
    .node-icon {
      position: relative;
      display: inline-block;
      width: 15px;
      height: 15px;
      flex: 0 0 15px;
    }
    .node-icon.device {
      border: 1px solid #55c8b8;
      border-radius: 3px;
      background: rgba(71, 182, 166, 0.18);
    }
    .node-icon.device:before,
    .node-icon.device:after {
      content: "";
      position: absolute;
      left: -3px;
      right: -3px;
      height: 1px;
      background: #55c8b8;
    }
    .node-icon.device:before { top: 4px; }
    .node-icon.device:after { bottom: 4px; }
    .node-icon.register {
      border: 1px solid #8bb7ff;
      border-radius: 2px;
      background: rgba(139, 183, 255, 0.16);
    }
    .node-icon.register:before,
    .node-icon.register:after {
      content: "";
      position: absolute;
      left: 3px;
      right: 3px;
      height: 1px;
      background: #8bb7ff;
    }
    .node-icon.register:before { top: 4px; }
    .node-icon.register:after { top: 8px; }
    .node-icon.field {
      border: 1px solid #e6b45c;
      border-radius: 50%;
      background: rgba(230, 180, 92, 0.13);
    }
    .node-icon.field:after {
      content: "";
      position: absolute;
      left: 4px;
      top: 4px;
      width: 5px;
      height: 5px;
      border-radius: 50%;
      background: #e6b45c;
    }
    .addr { color: var(--accent-2); font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 11px; }
    .prop { color: var(--muted); font-size: 11px; min-width: 38px; text-align: right; }
    table { width: 100%; border-collapse: collapse; font-size: 12px; }
    th {
      position: sticky;
      top: 0;
      background: var(--panel-2);
      color: var(--muted);
      text-align: left;
      z-index: 1;
      border-bottom: 1px solid var(--line);
      height: 30px;
      padding: 0 8px;
    }
    td { border-bottom: 1px solid rgba(41, 51, 61, 0.55); padding: 4px 8px; vertical-align: middle; }
    td input { width: 104px; height: 28px; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
    .indent { display: inline-block; width: calc(var(--depth) * 16px); }
    .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
    .bottom-grid { grid-column: 1 / span 2; display: grid; grid-template-columns: 390px 300px 1fr; min-height: 0; }
    .log-lines { padding: 8px; font-size: 11px; color: #b8c3cc; }
    .log-line { margin-bottom: 4px; white-space: pre-wrap; }
    .commander { display: flex; gap: 6px; padding: 8px; border-top: 1px solid var(--line); }
    .commander input { flex: 1; }
    .description { padding: 10px; color: #c7d0d8; font-size: 12px; line-height: 1.45; white-space: pre-wrap; }
    .memory-tabs { display: flex; gap: 4px; overflow-x: auto; max-width: 330px; }
    .memory-tabs button.active { border-color: var(--accent); color: #ffffff; }
    .memory-grid { padding: 6px; }
    .mem-row { display: grid; grid-template-columns: 92px repeat(4, 94px); gap: 4px; align-items: center; margin-bottom: 4px; }
    .mem-row input { width: 94px; height: 28px; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
    .empty { color: var(--muted); display: grid; place-items: center; height: 100%; }
    .toast {
      position: fixed;
      right: 14px;
      bottom: 14px;
      max-width: 520px;
      background: #241819;
      border: 1px solid #6b3030;
      color: #ffdada;
      border-radius: 8px;
      padding: 10px 12px;
      box-shadow: 0 12px 40px var(--shadow);
      display: none;
      z-index: 10;
    }
    .busy {
      position: fixed;
      left: 50%;
      top: 10px;
      transform: translateX(-50%);
      color: var(--muted);
      background: rgba(16, 20, 24, 0.92);
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 5px 12px;
      display: none;
      z-index: 11;
      font-size: 12px;
    }
  </style>
</head>
<body>
  <div id="app" class="app-shell"></div>
  <div id="busy" class="busy">Working</div>
  <div id="toast" class="toast"></div>
  <script>
    let state = null;
    let description = "";
    let autoTimer = null;

    const $ = (id) => document.getElementById(id);
    const esc = (value) => String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
    const toHex = (value) => {
      const number = Number(value);
      return "0x" + (Number.isFinite(number) ? Math.trunc(number).toString(16) : "0");
    };
    const pathArg = (path) => JSON.stringify(path);

    function setBusy(on) {
      $("busy").style.display = on ? "block" : "none";
    }

    function showError(message) {
      const toast = $("toast");
      toast.textContent = message;
      toast.style.display = "block";
      setTimeout(() => { toast.style.display = "none"; }, 5200);
    }

    async function callApi(name, ...args) {
      if (!window.pywebview || !window.pywebview.api) {
        showError("PyWebView bridge is not ready");
        return null;
      }
      setBusy(true);
      try {
        const result = await window.pywebview.api[name](...args);
        if (!result.ok) {
          if (result.data) render(result.data);
          showError(result.error || "Command failed");
          return null;
        }
        if (result.data && Object.prototype.hasOwnProperty.call(result.data, "configs")) {
          render(result.data);
        }
        return result.data;
      } catch (error) {
        showError(String(error));
        return null;
      } finally {
        setBusy(false);
      }
    }

    function render(nextState) {
      state = nextState;
      if (!state.launched) {
        renderStartup();
      } else {
        renderWorkspace();
      }
    }

    function renderStartup() {
      const current = state.currentConfig || state.configs[0] || null;
      const chipOptions = state.configs.map((item) =>
        `<option value="${esc(item.name)}" ${current && current.name === item.name ? "selected" : ""}>${esc(item.name)}</option>`
      ).join("");
      const tifOptions = current ? current.tifOptions.map((item) =>
        `<option value="${esc(item)}" ${current.selectedTif === item ? "selected" : ""}>${esc(item)}</option>`
      ).join("") : "";

      $("app").innerHTML = `
        <div class="topbar">
          <div class="brand">
            <div class="mark"></div>
            <div>
              <div class="brand-title">JGKit</div>
              <div class="brand-sub">Register and memory console</div>
            </div>
          </div>
          <div class="status"><span class="dot"></span> Disconnected</div>
        </div>
        <main class="startup">
          <section class="start-panel">
            <h1 class="start-title">JGKit</h1>
            <p class="start-copy">Chip register and memory workspace</p>
            <div class="start-grid">
              <div class="field">
                <label>Chip</label>
                <select id="chipSelect" onchange="syncStartupTif()">${chipOptions}</select>
              </div>
              <div class="field">
                <label>TIF</label>
                <select id="tifSelect">${tifOptions}</select>
              </div>
            </div>
            <button class="primary" onclick="launchWorkspace()">Launch</button>
          </section>
        </main>`;
    }

    function syncStartupTif() {
      const chip = $("chipSelect").value;
      const config = state.configs.find((item) => item.name === chip);
      $("tifSelect").innerHTML = (config ? config.tifOptions : []).map((item) => `<option value="${esc(item)}">${esc(item)}</option>`).join("");
    }

    function launchWorkspace() {
      callApi("launch", $("chipSelect").value, $("tifSelect").value);
    }

    function renderWorkspace() {
      const cfg = state.currentConfig || {};
      $("app").innerHTML = `
        <div class="topbar">
          <div class="brand">
            <div class="mark"></div>
            <div>
              <div class="brand-title">JGKit</div>
              <div class="brand-sub">${esc(cfg.name || "")} / ${esc(cfg.selectedTif || "")}</div>
            </div>
          </div>
          <div class="toolbar">
            <span class="status"><span class="dot ${state.connected ? "on" : ""}"></span>${state.connected ? "Connected" : "Disconnected"}</span>
            ${renderCoreSelect()}
            <label class="status"><input id="debugMode" type="checkbox" ${state.debugMode ? "checked" : ""} onchange="callApi('set_debug_mode', this.checked)"> Debug</label>
            <button onclick="connectTarget()" ${state.connected ? "disabled" : ""}>Connect</button>
            <button onclick="callApi('disconnect')" ${state.connected ? "" : "disabled"}>Stop</button>
            <button onclick="callApi('refresh_modify')" ${state.connected ? "" : "disabled"}>Refresh</button>
            <button onclick="callApi('upload_modify')" ${state.connected ? "" : "disabled"}>Upload</button>
            <button onclick="callApi('open_regcfg')" ${state.connected ? "" : "disabled"}>Open</button>
            <button onclick="callApi('save_regcfg')" ${state.connected ? "" : "disabled"}>Save</button>
            <button onclick="callApi('save_glicfg')" ${state.connected ? "" : "disabled"}>Glimpse</button>
            <label class="status"><input id="autoRefresh" type="checkbox" onchange="toggleAutoRefresh(this.checked)"> Auto</label>
            <button onclick="callApi('back_to_startup')">Chip</button>
          </div>
        </div>
        <main class="workspace">
          <section class="pane">
            <div class="pane-head"><span class="pane-title">Device Tree</span><span class="pane-meta">${state.deviceNodes.length} devices</span></div>
            <div class="scroll tree">${renderDeviceTree()}</div>
          </section>
          <section class="pane modify">
            <div class="pane-head"><span class="pane-title">Modify Tree</span><span class="pane-meta">${state.modifyItems.length} tracked</span></div>
            <div class="scroll">${renderModifyTable()}</div>
          </section>
          <section class="bottom-grid">
            <section class="pane-bottom">
              <div class="pane-head"><span class="pane-title">Commander</span></div>
              <div class="scroll log-lines">${renderLogs()}</div>
              <div class="commander">
                <input id="commandInput" placeholder="JGKit:" onkeydown="if(event.key==='Enter') submitCommand()">
                <button onclick="submitCommand()">Run</button>
              </div>
            </section>
            <section class="pane-bottom">
              <div class="pane-head"><span class="pane-title">Description</span></div>
              <div id="descriptionPanel" class="description">${esc(description)}</div>
            </section>
            <section class="pane-bottom memory">
              <div class="pane-head">
                <span class="pane-title">Memory</span>
                <span class="toolbar">
                  <button class="icon" onclick="addMemory()" ${state.connected ? "" : "disabled"}>+</button>
                  <button class="icon danger" onclick="removeMemory()" ${state.memoryTabs.length ? "" : "disabled"}>-</button>
                  <button class="icon" onclick="renameMemory()" ${state.memoryTabs.length ? "" : "disabled"}>N</button>
                  <button class="icon" onclick="callApi('shift_memory', state.memoryIndex, -1)" ${memoryEnabled()}>^</button>
                  <button class="icon" onclick="callApi('shift_memory', state.memoryIndex, 1)" ${memoryEnabled()}>v</button>
                  <button class="icon" onclick="callApi('refresh_memory', state.memoryIndex)" ${memoryEnabled()}>R</button>
                  <button class="icon" onclick="importMemory()" ${memoryEnabled()}>I</button>
                  <button class="icon" onclick="exportMemory()" ${memoryEnabled()}>E</button>
                </span>
              </div>
              <div class="pane-head"><div class="memory-tabs">${renderMemoryTabs()}</div></div>
              <div class="scroll memory-grid">${renderMemoryGrid()}</div>
            </section>
          </section>
        </main>`;
      const auto = $("autoRefresh");
      if (auto) auto.checked = !!autoTimer;
    }

    function renderCoreSelect() {
      if (!state.coreOptions.length) return "";
      const options = state.coreOptions.map((core) => `<option value="${esc(core)}" ${state.coreValue === core ? "selected" : ""}>${esc(core)}</option>`).join("");
      return `<select id="coreSelect" ${state.connected ? "disabled" : ""} onchange="callApi('set_core', this.value)">${options}</select>`;
    }

    function renderDeviceTree() {
      if (!state.deviceNodes.length) return `<div class="empty">No devices</div>`;
      return state.deviceNodes.map((device, i) => `
        <details>
          <summary onclick="setDescriptionFromSource(${pathArg([i])})">
            <span class="node-label"><span class="node-icon device"></span><span class="name">${esc(device.name)}</span></span>
            <span class="addr">${esc(device.address)}</span>
            <button class="icon" ${addEnabled()} onclick="event.stopPropagation(); callApi('add_modify_item', [${i}])">+</button>
          </summary>
          ${device.children.map((reg, j) => renderRegisterTree(reg, [i, j])).join("")}
        </details>`).join("");
    }

    function renderRegisterTree(item, path) {
      if (!item.children.length) return renderFieldRow(item, path);
      return `<details>
        <summary onclick="setDescriptionFromSource(${pathArg(path)})">
          <span class="node-label"><span class="node-icon register"></span><span class="name">${esc(item.name)}</span></span>
          <span class="addr">${esc(item.addressExpr)}</span>
          <button class="icon" ${addEnabled()} onclick="event.stopPropagation(); callApi('add_modify_item', ${pathArg(path)})">+</button>
        </summary>
        ${item.children.map((child, index) => renderFieldRow(child, [...path, index])).join("")}
      </details>`;
    }

    function renderFieldRow(item, path) {
      return `<div class="row" onclick="setDescriptionFromSource(${pathArg(path)})">
        <span class="node-label"><span class="node-icon field"></span><span class="name">${esc(item.name)}</span></span>
        <span><span class="addr">${esc(item.addressExpr)}</span> <span class="prop">${esc(item.property)}</span></span>
        <button class="icon" ${addEnabled()} onclick="event.stopPropagation(); callApi('add_modify_item', ${pathArg(path)})">+</button>
      </div>`;
    }

    function renderModifyTable() {
      if (!state.modifyItems.length) return `<div class="empty">No tracked registers</div>`;
      const rows = [];
      state.modifyItems.forEach((item, index) => pushModifyRows(rows, item, [index], 0));
      return `<table>
        <thead><tr><th>Name</th><th>Address | Field</th><th>Property</th><th>Write</th><th>Read</th><th>Actions</th></tr></thead>
        <tbody>${rows.join("")}</tbody>
      </table>`;
    }

    function pushModifyRows(rows, item, path, depth) {
      const pathText = pathArg(path);
      const write = item.writeValue === "NA" ? "" : item.writeValue;
      const writable = state.connected && item.level !== 0;
      const iconClass = item.level === 0 ? "device" : (item.children.length ? "register" : "field");
      rows.push(`<tr onclick="setDescriptionFromModify(${pathText})">
        <td><span class="indent" style="--depth:${depth}"></span><span class="node-label"><span class="node-icon ${iconClass}"></span><span class="name">${esc(item.name)}</span></span></td>
        <td class="addr">${esc(item.addressExpr)}</td>
        <td>${esc(item.property)}</td>
        <td><input value="${esc(write)}" ${writable ? "" : "disabled"} onblur="callApi('set_write_value', ${pathText}, this.value)" onkeydown="if(event.key==='Enter') writeModify(${pathText}, this.value)"></td>
        <td class="mono">${esc(item.readValue)}</td>
        <td>
          <button class="icon" onclick="event.stopPropagation(); callApi('read_item', ${pathText})" ${writable ? "" : "disabled"}>R</button>
          <button class="icon" onclick="event.stopPropagation(); writeModify(${pathText}, this.closest('tr').querySelector('input').value)" ${writable ? "" : "disabled"}>W</button>
          <button class="icon danger" onclick="event.stopPropagation(); callApi('remove_modify_item', ${pathText})">-</button>
        </td>
      </tr>`);
      item.children.forEach((child, index) => pushModifyRows(rows, child, [...path, index], depth + 1));
    }

    function renderLogs() {
      if (!state.logs.length) return `<div class="empty">No log entries</div>`;
      return state.logs.slice(-80).map((line) => `<div class="log-line">${esc(line)}</div>`).join("");
    }

    function renderMemoryTabs() {
      if (!state.memoryTabs.length) return `<span class="pane-meta">No memory views</span>`;
      return state.memoryTabs.map((tab, index) => `<button class="${index === state.memoryIndex ? "active" : ""}" onclick="callApi('select_memory', ${index})">${esc(tab.name)}</button>`).join("");
    }

    function renderMemoryGrid() {
      const tab = state.memoryTabs[state.memoryIndex];
      if (!tab) return `<div class="empty">No memory views</div>`;
      const rows = [];
      for (let i = 0; i < tab.values.length; i += 4) {
        const cells = [];
        for (let j = 0; j < 4 && i + j < tab.values.length; j += 1) {
          const idx = i + j;
          cells.push(`<input value="${esc(toHex(tab.values[idx]))}" ${state.connected ? "" : "disabled"} onkeydown="if(event.key==='Enter') callApi('write_memory_word', ${state.memoryIndex}, ${idx}, this.value)">`);
        }
        rows.push(`<div class="mem-row"><span class="addr">${esc(toHex(tab.headAddress + i * 4))}</span>${cells.join("")}</div>`);
      }
      return rows.join("");
    }

    function memoryEnabled() {
      return state.connected && state.memoryTabs.length ? "" : "disabled";
    }

    function addEnabled() {
      return state.connected ? "" : "disabled";
    }

    function getSource(path) {
      let item = state.deviceNodes[path[0]];
      if (path.length > 1) item = item.children[path[1]];
      if (path.length > 2) item = item.children[path[2]];
      return item;
    }

    function getModify(path) {
      let item = state.modifyItems[path[0]];
      for (let i = 1; i < path.length; i += 1) item = item.children[path[i]];
      return item;
    }

    function setDescriptionFromSource(path) {
      const item = getSource(path);
      description = item.description || "";
      updateDescriptionPanel();
    }

    function setDescriptionFromModify(path) {
      const item = getModify(path);
      description = item.description || "";
      updateDescriptionPanel();
    }

    function updateDescriptionPanel() {
      const panel = $("descriptionPanel");
      if (panel) panel.textContent = description;
    }

    function connectTarget() {
      const core = $("coreSelect") ? $("coreSelect").value : null;
      callApi("connect", core);
    }

    function writeModify(path, value) {
      callApi("write_item", path, value);
    }

    function addMemory() {
      const address = prompt("Address", "0x0");
      if (address) callApi("add_memory", address);
    }

    function removeMemory() {
      if (state.memoryTabs.length) callApi("remove_memory", state.memoryIndex);
    }

    function renameMemory() {
      const tab = state.memoryTabs[state.memoryIndex];
      if (!tab) return;
      const name = prompt("Name", tab.name);
      if (name) callApi("rename_memory", state.memoryIndex, name);
    }

    function importMemory() {
      const tab = state.memoryTabs[state.memoryIndex];
      if (!tab) return;
      const address = prompt("Address", toHex(tab.headAddress));
      if (address) callApi("import_memory", state.memoryIndex, address);
    }

    function exportMemory() {
      const tab = state.memoryTabs[state.memoryIndex];
      if (!tab) return;
      const start = prompt("Start address", toHex(tab.headAddress));
      if (!start) return;
      const length = prompt("Length", String(tab.tailAddress - tab.headAddress));
      if (!length) return;
      callApi("export_memory", state.memoryIndex, start, length);
    }

    function submitCommand() {
      const input = $("commandInput");
      const value = input.value;
      input.value = "";
      callApi("commander", value);
    }

    function toggleAutoRefresh(enabled) {
      if (autoTimer) {
        clearInterval(autoTimer);
        autoTimer = null;
      }
      if (enabled) {
        autoTimer = setInterval(() => callApi("refresh_all"), 600);
      }
    }

    function boot() {
      callApi("bootstrap");
    }

    window.addEventListener("pywebviewready", boot);
    document.addEventListener("DOMContentLoaded", () => {
      setTimeout(() => {
        if (!state && window.pywebview && window.pywebview.api) boot();
      }, 100);
    });
  </script>
</body>
</html>"""
