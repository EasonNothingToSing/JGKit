HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>JGKit</title>
  <style>
    :root {
      --canvas: #0e1116;
      --surface: #151a21;
      --surface-raised: #1b222b;
      --surface-hover: #202a34;
      --line: #2a333e;
      --line-strong: #3a4653;
      --text: #e6edf3;
      --text-soft: #b7c0ca;
      --muted: #84909c;
      --connected: #22c7a9;
      --selected: #66a6ff;
      --pending: #f2b84b;
      --danger: #f06161;
      --input: #0b0f14;
      --explorer-width: 310px;
      --inspector-width: 292px;
      --console-height: 176px;
      color-scheme: dark;
      font-family: "IBM Plex Sans", "Segoe UI", system-ui, sans-serif;
    }

    * { box-sizing: border-box; }
    html, body, #app { width: 100%; height: 100%; margin: 0; }
    body { background: var(--canvas); color: var(--text); overflow: hidden; }
    button, input, select { font: inherit; }
    button { letter-spacing: 0; }
    button, summary, input, select { outline: none; }
    button:focus-visible, summary:focus-visible, input:focus-visible, select:focus-visible {
      box-shadow: 0 0 0 2px var(--canvas), 0 0 0 4px var(--selected);
    }

    .mono, .address, .value-input, .memory-input, .bit-cell, .console-lines {
      font-family: "JetBrains Mono", "Cascadia Code", SFMono-Regular, Consolas, monospace;
      font-variant-numeric: tabular-nums;
    }

    .app-shell { height: 100%; min-width: 980px; display: flex; flex-direction: column; }
    .icon { width: 16px; height: 16px; flex: 0 0 16px; stroke-width: 1.8; }
    .icon.small { width: 14px; height: 14px; flex-basis: 14px; }

    .button {
      height: 32px;
      border: 1px solid var(--line);
      border-radius: 5px;
      background: var(--surface-raised);
      color: var(--text-soft);
      padding: 0 11px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 7px;
      cursor: pointer;
      white-space: nowrap;
    }
    .button:hover:not(:disabled) { border-color: var(--line-strong); background: var(--surface-hover); color: var(--text); }
    .button:disabled { opacity: 0.38; cursor: default; }
    .button.primary { background: #116354; border-color: #1d8d79; color: #f2fffc; }
    .button.primary:hover:not(:disabled) { background: #167765; border-color: var(--connected); }
    .button.apply { background: #5b4315; border-color: #8c6924; color: #ffe4a8; }
    .button.apply:hover:not(:disabled) { background: #6b501b; border-color: var(--pending); }
    .button.danger { color: #ffb8b8; }
    .button.danger:hover:not(:disabled) { border-color: var(--danger); background: #361c21; }
    .button.ghost { border-color: transparent; background: transparent; }
    .icon-button { width: 30px; min-width: 30px; height: 30px; padding: 0; }
    .icon-button.tiny { width: 26px; min-width: 26px; height: 26px; }

    input, select {
      height: 32px;
      border: 1px solid var(--line);
      border-radius: 5px;
      background: var(--input);
      color: var(--text);
      padding: 0 9px;
    }
    input:hover, select:hover { border-color: var(--line-strong); }
    input:focus, select:focus { border-color: var(--selected); }
    input::placeholder { color: #65717d; }
    input:disabled, select:disabled { opacity: 0.48; }

    .targetbar {
      height: 56px;
      flex: 0 0 56px;
      display: grid;
      grid-template-columns: minmax(180px, 0.8fr) minmax(300px, 1.4fr) auto;
      align-items: center;
      gap: 14px;
      padding: 0 12px;
      border-bottom: 1px solid var(--line);
      background: #11161c;
    }
    .brand { display: flex; align-items: center; gap: 10px; min-width: 0; }
    .brand-mark {
      width: 30px;
      height: 30px;
      border: 1px solid #2b8d7b;
      border-radius: 5px;
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 2px;
      padding: 5px;
      background: #10231f;
    }
    .brand-mark i { display: block; background: #2f766a; border-radius: 1px; }
    .brand-mark i:nth-child(2), .brand-mark i:nth-child(7) { background: var(--connected); }
    .brand-copy { min-width: 0; }
    .brand-title { font-weight: 700; font-size: 14px; }
    .brand-sub { color: var(--muted); font-size: 11px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .target-context { display: flex; align-items: center; gap: 7px; min-width: 0; }
    .target-chip {
      min-width: 0;
      height: 32px;
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 0 10px;
      border: 1px solid var(--line);
      border-radius: 5px;
      background: var(--surface);
    }
    .target-chip strong { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 13px; }
    .target-chip span { color: var(--muted); font-size: 11px; }
    .connection-cluster { display: flex; align-items: center; gap: 7px; justify-content: flex-end; }
    .connection-state { display: inline-flex; align-items: center; gap: 7px; color: var(--muted); font-size: 12px; }
    .state-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--danger); }
    .state-dot.on { background: var(--connected); box-shadow: 0 0 0 3px rgba(34, 199, 169, 0.11); }

    .simulation-banner {
      height: 27px;
      flex: 0 0 27px;
      border-bottom: 1px solid #63501f;
      background: #2b2413;
      color: #f6d88e;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      font-size: 11px;
      font-weight: 700;
    }

    .workbench {
      flex: 1;
      min-height: 0;
      display: grid;
      grid-template-columns: var(--explorer-width) 4px minmax(360px, 1fr) 4px var(--inspector-width);
      background: var(--canvas);
    }
    .panel { min-width: 0; min-height: 0; background: var(--surface); display: flex; flex-direction: column; }
    .explorer { border-right: 1px solid var(--line); }
    .inspector { border-left: 1px solid var(--line); }
    .panel-head {
      height: 40px;
      flex: 0 0 40px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      padding: 0 10px;
      border-bottom: 1px solid var(--line);
      background: var(--surface-raised);
    }
    .panel-title { font-size: 12px; font-weight: 700; color: var(--text-soft); }
    .panel-meta { font-size: 11px; color: var(--muted); }
    .panel-tools { display: flex; align-items: center; gap: 4px; }
    .scroll { overflow: auto; min-height: 0; flex: 1; scrollbar-color: #39434e transparent; scrollbar-width: thin; }
    .resizer { background: #0b0f14; position: relative; z-index: 2; }
    .resizer.vertical { cursor: col-resize; }
    .resizer.horizontal { height: 4px; cursor: row-resize; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }
    .resizer:hover, .resizer.active { background: var(--selected); }

    .search-wrap { position: relative; padding: 8px; border-bottom: 1px solid var(--line); }
    .search-wrap .icon { position: absolute; left: 17px; top: 17px; color: var(--muted); pointer-events: none; }
    .search-wrap input { width: 100%; padding-left: 31px; }
    .tree { padding: 5px 7px 12px; }
    details.tree-node { border-bottom: 1px solid rgba(42, 51, 62, 0.6); }
    summary.tree-row, .tree-row.leaf {
      min-height: 31px;
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto 28px;
      gap: 7px;
      align-items: center;
      padding: 2px 1px 2px 5px;
      cursor: pointer;
      list-style: none;
    }
    summary.tree-row::-webkit-details-marker { display: none; }
    summary.tree-row:hover, .tree-row.leaf:hover { background: rgba(102, 166, 255, 0.07); }
    .node-name { min-width: 0; display: flex; align-items: center; gap: 7px; }
    .node-name span:last-child { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 12px; }
    .node-glyph { width: 14px; height: 14px; flex: 0 0 14px; border: 1px solid var(--line-strong); border-radius: 2px; position: relative; }
    .node-glyph.device { border-color: #2f9e8b; background: rgba(34, 199, 169, 0.11); }
    .node-glyph.register { border-color: #568acb; background: rgba(102, 166, 255, 0.1); }
    .node-glyph.field { border-radius: 50%; border-color: #9b7831; background: rgba(242, 184, 75, 0.1); }
    .node-glyph:after { content: ""; position: absolute; left: 3px; right: 3px; top: 6px; border-top: 1px solid currentColor; }
    .address { color: #82b3f3; font-size: 10px; white-space: nowrap; }
    .access { color: var(--muted); font-size: 10px; min-width: 28px; text-align: center; }
    .tracked { color: var(--connected); }

    .center-panel { min-width: 0; min-height: 0; display: flex; flex-direction: column; background: var(--surface); }
    .viewbar {
      height: 40px;
      flex: 0 0 40px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid var(--line);
      background: var(--surface-raised);
      padding: 0 8px 0 4px;
    }
    .tabs { height: 100%; display: flex; align-items: stretch; }
    .tab-button {
      min-width: 98px;
      padding: 0 14px;
      border: 0;
      border-bottom: 2px solid transparent;
      background: transparent;
      color: var(--muted);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 7px;
    }
    .tab-button:hover { color: var(--text); background: rgba(255, 255, 255, 0.025); }
    .tab-button.active { color: var(--text); border-bottom-color: var(--selected); }
    .view-actions { display: flex; align-items: center; gap: 6px; }
    .pending-count { color: var(--pending); font-size: 11px; }

    .table-wrap { min-height: 0; flex: 1; overflow: auto; }
    table { width: 100%; border-collapse: collapse; table-layout: fixed; font-size: 11px; }
    th {
      position: sticky;
      top: 0;
      z-index: 2;
      height: 31px;
      padding: 0 8px;
      text-align: left;
      background: #181f27;
      border-bottom: 1px solid var(--line-strong);
      color: var(--muted);
      font-weight: 600;
    }
    td { height: 35px; padding: 3px 8px; border-bottom: 1px solid rgba(42, 51, 62, 0.58); vertical-align: middle; }
    tr:hover td { background: rgba(102, 166, 255, 0.045); }
    tr.selected td { background: rgba(102, 166, 255, 0.085); }
    tr.pending td:first-child { box-shadow: inset 2px 0 0 var(--pending); }
    th:nth-child(1) { width: 28%; }
    th:nth-child(2) { width: 19%; }
    th:nth-child(3) { width: 9%; }
    th:nth-child(4), th:nth-child(5) { width: 15%; }
    th:nth-child(6) { width: 14%; }
    .register-name { display: flex; align-items: center; min-width: 0; gap: 6px; }
    .register-name .label { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .indent { display: inline-block; width: calc(var(--depth) * 14px); flex: 0 0 auto; }
    .twisty-spacer { width: 22px; flex: 0 0 22px; }
    .value-input { width: 100%; min-width: 72px; height: 27px; font-size: 11px; }
    .value-input.pending { border-color: #876827; color: #ffdb83; background: #19150d; }
    .value-input.invalid { border-color: var(--danger); }
    .live-value { color: var(--text-soft); cursor: copy; }
    .row-actions { display: flex; align-items: center; gap: 3px; }

    .memory-toolbar { padding: 7px 8px; border-bottom: 1px solid var(--line); display: flex; align-items: center; gap: 6px; }
    .memory-tabs { flex: 1; min-width: 0; display: flex; gap: 4px; overflow-x: auto; }
    .memory-tab { height: 29px; padding: 0 10px; border: 1px solid var(--line); border-radius: 4px; background: transparent; color: var(--muted); cursor: pointer; white-space: nowrap; }
    .memory-tab.active { border-color: #497dbb; background: #172538; color: var(--text); }
    .memory-grid { padding: 8px; min-width: 570px; }
    .memory-header, .memory-row { display: grid; grid-template-columns: 110px repeat(4, minmax(90px, 1fr)); gap: 5px; }
    .memory-header { padding-bottom: 5px; color: var(--muted); font-size: 10px; text-align: center; }
    .memory-row { margin-bottom: 5px; align-items: center; }
    .memory-row > .address { padding-left: 7px; }
    .memory-input { width: 100%; height: 28px; font-size: 11px; text-align: center; }

    .inspector-body { padding: 12px; }
    .inspector-kicker { color: var(--selected); font-size: 10px; font-weight: 700; text-transform: uppercase; }
    .inspector-name { font-size: 16px; font-weight: 700; margin: 5px 0 12px; overflow-wrap: anywhere; }
    .property-list { display: grid; grid-template-columns: 72px minmax(0, 1fr); gap: 7px 9px; margin: 0 0 16px; font-size: 11px; }
    .property-list dt { color: var(--muted); }
    .property-list dd { margin: 0; color: var(--text-soft); overflow-wrap: anywhere; }
    .section-label { margin: 15px 0 8px; color: var(--muted); font-size: 10px; font-weight: 700; text-transform: uppercase; }
    .bit-grid { display: grid; grid-template-columns: repeat(16, minmax(10px, 1fr)); gap: 2px; }
    .bit-cell { height: 28px; min-width: 0; border: 1px solid var(--line); border-radius: 2px; background: #11161c; color: #65717d; display: grid; place-items: center; font-size: 8px; }
    .bit-cell.on { background: #123f38; border-color: #247c6c; color: #a8f1e4; }
    .bit-cell.pending { box-shadow: inset 0 -2px 0 var(--pending); }
    .description { color: var(--text-soft); font-size: 12px; line-height: 1.55; white-space: pre-wrap; overflow-wrap: anywhere; }

    .console-dock { height: var(--console-height); min-height: 84px; max-height: 45vh; flex: 0 0 var(--console-height); background: #0d1217; display: flex; flex-direction: column; }
    .console-dock.collapsed { height: 40px; min-height: 40px; flex-basis: 40px; }
    .console-head { height: 36px; flex: 0 0 36px; display: flex; align-items: center; justify-content: space-between; padding: 0 8px 0 12px; border-bottom: 1px solid var(--line); }
    .console-title { display: flex; align-items: center; gap: 8px; color: var(--text-soft); font-size: 11px; font-weight: 700; }
    .console-body { min-height: 0; flex: 1; display: grid; grid-template-columns: minmax(0, 1fr) 320px; }
    .console-lines { overflow: auto; padding: 7px 10px; color: #aab5bf; font-size: 10px; line-height: 1.55; border-right: 1px solid var(--line); }
    .console-line { white-space: pre-wrap; }
    .commander { display: flex; align-items: flex-end; gap: 6px; padding: 8px; }
    .commander input { min-width: 0; flex: 1; }

    .statusbar {
      height: 25px;
      flex: 0 0 25px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 0 10px;
      border-top: 1px solid var(--line);
      background: #11161c;
      color: var(--muted);
      font-size: 10px;
    }
    .status-group { display: flex; align-items: center; gap: 13px; min-width: 0; }
    .status-item { display: inline-flex; align-items: center; gap: 5px; white-space: nowrap; }
    .status-item.pending { color: var(--pending); }
    .switch { display: inline-flex; align-items: center; gap: 6px; cursor: pointer; }
    .switch input { width: 13px; height: 13px; margin: 0; accent-color: var(--connected); }
    .rate-select { width: 66px; height: 21px; padding: 0 4px; border-radius: 3px; font-size: 10px; }

    .more-menu { position: relative; }
    .more-menu > summary { list-style: none; }
    .more-menu > summary::-webkit-details-marker { display: none; }
    .menu-popover {
      position: absolute;
      right: 0;
      top: 37px;
      width: 218px;
      padding: 5px;
      border: 1px solid var(--line-strong);
      border-radius: 6px;
      background: #1b222b;
      box-shadow: 0 14px 36px rgba(0, 0, 0, 0.38);
      z-index: 20;
    }
    .menu-item { width: 100%; height: 33px; padding: 0 9px; border: 0; border-radius: 4px; background: transparent; color: var(--text-soft); display: flex; align-items: center; gap: 9px; cursor: pointer; text-align: left; }
    .menu-item:hover:not(:disabled) { background: var(--surface-hover); color: var(--text); }
    .menu-item:disabled { opacity: 0.38; }
    .menu-separator { height: 1px; background: var(--line); margin: 5px; }
    .menu-toggle { padding: 7px 9px; display: flex; justify-content: space-between; align-items: center; color: var(--text-soft); font-size: 12px; }

    .empty { height: 100%; min-height: 120px; display: grid; place-items: center; padding: 24px; text-align: center; color: var(--muted); }
    .empty-content { max-width: 330px; }
    .empty-icon { width: 34px; height: 34px; margin: 0 auto 9px; color: #56616d; }
    .empty-title { color: var(--text-soft); font-size: 13px; font-weight: 700; margin-bottom: 4px; }
    .empty-copy { font-size: 11px; line-height: 1.5; margin-bottom: 12px; }

    .startup-shell { height: 100%; display: flex; flex-direction: column; background: var(--canvas); }
    .startup-head { height: 56px; flex: 0 0 56px; padding: 0 17px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--line); background: #11161c; }
    .startup-main { flex: 1; min-height: 0; display: grid; grid-template-columns: minmax(410px, 560px) minmax(300px, 1fr); }
    .startup-form { display: flex; flex-direction: column; justify-content: center; padding: 48px clamp(38px, 6vw, 82px); border-right: 1px solid var(--line); }
    .startup-kicker { color: var(--connected); font-size: 11px; font-weight: 700; margin-bottom: 10px; }
    .startup-title { margin: 0 0 9px; font-size: 30px; line-height: 1.13; letter-spacing: 0; }
    .startup-copy { margin: 0 0 29px; color: var(--muted); font-size: 13px; line-height: 1.55; }
    .field { margin-bottom: 16px; }
    .field label { display: block; margin-bottom: 6px; color: var(--text-soft); font-size: 11px; font-weight: 600; }
    .field select, .field input { width: 100%; }
    .segment { display: flex; gap: 5px; flex-wrap: wrap; }
    .segment button { flex: 1 1 80px; }
    .segment button.active { border-color: var(--connected); background: #13352f; color: #c8fff5; }
    .segment button.active:hover:not(:disabled) { border-color: var(--connected); background: #17443c; color: #e6fffb; }
    .startup-action { margin-top: 7px; justify-content: space-between; }
    .startup-detail { display: flex; flex-direction: column; justify-content: center; padding: 48px clamp(36px, 6vw, 90px); background: #10151b; }
    .instrument-line { display: grid; grid-template-columns: repeat(16, 1fr); gap: 4px; margin-bottom: 28px; }
    .instrument-line i { height: 8px; background: #202933; border: 1px solid #2d3844; border-radius: 2px; }
    .instrument-line i:nth-child(4n+1), .instrument-line i:nth-child(11) { background: #164b42; border-color: #247a6b; }
    .detail-title { font-size: 12px; color: var(--text-soft); font-weight: 700; margin-bottom: 12px; }

    .toast-stack { position: fixed; right: 12px; bottom: 38px; z-index: 50; display: flex; flex-direction: column; gap: 7px; pointer-events: none; }
    .toast { width: min(380px, calc(100vw - 24px)); padding: 10px 12px; border: 1px solid var(--line-strong); border-radius: 6px; background: #1b222b; color: var(--text); box-shadow: 0 13px 34px rgba(0, 0, 0, 0.35); font-size: 12px; animation: toast-in 150ms ease-out; }
    .toast.success { border-color: #267b6b; }
    .toast.warning { border-color: #806322; color: #f9dda0; }
    .toast.error { border-color: #7e343a; color: #ffc5c5; }
    @keyframes toast-in { from { opacity: 0; transform: translateY(5px); } }

    .busy {
      position: fixed;
      left: 50%;
      top: 9px;
      transform: translateX(-50%);
      z-index: 60;
      height: 30px;
      padding: 0 12px;
      border: 1px solid var(--line-strong);
      border-radius: 5px;
      background: #1b222b;
      display: none;
      align-items: center;
      gap: 8px;
      color: var(--text-soft);
      font-size: 11px;
      box-shadow: 0 10px 28px rgba(0, 0, 0, 0.32);
    }
    .busy.show { display: flex; }
    .busy-spinner { width: 12px; height: 12px; border: 2px solid #3c4752; border-top-color: var(--connected); border-radius: 50%; animation: spin 700ms linear infinite; }
    @keyframes spin { to { transform: rotate(360deg); } }

    .modal-backdrop { position: fixed; inset: 0; z-index: 70; display: grid; place-items: center; padding: 24px; background: rgba(5, 8, 11, 0.72); }
    .modal { width: min(520px, 100%); max-height: min(680px, calc(100vh - 48px)); display: flex; flex-direction: column; border: 1px solid var(--line-strong); border-radius: 7px; background: #171d24; box-shadow: 0 24px 60px rgba(0, 0, 0, 0.48); }
    .modal-head { height: 46px; flex: 0 0 46px; display: flex; align-items: center; justify-content: space-between; padding: 0 10px 0 15px; border-bottom: 1px solid var(--line); }
    .modal-title { font-size: 13px; font-weight: 700; }
    .modal-body { min-height: 0; overflow: auto; padding: 16px; }
    .modal-copy { margin: 0 0 15px; color: var(--text-soft); font-size: 12px; line-height: 1.5; }
    .modal-actions { display: flex; justify-content: flex-end; gap: 7px; padding: 11px 14px; border-top: 1px solid var(--line); }
    .change-list { border: 1px solid var(--line); border-radius: 5px; overflow: hidden; }
    .change-row { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 10px; padding: 8px 10px; border-bottom: 1px solid var(--line); font-size: 11px; }
    .change-row:last-child { border-bottom: 0; }
    .change-name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--text-soft); }
    .change-values { color: var(--muted); white-space: nowrap; }
    .change-values strong { color: var(--pending); font-weight: 600; }
    .form-error { min-height: 17px; color: #ff9c9c; font-size: 11px; }

    @media (max-width: 1120px) {
      .targetbar { grid-template-columns: 175px minmax(280px, 1fr) auto; gap: 8px; }
      .connection-state .state-text { display: none; }
      .button .responsive-label { display: none; }
      .button.responsive { width: 32px; padding: 0; }
      .console-body { grid-template-columns: minmax(0, 1fr) 270px; }
      th:nth-child(3), td:nth-child(3) { display: none; }
      th:nth-child(1) { width: 27%; }
      th:nth-child(2) { width: 21%; }
      th:nth-child(4) { width: 19%; }
      th:nth-child(5) { width: 15%; }
      th:nth-child(6) { width: 18%; }
      td { padding-left: 6px; padding-right: 6px; }
    }
    @media (prefers-reduced-motion: reduce) {
      *, *:before, *:after { animation-duration: 0.01ms !important; animation-iteration-count: 1 !important; }
    }
  </style>
</head>
<body>
  <div id="app"></div>
  <div id="busy" class="busy"><span class="busy-spinner"></span><span id="busyText">Working</span></div>
  <div id="toastStack" class="toast-stack" aria-live="polite"></div>
  <div id="modalRoot"></div>

  <script>
    let state = null;
    let activeView = "registers";
    let selectedItem = null;
    let deviceQuery = "";
    let autoTimer = null;
    let refreshInFlight = false;
    let lastRefreshAt = null;
    let refreshRate = 1000;
    let consoleCollapsed = false;
    let modal = null;
    const collapsedModify = new Set();
    const layout = { explorer: 310, inspector: 292, console: 176 };

    // Path data follows Lucide's open icon set; keeping it inline preserves offline packaging.
    const ICONS = {
      activity: '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
      arrowDown: '<path d="M12 5v14"/><path d="m19 12-7 7-7-7"/>',
      arrowLeft: '<path d="m12 19-7-7 7-7"/><path d="M19 12H5"/>',
      arrowRight: '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
      arrowUp: '<path d="m5 12 7-7 7 7"/><path d="M12 19V5"/>',
      check: '<path d="m20 6-11 11-5-5"/>',
      chevronDown: '<path d="m6 9 6 6 6-6"/>',
      chevronRight: '<path d="m9 18 6-6-6-6"/>',
      chip: '<rect width="16" height="16" x="4" y="4" rx="2"/><rect width="6" height="6" x="9" y="9" rx="1"/><path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3"/>',
      copy: '<rect width="14" height="14" x="8" y="8" rx="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>',
      download: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m7 10 5 5 5-5"/><path d="M12 15V3"/>',
      ellipsis: '<circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/><circle cx="5" cy="12" r="1"/>',
      fileOutput: '<path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><path d="M12 18v-6"/><path d="m9 15 3 3 3-3"/>',
      folderOpen: '<path d="m6 14 1.5-2.9A2 2 0 0 1 9.24 10H20a2 2 0 0 1 1.94 2.5l-1.54 6a2 2 0 0 1-1.95 1.5H4a2 2 0 0 1-2-2V5c0-1.1.9-2 2-2h3.9a2 2 0 0 1 1.69.9l.81 1.2a2 2 0 0 0 1.67.9H18a2 2 0 0 1 2 2v2"/>',
      memory: '<path d="M6 19v-3M10 19v-3M14 19v-3M18 19v-3M8 11V9M16 11V9M12 11V9M2 15h20M2 5h20M6 5V2M10 5V2M14 5V2M18 5V2"/><rect width="20" height="10" x="2" y="5" rx="2"/>',
      panelBottom: '<rect width="18" height="18" x="3" y="3" rx="2"/><path d="M3 15h18"/>',
      pencil: '<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/>',
      play: '<polygon points="6 3 20 12 6 21 6 3"/>',
      plug: '<path d="M12 22v-5"/><path d="M9 7V2"/><path d="M15 7V2"/><path d="M6 13V8h12v5a6 6 0 0 1-12 0Z"/>',
      plus: '<path d="M5 12h14"/><path d="M12 5v14"/>',
      refresh: '<path d="M21 12a9 9 0 0 0-15-6.7L3 8"/><path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 15 6.7L21 16"/><path d="M16 16h5v5"/>',
      save: '<path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2Z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/>',
      search: '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
      terminal: '<polyline points="4 17 10 11 4 5"/><line x1="12" x2="20" y1="19" y2="19"/>',
      trash: '<path d="M3 6h18"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/><path d="m19 6-1 14c-.1 1-1 2-2 2H8c-1 0-1.9-1-2-2L5 6"/><path d="M10 11v6M14 11v6"/>',
      upload: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m17 8-5-5-5 5"/><path d="M12 3v12"/>',
      x: '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>'
    };

    const $ = (id) => document.getElementById(id);
    const icon = (name, small = false) => `<svg class="icon${small ? " small" : ""}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICONS[name] || ""}</svg>`;
    const esc = (value) => String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
    const pathArg = (path) => JSON.stringify(path);
    const pathKey = (path) => path.join(".");
    const toHex = (value) => {
      const number = Number(value);
      return "0x" + (Number.isFinite(number) ? (Math.trunc(number) >>> 0).toString(16).padStart(8, "0") : "????????");
    };
    const valuesMatch = (left, right) => {
      try { return BigInt(String(left).trim()) === BigInt(String(right).trim()); }
      catch (_) {
        try { return BigInt("0x" + String(left).trim().replace(/^0x/i, "")) === BigInt("0x" + String(right).trim().replace(/^0x/i, "")); }
        catch (_) { return false; }
      }
    };

    function setBusy(on, text = "Working") {
      $("busyText").textContent = text;
      $("busy").classList.toggle("show", on);
    }

    function showToast(message, type = "error") {
      const toast = document.createElement("div");
      toast.className = `toast ${type}`;
      toast.textContent = message;
      $("toastStack").appendChild(toast);
      setTimeout(() => toast.remove(), type === "error" ? 6200 : 3600);
    }

    async function invoke(name, args = [], options = {}) {
      const settings = { renderState: true, busy: true, busyText: "Working", success: "", ...options };
      if (!window.pywebview || !window.pywebview.api) {
        showToast("PyWebView bridge is not ready.");
        return null;
      }
      if (settings.busy) setBusy(true, settings.busyText);
      try {
        const result = await window.pywebview.api[name](...args);
        if (!result.ok) {
          if (result.data) render(result.data);
          showToast(result.error || "Command failed.");
          return null;
        }
        if (result.data && settings.renderState && Object.prototype.hasOwnProperty.call(result.data, "configs")) {
          render(result.data);
        }
        if (settings.success) showToast(settings.success, "success");
        return result.data;
      } catch (error) {
        showToast(String(error));
        return null;
      } finally {
        if (settings.busy) setBusy(false);
      }
    }

    function render(nextState) {
      const scroll = captureScroll();
      if (!nextState.connected && autoTimer) {
        clearInterval(autoTimer);
        autoTimer = null;
      }
      state = nextState;
      if (!state.launched) renderStartup();
      else renderWorkspace();
      requestAnimationFrame(() => restoreScroll(scroll));
    }

    function renderStartup() {
      const preferred = loadPreference("lastChip");
      const current = state.configs.find((item) => item.name === preferred) || state.currentConfig || state.configs[0] || null;
      const chipOptions = state.configs.map((item) => `<option value="${esc(item.name)}" ${current && current.name === item.name ? "selected" : ""}>${esc(item.name)}</option>`).join("");
      const selectedTif = current ? (loadPreference(`tif:${current.name}`) || current.selectedTif || current.tifOptions[0]) : "";
      $("app").innerHTML = `
        <div class="startup-shell">
          <header class="startup-head">
            ${renderBrand("Embedded register and memory workspace")}
            <span class="panel-meta">${state.configs.length} target profiles available</span>
          </header>
          <main class="startup-main">
            <section class="startup-form">
              <div class="startup-kicker">TARGET SETUP</div>
              <h1 class="startup-title">Open a hardware workspace</h1>
              <p class="startup-copy">Choose the target profile and transport interface used for this debugging session.</p>
              <div class="field">
                <label for="chipSelect">Target chip</label>
                <select id="chipSelect" onchange="syncStartupTif()" ${state.configs.length ? "" : "disabled"}>${chipOptions}</select>
              </div>
              <div class="field">
                <label>Transport interface</label>
                <div id="tifSegment" class="segment">${renderTifSegment(current, selectedTif)}</div>
              </div>
              <button class="button primary startup-action" onclick="launchWorkspace()" ${current ? "" : "disabled"}><span>Open workspace</span>${icon("arrowRight")}</button>
            </section>
            <aside class="startup-detail">
              <div class="instrument-line">${Array.from({length: 16}, () => "<i></i>").join("")}</div>
              <div class="detail-title">Session profile</div>
              <dl id="startupDetails" class="property-list">${renderStartupDetails(current, selectedTif)}</dl>
            </aside>
          </main>
        </div>`;
    }

    function renderBrand(subtitle) {
      return `<div class="brand"><span class="brand-mark" aria-hidden="true">${Array.from({length: 8}, () => "<i></i>").join("")}</span><span class="brand-copy"><div class="brand-title">JGKit</div><div class="brand-sub">${esc(subtitle)}</div></span></div>`;
    }

    function renderTifSegment(config, selected) {
      if (!config || !config.tifOptions.length) return `<span class="panel-meta">No interfaces configured</span>`;
      return config.tifOptions.map((item) => `<button type="button" class="button ${item === selected ? "active" : ""}" data-tif="${esc(item)}" onclick="selectTif(this)">${esc(item)}</button>`).join("");
    }

    function renderStartupDetails(config, tif) {
      if (!config) return `<dt>Status</dt><dd>No valid target profiles were found.</dd>`;
      return `<dt>Chip</dt><dd>${esc(config.name)}</dd><dt>Core</dt><dd>${esc(config.core)}</dd><dt>Interface</dt><dd>${esc(tif)}</dd><dt>Register map</dt><dd>${esc(config.excel || "Not configured")}</dd><dt>Sheets</dt><dd>${esc((config.sheets || []).join(", ") || "Automatic")}</dd>`;
    }

    function syncStartupTif() {
      const config = state.configs.find((item) => item.name === $("chipSelect").value);
      const tif = loadPreference(`tif:${config.name}`) || config.selectedTif || config.tifOptions[0];
      $("tifSegment").innerHTML = renderTifSegment(config, tif);
      $("startupDetails").innerHTML = renderStartupDetails(config, tif);
    }

    function selectTif(button) {
      document.querySelectorAll("#tifSegment .button").forEach((item) => item.classList.toggle("active", item === button));
      const config = state.configs.find((item) => item.name === $("chipSelect").value);
      $("startupDetails").innerHTML = renderStartupDetails(config, button.dataset.tif);
    }

    function launchWorkspace() {
      const chip = $("chipSelect").value;
      const selected = document.querySelector("#tifSegment .active");
      if (!chip || !selected) return;
      savePreference("lastChip", chip);
      savePreference(`tif:${chip}`, selected.dataset.tif);
      collapsedModify.clear();
      selectedItem = null;
      invoke("launch", [chip, selected.dataset.tif], { busyText: "Loading target map" });
    }

    function renderWorkspace() {
      applyLayout();
      const cfg = state.currentConfig || {};
      $("app").innerHTML = `
        <div class="app-shell">
          <header class="targetbar">
            ${renderBrand("Register and memory instrument")}
            <div class="target-context">
              <div class="target-chip">${icon("chip")}<strong>${esc(cfg.name || "No target")}</strong><span>${esc(cfg.selectedTif || "")}</span></div>
              ${renderCoreSelect()}
              <button class="button icon-button ghost" title="Change target" aria-label="Change target" onclick="invoke('back_to_startup', [], {busyText:'Closing workspace'})">${icon("ellipsis")}</button>
            </div>
            <div class="connection-cluster">
              <span class="connection-state"><span class="state-dot ${state.connected ? "on" : ""}"></span><span class="state-text">${state.connected ? "Connected" : "Disconnected"}</span></span>
              ${state.connected
                ? `<button class="button danger responsive" aria-label="Disconnect" onclick="openModal('disconnect')">${icon("plug")}<span class="responsive-label">Disconnect</span></button>`
                : `<button class="button primary" onclick="connectTarget()">${icon("plug")}Connect</button>`}
              ${renderMoreMenu()}
            </div>
          </header>
          ${state.debugMode ? `<div class="simulation-banner">${icon("activity", true)} SIMULATION MODE · values are generated locally and are not read from hardware</div>` : ""}
          <div id="workbench" class="workbench">
            ${renderExplorer()}
            <div class="resizer vertical" onpointerdown="startResize(event, 'explorer')"></div>
            ${renderCenterPanel()}
            <div class="resizer vertical" onpointerdown="startResize(event, 'inspector')"></div>
            ${renderInspector()}
          </div>
          ${renderConsole()}
          ${renderStatusbar()}
        </div>`;
      $("modalRoot").innerHTML = modal ? renderModal() : "";
      applyLayout();
      if (modal) requestAnimationFrame(() => document.querySelector(".modal input")?.focus());
    }

    function renderCoreSelect() {
      if (!state.coreOptions.length) return "";
      const options = state.coreOptions.map((core) => `<option value="${esc(core)}" ${state.coreValue === core ? "selected" : ""}>${esc(core)}</option>`).join("");
      return `<select id="coreSelect" title="Target core" ${state.connected ? "disabled" : ""} onchange="invoke('set_core', [this.value], {busy:false})">${options}</select>`;
    }

    function renderMoreMenu() {
      return `<details class="more-menu">
        <summary class="button icon-button" title="More actions" aria-label="More actions">${icon("ellipsis")}</summary>
        <div class="menu-popover">
          <button class="menu-item" onclick="invoke('open_regcfg', [], {busyText:'Opening register configuration', success:'Configuration loaded for review'})">${icon("folderOpen")}Open register config</button>
          <button class="menu-item" ${state.modifyItems.length ? "" : "disabled"} onclick="invoke('save_regcfg', [], {busyText:'Saving register configuration', success:'Register configuration saved'})">${icon("save")}Save register config</button>
          <button class="menu-item" ${state.connected && state.modifyItems.length ? "" : "disabled"} onclick="invoke('save_glicfg', [], {busyText:'Exporting glimpse', success:'Glimpse exported'})">${icon("fileOutput")}Export glimpse</button>
          <div class="menu-separator"></div>
          <label class="menu-toggle"><span>Simulation mode</span><input type="checkbox" ${state.debugMode ? "checked" : ""} onchange="invoke('set_debug_mode', [this.checked], {busyText:'Changing link mode'})"></label>
          <div class="menu-separator"></div>
          <button class="menu-item" onclick="invoke('back_to_startup', [], {busyText:'Closing workspace'})">${icon("chip")}Change target</button>
        </div>
      </details>`;
    }

    function renderExplorer() {
      return `<aside class="panel explorer">
        <div class="panel-head"><span class="panel-title">Device explorer</span><span class="panel-meta">${state.deviceNodes.length} devices</span></div>
        <div class="search-wrap">${icon("search", true)}<input id="deviceSearch" value="${esc(deviceQuery)}" placeholder="Search name or address" oninput="filterDeviceTree(this.value)"></div>
        <div class="panel-head"><span class="panel-meta">Register map</span><span class="panel-tools"><button class="button icon-button tiny ghost" title="Expand all" aria-label="Expand all" onclick="setAllTreeNodes(true)">${icon("chevronDown", true)}</button><button class="button icon-button tiny ghost" title="Collapse all" aria-label="Collapse all" onclick="setAllTreeNodes(false)">${icon("chevronRight", true)}</button></span></div>
        <div id="deviceTree" class="scroll tree">${renderDeviceTree()}</div>
      </aside>`;
    }

    function renderDeviceTree() {
      if (!state.deviceNodes.length) return renderEmpty("chip", "No register map", "The selected profile did not produce any devices.");
      const query = deviceQuery.trim().toLowerCase();
      const nodes = state.deviceNodes.map((device, index) => renderDeviceNode(device, [index], query)).filter(Boolean);
      return nodes.length ? nodes.join("") : renderEmpty("search", "No matching registers", "Try another name, address, or field property.");
    }

    function renderDeviceNode(device, path, query) {
      const selfMatch = sourceMatches(device, query);
      const children = device.children.map((item, index) => renderSourceRegister(item, [...path, index], query, selfMatch)).filter(Boolean);
      if (query && !selfMatch && !children.length) return "";
      return `<details class="tree-node" ${query ? "open" : ""}>
        <summary class="tree-row" onclick="selectSource(${pathArg(path)})">
          <span class="node-name"><span class="node-glyph device"></span><span>${esc(device.name)}</span></span>
          <span class="address">${esc(device.address)}</span>${renderTrackButton(device.name, device.address, path)}
        </summary>${children.join("")}
      </details>`;
    }

    function renderSourceRegister(item, path, query, parentMatched = false) {
      const selfMatch = sourceMatches(item, query);
      const children = item.children.map((child, index) => renderSourceField(child, [...path, index], query, selfMatch || parentMatched)).filter(Boolean);
      if (query && !parentMatched && !selfMatch && !children.length) return "";
      if (!item.children.length) return renderSourceField(item, path, query, parentMatched);
      return `<details class="tree-node" ${query ? "open" : ""}>
        <summary class="tree-row" onclick="selectSource(${pathArg(path)})">
          <span class="node-name"><span class="node-glyph register"></span><span>${esc(item.name)}</span></span>
          <span class="address">${esc(item.addressExpr)}</span>${renderTrackButton(item.name, item.addressExpr, path)}
        </summary>${children.join("")}
      </details>`;
    }

    function renderSourceField(item, path, query, parentMatched = false) {
      if (query && !parentMatched && !sourceMatches(item, query)) return "";
      return `<div class="tree-row leaf" onclick="selectSource(${pathArg(path)})">
        <span class="node-name"><span class="node-glyph field"></span><span>${esc(item.name)}</span></span>
        <span><span class="address">${esc(item.addressExpr)}</span> <span class="access">${esc(item.property)}</span></span>
        ${renderTrackButton(item.name, item.addressExpr, path)}
      </div>`;
    }

    function renderTrackButton(name, address, path) {
      const tracked = isTracked(name, address);
      return `<button class="button icon-button tiny ghost ${tracked ? "tracked" : ""}" title="${tracked ? "Already tracked" : "Track register"}" aria-label="${tracked ? "Already tracked" : "Track register"}" ${tracked || !state.connected ? "disabled" : ""} onclick="event.stopPropagation(); invoke('add_modify_item', [${pathArg(path)}], {busyText:'Reading register', success:'Register added'})">${icon(tracked ? "check" : "plus", true)}</button>`;
    }

    function renderCenterPanel() {
      const pending = pendingItems();
      return `<main class="center-panel">
        <div class="viewbar">
          <div class="tabs">
            <button class="tab-button ${activeView === "registers" ? "active" : ""}" onclick="setActiveView('registers')">${icon("activity", true)}Registers</button>
            <button class="tab-button ${activeView === "memory" ? "active" : ""}" onclick="setActiveView('memory')">${icon("memory", true)}Memory</button>
          </div>
          <div class="view-actions">${activeView === "registers" ? renderRegisterActions(pending) : renderMemoryActions()}</div>
        </div>
        ${activeView === "registers" ? renderRegisterView() : renderMemoryView()}
      </main>`;
    }

    function renderRegisterActions(pending) {
      return `<span class="pending-count">${pending.length ? `${pending.length} pending` : "No pending changes"}</span>
        <button class="button icon-button" title="Refresh registers" aria-label="Refresh registers" ${state.connected ? "" : "disabled"} onclick="refreshLive(true)">${icon("refresh")}</button>
        <button id="applyButton" class="button apply" ${state.connected && pending.length ? "" : "disabled"} onclick="openModal('apply')">${icon("upload")}Apply ${pending.length || ""}</button>`;
    }

    function renderRegisterView() {
      if (!state.modifyItems.length) return renderEmpty("activity", "No tracked registers", state.connected ? "Add registers from Device explorer to inspect live values." : "Connect to the target, then add registers from Device explorer.", state.connected ? `<button class="button" onclick="$('deviceSearch').focus()">${icon("search")}Find registers</button>` : "");
      const rows = [];
      state.modifyItems.forEach((item, index) => pushModifyRows(rows, item, [index], 0));
      return `<div id="registerScroll" class="table-wrap"><table><thead><tr><th>Name</th><th>Address / field</th><th>Access</th><th>Target value</th><th>Live value</th><th>Actions</th></tr></thead><tbody>${rows.join("")}</tbody></table></div>`;
    }

    function pushModifyRows(rows, item, path, depth) {
      const key = pathKey(path);
      const hasChildren = item.children.length > 0;
      const collapsed = collapsedModify.has(key);
      const selected = selectedItem && selectedItem.kind === "modify" && pathKey(selectedItem.path) === key;
      const canWrite = isWritable(item);
      const write = item.writeValue === "NA" ? "" : item.writeValue;
      const toggle = hasChildren
        ? `<button class="button icon-button tiny ghost" title="${collapsed ? "Expand" : "Collapse"}" aria-label="${collapsed ? "Expand" : "Collapse"}" onclick="event.stopPropagation(); toggleModify(${pathArg(path)})">${icon(collapsed ? "chevronRight" : "chevronDown", true)}</button>`
        : `<span class="twisty-spacer"></span>`;
      rows.push(`<tr data-row-path="${key}" class="${selected ? "selected " : ""}${item.pending ? "pending" : ""}" onclick="selectModify(${pathArg(path)})">
        <td><div class="register-name"><span class="indent" style="--depth:${depth}"></span>${toggle}<span class="node-glyph ${item.level === 0 ? "device" : (hasChildren ? "register" : "field")}"></span><span class="label">${esc(item.name)}</span></div></td>
        <td class="address">${esc(item.addressExpr)}</td>
        <td class="access">${esc(item.property)}</td>
        <td><input class="value-input ${item.pending ? "pending" : ""}" value="${esc(write)}" placeholder="${canWrite ? "0x0" : "Read only"}" ${state.connected && canWrite ? "" : "disabled"} onfocus="this.dataset.before=this.value" onblur="stageWrite(${pathArg(path)}, this.value)" onkeydown="if(event.key==='Enter'){this.blur()}if(event.key==='Escape'){this.value=this.dataset.before||'';this.blur()}"></td>
        <td class="live-value mono" data-live-path="${key}" title="Click to copy live value" onclick="event.stopPropagation(); copyText('${esc(item.readValue)}', 'Live value copied')">${esc(item.readValue)}</td>
        <td><div class="row-actions"><button class="button icon-button tiny ghost" title="Read now" aria-label="Read now" ${state.connected && item.level !== 0 ? "" : "disabled"} onclick="event.stopPropagation(); invoke('read_item', [${pathArg(path)}], {busyText:'Reading register'})">${icon("refresh", true)}</button><button class="button icon-button tiny ghost" title="Copy address" aria-label="Copy address" onclick="event.stopPropagation(); copyText('${esc(item.addressExpr)}')">${icon("copy", true)}</button><button class="button icon-button tiny ghost danger" title="Remove from tracked registers" aria-label="Remove from tracked registers" onclick="event.stopPropagation(); invoke('remove_modify_item', [${pathArg(path)}], {busy:false, success:'Register removed'})">${icon("trash", true)}</button></div></td>
      </tr>`);
      if (!collapsed) item.children.forEach((child, index) => pushModifyRows(rows, child, [...path, index], depth + 1));
    }

    function renderMemoryActions() {
      const hasTab = state.memoryTabs.length > 0;
      return `<button class="button" ${state.connected ? "" : "disabled"} onclick="openModal('addMemory')">${icon("plus")}Add view</button>
        <button class="button icon-button" title="Memory actions" aria-label="Memory actions" ${hasTab ? "" : "disabled"} onclick="openModal('memoryActions')">${icon("ellipsis")}</button>`;
    }

    function renderMemoryView() {
      if (!state.memoryTabs.length) return renderEmpty("memory", "No memory views", state.connected ? "Open a memory address to inspect a live 32-bit block." : "Connect to the target before opening a memory view.", state.connected ? `<button class="button" onclick="openModal('addMemory')">${icon("plus")}Add memory view</button>` : "");
      return `<div class="memory-toolbar"><div class="memory-tabs">${renderMemoryTabs()}</div><button class="button icon-button tiny ghost" title="Previous block" aria-label="Previous block" ${memoryEnabled()} onclick="invoke('shift_memory', [state.memoryIndex, -1], {busyText:'Reading previous block'})">${icon("arrowLeft", true)}</button><button class="button icon-button tiny ghost" title="Next block" aria-label="Next block" ${memoryEnabled()} onclick="invoke('shift_memory', [state.memoryIndex, 1], {busyText:'Reading next block'})">${icon("arrowRight", true)}</button><button class="button icon-button tiny ghost" title="Refresh memory" aria-label="Refresh memory" ${memoryEnabled()} onclick="invoke('refresh_memory', [state.memoryIndex], {busyText:'Refreshing memory'})">${icon("refresh", true)}</button></div><div id="memoryScroll" class="scroll memory-grid">${renderMemoryGrid()}</div>`;
    }

    function renderMemoryTabs() {
      return state.memoryTabs.map((tab, index) => `<button class="memory-tab ${index === state.memoryIndex ? "active" : ""}" onclick="invoke('select_memory', [${index}], {busy:false})">${esc(tab.name)}</button>`).join("");
    }

    function renderMemoryGrid() {
      const tab = state.memoryTabs[state.memoryIndex];
      if (!tab) return "";
      const rows = [];
      for (let i = 0; i < tab.values.length; i += 4) {
        const cells = [];
        for (let j = 0; j < 4 && i + j < tab.values.length; j += 1) {
          const index = i + j;
          cells.push(`<input class="memory-input" data-memory-index="${index}" value="${esc(toHex(tab.values[index]))}" ${state.connected ? "" : "disabled"} onkeydown="if(event.key==='Enter') writeMemoryWord(${index}, this.value)">`);
        }
        rows.push(`<div class="memory-row"><span class="address">${esc(toHex(tab.headAddress + i * 4))}</span>${cells.join("")}</div>`);
      }
      return `<div class="memory-header"><span>Address</span><span>+0</span><span>+4</span><span>+8</span><span>+C</span></div>${rows.join("")}`;
    }

    function renderInspector() {
      return `<aside class="panel inspector"><div class="panel-head"><span class="panel-title">Inspector</span><span class="panel-meta">32-bit view</span></div><div id="inspectorBody" class="scroll inspector-body">${renderInspectorBody()}</div></aside>`;
    }

    function renderInspectorBody() {
      const item = selectedItem ? (selectedItem.kind === "source" ? getSource(selectedItem.path) : getModify(selectedItem.path)) : null;
      if (!item) return renderEmpty("activity", "Nothing selected", "Select a device, register, or field to inspect its address, access and bit state.");
      const value = item.readValue && item.readValue !== "NA" && item.readValue !== "?" ? item.readValue : null;
      return `<div class="inspector-kicker">${item.level === 0 || item.address ? "Device" : (item.children && item.children.length ? "Register" : "Field")}</div>
        <div class="inspector-name">${esc(item.name)}</div>
        <dl class="property-list"><dt>Address</dt><dd class="mono">${esc(item.addressExpr || item.address || "NA")}</dd><dt>Access</dt><dd>${esc(item.property || "NA")}</dd><dt>Live value</dt><dd class="mono">${esc(value || "Not read")}</dd><dt>Target value</dt><dd class="mono">${esc(item.writeValue && item.writeValue !== "NA" ? item.writeValue : "Not staged")}</dd></dl>
        <div class="section-label">Bit state · 31 to 0</div>${renderBitGrid(value, item.pending)}
        <div class="section-label">Description</div><div class="description">${esc(cleanDescription(item.description))}</div>`;
    }

    function renderBitGrid(value, pending) {
      let number = null;
      try { number = value === null ? null : BigInt(String(value)); }
      catch (_) { number = null; }
      return `<div class="bit-grid">${Array.from({length: 32}, (_, index) => {
        const bit = 31 - index;
        const on = number !== null && ((number >> BigInt(bit)) & 1n) === 1n;
        return `<span class="bit-cell ${on ? "on" : ""}${pending ? " pending" : ""}" title="Bit ${bit}: ${on ? 1 : 0}">${bit}</span>`;
      }).join("")}</div>`;
    }

    function renderConsole() {
      return `<section class="console-dock ${consoleCollapsed ? "collapsed" : ""}">
        ${consoleCollapsed ? "" : `<div class="resizer horizontal" onpointerdown="startResize(event, 'console')"></div>`}
        <div class="console-head"><span class="console-title">${icon("terminal", true)}Console <span class="panel-meta">${state.logs.length} entries</span></span><button class="button icon-button tiny ghost" title="${consoleCollapsed ? "Open console" : "Collapse console"}" aria-label="${consoleCollapsed ? "Open console" : "Collapse console"}" onclick="toggleConsole()">${icon(consoleCollapsed ? "arrowUp" : "arrowDown", true)}</button></div>
        ${consoleCollapsed ? "" : `<div class="console-body"><div id="consoleLines" class="console-lines">${renderLogs()}</div><div class="commander"><input id="commandInput" placeholder="Enter command" onkeydown="if(event.key==='Enter') submitCommand()"><button class="button icon-button" title="Run command" aria-label="Run command" onclick="submitCommand()">${icon("play")}</button></div></div>`}
      </section>`;
    }

    function renderLogs() {
      if (!state.logs.length) return `<div class="panel-meta">Runtime messages will appear here.</div>`;
      return state.logs.slice(-120).map((line) => `<div class="console-line">${esc(line)}</div>`).join("");
    }

    function renderStatusbar() {
      return `<footer class="statusbar">${renderStatusbarBody()}</footer>`;
    }

    function renderStatusbarBody() {
      const pending = pendingItems().length;
      return `<span class="status-group"><span class="status-item">${icon("activity", true)}${state.connected ? "Target online" : "Target offline"}</span><span class="status-item ${pending ? "pending" : ""}">${pending ? `${pending} pending change${pending === 1 ? "" : "s"}` : "No pending changes"}</span><span class="status-item">Last update: ${lastRefreshAt ? lastRefreshAt.toLocaleTimeString() : "Not refreshed"}</span></span><span class="status-group"><label class="switch"><input id="autoRefresh" type="checkbox" ${autoTimer ? "checked" : ""} ${state.connected ? "" : "disabled"} onchange="toggleAutoRefresh(this.checked)">Auto refresh</label><select class="rate-select" aria-label="Refresh interval" onchange="setRefreshRate(this.value)"><option value="600" ${refreshRate === 600 ? "selected" : ""}>0.6 s</option><option value="1000" ${refreshRate === 1000 ? "selected" : ""}>1 s</option><option value="2000" ${refreshRate === 2000 ? "selected" : ""}>2 s</option></select></span>`;
    }

    function renderEmpty(iconName, title, copy, action = "") {
      return `<div class="empty"><div class="empty-content"><div class="empty-icon">${icon(iconName)}</div><div class="empty-title">${esc(title)}</div><div class="empty-copy">${esc(copy)}</div>${action}</div></div>`;
    }

    function renderModal() {
      const close = `<button type="button" class="button icon-button ghost" title="Close" aria-label="Close" onclick="closeModal()">${icon("x")}</button>`;
      if (modal.kind === "apply") {
        const changes = pendingItems();
        return `<div class="modal-backdrop" onclick="if(event.target===this)closeModal()"><section class="modal" role="dialog" aria-modal="true"><div class="modal-head"><span class="modal-title">Apply ${changes.length} pending change${changes.length === 1 ? "" : "s"}</span>${close}</div><div class="modal-body"><p class="modal-copy">JGKit will write each target value and read it back for verification. Review the addresses before continuing.</p><div class="change-list">${changes.map(({item}) => `<div class="change-row"><span class="change-name">${esc(item.name)} <span class="address">${esc(item.addressExpr)}</span></span><span class="change-values">${esc(item.readValue)} → <strong>${esc(item.writeValue)}</strong></span></div>`).join("")}</div></div><div class="modal-actions"><button class="button" onclick="discardPending()">Discard all</button><button class="button" onclick="closeModal()">Cancel</button><button class="button apply" onclick="applyPending()">${icon("upload")}Apply changes</button></div></section></div>`;
      }
      if (modal.kind === "memoryActions") {
        return `<div class="modal-backdrop" onclick="if(event.target===this)closeModal()"><section class="modal" role="dialog" aria-modal="true"><div class="modal-head"><span class="modal-title">Memory view actions</span>${close}</div><div class="modal-body"><div class="change-list"><button class="menu-item" onclick="openModal('renameMemory')">${icon("pencil")}Rename current view</button><button class="menu-item" ${state.connected ? "" : "disabled"} onclick="openModal('importMemory')">${icon("upload")}Import binary data</button><button class="menu-item" ${state.connected ? "" : "disabled"} onclick="openModal('exportMemory')">${icon("download")}Export memory range</button><button class="menu-item danger" onclick="openModal('removeMemory')">${icon("trash")}Remove current view</button></div></div><div class="modal-actions"><button class="button" onclick="closeModal()">Close</button></div></section></div>`;
      }
      const specs = {
        addMemory: ["Add memory view", "Enter the first address of the 32-bit memory block.", [{id:"address", label:"Start address", value:"0x00000000"}], "Add view"],
        renameMemory: ["Rename memory view", "Choose a short name that identifies this address range.", [{id:"name", label:"View name", value:state.memoryTabs[state.memoryIndex]?.name || ""}], "Rename"],
        importMemory: ["Import binary data", "Choose the destination address before selecting a .raw or .bin file.", [{id:"address", label:"Destination address", value:toHex(state.memoryTabs[state.memoryIndex]?.headAddress || 0)}], "Choose file"],
        exportMemory: ["Export memory range", "Enter the first address and byte length to export.", [{id:"start", label:"Start address", value:toHex(state.memoryTabs[state.memoryIndex]?.headAddress || 0)}, {id:"length", label:"Length in bytes", value:String((state.memoryTabs[state.memoryIndex]?.tailAddress || 0) - (state.memoryTabs[state.memoryIndex]?.headAddress || 0))}], "Export"],
        removeMemory: ["Remove memory view", `Remove “${state.memoryTabs[state.memoryIndex]?.name || "this view"}” from the workspace? Hardware memory will not be changed.`, [], "Remove"],
        disconnect: ["Disconnect target", "End the active hardware session? Pending target values will stay in the workspace and will not be written.", [], "Disconnect"]
      };
      const [title, copy, fields, action] = specs[modal.kind];
      const destructive = modal.kind === "removeMemory" || modal.kind === "disconnect";
      return `<div class="modal-backdrop" onclick="if(event.target===this)closeModal()"><form class="modal" role="dialog" aria-modal="true" onsubmit="submitModal(event)"><div class="modal-head"><span class="modal-title">${esc(title)}</span>${close}</div><div class="modal-body"><p class="modal-copy">${esc(copy)}</p>${fields.map((field) => `<div class="field"><label for="modal-${field.id}">${esc(field.label)}</label><input id="modal-${field.id}" name="${field.id}" value="${esc(field.value)}" autocomplete="off"></div>`).join("")}<div id="modalError" class="form-error"></div></div><div class="modal-actions"><button type="button" class="button" onclick="closeModal()">Cancel</button><button type="submit" class="button ${destructive ? "danger" : "primary"}">${modal.kind === "removeMemory" ? icon("trash") : (modal.kind === "disconnect" ? icon("plug") : "")}${esc(action)}</button></div></form></div>`;
    }

    function openModal(kind) { modal = {kind}; renderWorkspace(); }
    function closeModal() { modal = null; $("modalRoot").innerHTML = ""; }

    function submitModal(event) {
      event.preventDefault();
      const form = new FormData(event.currentTarget);
      const fail = (message) => { $("modalError").textContent = message; };
      const addressFields = ["address", "start", "length"];
      for (const field of addressFields) {
        if (form.has(field) && !isValidNumber(form.get(field))) return fail(`${field[0].toUpperCase() + field.slice(1)} must be a decimal or hexadecimal number.`);
      }
      const kind = modal.kind;
      closeModal();
      if (kind === "addMemory") invoke("add_memory", [form.get("address")], {busyText:"Opening memory view", success:"Memory view added"});
      if (kind === "renameMemory") {
        const name = String(form.get("name") || "").trim();
        if (name) invoke("rename_memory", [state.memoryIndex, name], {busy:false, success:"Memory view renamed"});
      }
      if (kind === "importMemory") invoke("import_memory", [state.memoryIndex, form.get("address")], {busyText:"Importing memory data", success:"Memory data imported"});
      if (kind === "exportMemory") invoke("export_memory", [state.memoryIndex, form.get("start"), form.get("length")], {busyText:"Exporting memory data", success:"Memory range exported"});
      if (kind === "removeMemory") invoke("remove_memory", [state.memoryIndex], {busy:false, success:"Memory view removed"});
      if (kind === "disconnect") invoke("disconnect", [], {busyText:"Disconnecting", success:"Target disconnected"});
    }

    function applyPending() {
      const count = pendingItems().length;
      closeModal();
      invoke("upload_modify", [], {busyText:`Applying ${count} changes`, success:`Applied and verified ${count} changes`});
    }

    function discardPending() {
      closeModal();
      invoke("discard_pending", [], {busy:false, success:"Pending changes discarded"});
    }

    function filterDeviceTree(value) {
      deviceQuery = value;
      $("deviceTree").innerHTML = renderDeviceTree();
    }

    function setAllTreeNodes(open) { document.querySelectorAll("#deviceTree details").forEach((item) => { item.open = open; }); }
    function sourceMatches(item, query) { return !query || [item.name, item.address, item.addressExpr, item.property, item.description].some((value) => String(value || "").toLowerCase().includes(query)); }
    function isTracked(name, address) {
      let tracked = false;
      walkModify((item) => { if (item.name === name && item.addressExpr === address) tracked = true; });
      return tracked;
    }

    function selectSource(path) { selectedItem = {kind:"source", path}; updateSelection(); }
    function selectModify(path) { selectedItem = {kind:"modify", path}; updateSelection(); }
    function updateSelection() {
      document.querySelectorAll("tr.selected").forEach((row) => row.classList.remove("selected"));
      if (selectedItem?.kind === "modify") document.querySelector(`[data-row-path="${pathKey(selectedItem.path)}"]`)?.classList.add("selected");
      if ($("inspectorBody")) $("inspectorBody").innerHTML = renderInspectorBody();
    }

    function getSource(path) {
      let item = state.deviceNodes[path[0]];
      if (path.length > 1) item = item.children[path[1]];
      if (path.length > 2) item = item.children[path[2]];
      return item;
    }
    function getModify(path) { let item = state.modifyItems[path[0]]; for (let i = 1; i < path.length; i += 1) item = item.children[path[i]]; return item; }
    function walkModify(callback) { const walk = (items, base = []) => items.forEach((item, index) => { const path = [...base, index]; callback(item, path); walk(item.children, path); }); walk(state.modifyItems); }
    function pendingItems() { const items = []; walkModify((item, path) => { if (item.pending) items.push({item, path}); }); return items; }
    function isWritable(item) { return item.level === 1 || (item.level > 1 && String(item.property).toUpperCase().includes("W")); }

    function toggleModify(path) {
      const key = pathKey(path);
      if (collapsedModify.has(key)) collapsedModify.delete(key); else collapsedModify.add(key);
      renderWorkspace();
    }

    async function stageWrite(path, value) {
      const item = getModify(path);
      const text = String(value || "").trim();
      if (text && !isValidNumber(text)) {
        showToast("Target value must be a decimal or hexadecimal number.");
        renderWorkspace();
        return;
      }
      item.writeValue = text || "NA";
      item.pending = !!text && !valuesMatch(text, item.readValue);
      const data = await invoke("set_write_value", [path, text], {renderState:false, busy:false});
      if (data) {
        state = data;
        renderWorkspace();
      }
    }

    function writeMemoryWord(index, value) {
      if (!isValidNumber(value)) return showToast("Memory value must be a decimal or hexadecimal number.");
      invoke("write_memory_word", [state.memoryIndex, index, value], {busyText:"Writing memory word", success:"Memory word written and refreshed"});
    }

    function setActiveView(view) { activeView = view; selectedItem = null; renderWorkspace(); }
    function memoryEnabled() { return state.connected && state.memoryTabs.length ? "" : "disabled"; }
    function connectTarget() { const core = $("coreSelect") ? $("coreSelect").value : null; invoke("connect", [core], {busyText:"Connecting to target", success:state.debugMode ? "Simulation link connected" : "Target connected"}); }
    function submitCommand() { const input = $("commandInput"); const value = input.value.trim(); if (!value) return; input.value = ""; invoke("commander", [value], {busy:false}); }
    function toggleConsole() { consoleCollapsed = !consoleCollapsed; renderWorkspace(); }

    async function refreshLive(manual = false) {
      if (refreshInFlight || !state.connected) return;
      if (!manual && document.activeElement?.matches(".value-input, .memory-input")) return;
      refreshInFlight = true;
      const data = await invoke("refresh_all", [], {renderState:false, busy:manual, busyText:"Refreshing live values"});
      if (data) {
        state = data;
        lastRefreshAt = new Date();
        patchLiveValues();
        if (manual) showToast("Live values refreshed", "success");
      }
      refreshInFlight = false;
    }

    function patchLiveValues() {
      walkModify((item, path) => {
        const cell = document.querySelector(`[data-live-path="${pathKey(path)}"]`);
        if (cell) cell.textContent = item.readValue;
        const row = document.querySelector(`[data-row-path="${pathKey(path)}"]`);
        if (row) {
          row.classList.toggle("pending", !!item.pending);
          row.querySelector(".value-input")?.classList.toggle("pending", !!item.pending);
        }
      });
      const tab = state.memoryTabs[state.memoryIndex];
      if (tab) tab.values.forEach((value, index) => {
        const input = document.querySelector(`[data-memory-index="${index}"]`);
        if (input && input !== document.activeElement) input.value = toHex(value);
      });
      if ($("consoleLines")) $("consoleLines").innerHTML = renderLogs();
      if ($("inspectorBody")) $("inspectorBody").innerHTML = renderInspectorBody();
      const status = document.querySelector(".statusbar");
      if (status) status.innerHTML = renderStatusbarBody();
      const actions = document.querySelector(".view-actions");
      if (actions && activeView === "registers") actions.innerHTML = renderRegisterActions(pendingItems());
    }

    function toggleAutoRefresh(enabled) {
      if (autoTimer) clearInterval(autoTimer);
      autoTimer = enabled ? setInterval(() => refreshLive(false), refreshRate) : null;
      const status = document.querySelector(".statusbar");
      if (status) status.innerHTML = renderStatusbarBody();
    }
    function setRefreshRate(value) { refreshRate = Number(value); if (autoTimer) toggleAutoRefresh(true); }

    function startResize(event, kind) {
      event.preventDefault();
      const handle = event.currentTarget;
      handle.classList.add("active");
      const startX = event.clientX;
      const startY = event.clientY;
      const initial = layout[kind];
      const move = (next) => {
        if (kind === "explorer") layout.explorer = Math.max(230, Math.min(460, initial + next.clientX - startX));
        if (kind === "inspector") layout.inspector = Math.max(230, Math.min(430, initial - next.clientX + startX));
        if (kind === "console") layout.console = Math.max(110, Math.min(window.innerHeight * 0.45, initial - next.clientY + startY));
        applyLayout();
      };
      const end = () => {
        handle.classList.remove("active");
        document.removeEventListener("pointermove", move);
        document.removeEventListener("pointerup", end);
        savePreference("layout", JSON.stringify(layout));
      };
      document.addEventListener("pointermove", move);
      document.addEventListener("pointerup", end);
    }

    function applyLayout() {
      const root = document.documentElement.style;
      const compact = window.innerWidth <= 1120;
      root.setProperty("--explorer-width", `${compact ? Math.min(layout.explorer, 240) : layout.explorer}px`);
      root.setProperty("--inspector-width", `${compact ? Math.min(layout.inspector, 230) : layout.inspector}px`);
      root.setProperty("--console-height", `${layout.console}px`);
    }

    function captureScroll() {
      const ids = ["deviceTree", "registerScroll", "memoryScroll", "consoleLines", "inspectorBody"];
      return Object.fromEntries(ids.map((id) => [id, $(id)?.scrollTop || 0]));
    }
    function restoreScroll(snapshot) { Object.entries(snapshot || {}).forEach(([id, top]) => { if ($(id)) $(id).scrollTop = top; }); }
    function isValidNumber(value) { return /^(?:0x[0-9a-f]+|\d+)$/i.test(String(value).trim()); }
    function cleanDescription(value) { const text = String(value || "").trim(); return !text || text.toLowerCase() === "nan" ? "No description is available for this item." : text; }
    function copyText(value, message = "Address copied") { navigator.clipboard?.writeText(value).then(() => showToast(message, "success")).catch(() => showToast("Unable to access the clipboard.")); }
    function savePreference(key, value) { try { localStorage.setItem(`jgkit:${key}`, value); } catch (_) {} }
    function loadPreference(key) { try { return localStorage.getItem(`jgkit:${key}`); } catch (_) { return null; } }

    function boot() {
      try {
        const saved = JSON.parse(loadPreference("layout") || "null");
        if (saved) Object.assign(layout, saved);
      } catch (_) {}
      applyLayout();
      invoke("bootstrap", [], {busyText:"Loading target profiles"});
    }

    window.addEventListener("pywebviewready", boot);
    window.addEventListener("resize", applyLayout);
    document.addEventListener("DOMContentLoaded", () => setTimeout(() => {
      if (!state && window.pywebview && window.pywebview.api) boot();
    }, 100));
  </script>
</body>
</html>"""
