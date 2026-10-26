# Fluent Notes - single-file Windows 11 Fluent style desktop app built with pywebview
# Dependency: pip install pywebview
# Run: python example.py

import json
import os
import platform
import sys

import webview

APP_NAME = "Fluent Notes"
APP_DIR = os.path.join(os.path.expanduser("~"), ".fluent_notes")
DATA_FILE = os.path.join(APP_DIR, "data.json")
LIGHT_BG = "#F3F3F3"


class Store:
    """JSON backed persistence for notes and settings."""

    def __init__(self, path):
        self.path = path
        self.data = {"notes": [], "settings": {"theme": "light"}}
        self.load()

    def load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, ValueError):
            return
        if not isinstance(payload, dict):
            return
        notes = payload.get("notes")
        settings = payload.get("settings")
        if isinstance(notes, list):
            self.data["notes"] = [item for item in notes if isinstance(item, dict)]
        if isinstance(settings, dict):
            self.data["settings"].update(settings)

    def save(self):
        try:
            folder = os.path.dirname(self.path)
            if folder:
                os.makedirs(folder, exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as handle:
                json.dump(self.data, handle, ensure_ascii=False, indent=2)
            return True
        except OSError:
            return False


class Api:
    """Methods exposed to JavaScript through pywebview's js_api bridge."""

    def __init__(self, store):
        self.store = store
        self.window = None
        self.maximized = False

    def attach(self, window):
        self.window = window

    def minimize(self):
        if self.window is not None:
            self.window.minimize()
        return True

    def toggle_maximize(self):
        self.maximized = not self.maximized
        if self.window is not None:
            try:
                if self.maximized:
                    self.window.maximize()
                else:
                    self.window.restore()
            except Exception:
                self.maximized = not self.maximized
        return self.maximized

    def close(self):
        if self.window is not None:
            self.window.destroy()
        return True

    def load_state(self):
        return {
            "notes": self.store.data.get("notes", []),
            "settings": self.store.data.get("settings", {"theme": "light"}),
        }

    def save_notes(self, notes):
        if isinstance(notes, list):
            self.store.data["notes"] = [item for item in notes if isinstance(item, dict)]
            self.store.save()
        return True

    def save_settings(self, settings):
        if isinstance(settings, dict):
            self.store.data["settings"].update(settings)
            self.store.save()
        return True

    def get_app_info(self):
        return {
            "python": sys.version.split()[0],
            "platform": platform.system() + " " + platform.release(),
            "pywebview": getattr(webview, "__version__", "unknown"),
            "data_file": DATA_FILE,
        }


HTML = r"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="UTF-8" />
<title>Fluent Notes</title>
<style>
  :root {
    --ease: cubic-bezier(0.2, 0, 0, 1);
  }

  html[data-theme="light"] {
    --bg: #F3F3F3;
    --card: rgba(255, 255, 255, 0.72);
    --text-primary: #1A1A1A;
    --text-secondary: #616161;
    --text-tertiary: #8A8A8A;
    --stroke: rgba(0, 0, 0, 0.06);
    --stroke-strong: rgba(0, 0, 0, 0.11);
    --accent: #0067C0;
    --accent-text: #FFFFFF;
    --hover: rgba(0, 0, 0, 0.037);
    --pressed: rgba(0, 0, 0, 0.074);
    --input-bg: rgba(255, 255, 255, 0.85);
    --shadow-card: 0 1px 2px rgba(0, 0, 0, 0.04), 0 2px 8px rgba(0, 0, 0, 0.045);
    --shadow-flyout: 0 8px 28px rgba(0, 0, 0, 0.16);
  }

  html[data-theme="dark"] {
    --bg: #202020;
    --card: rgba(255, 255, 255, 0.045);
    --text-primary: #FFFFFF;
    --text-secondary: #C8C8C8;
    --text-tertiary: #9A9A9A;
    --stroke: rgba(255, 255, 255, 0.06);
    --stroke-strong: rgba(255, 255, 255, 0.11);
    --accent: #60CDFF;
    --accent-text: #00334D;
    --hover: rgba(255, 255, 255, 0.055);
    --pressed: rgba(255, 255, 255, 0.09);
    --input-bg: rgba(255, 255, 255, 0.06);
    --shadow-card: 0 1px 2px rgba(0, 0, 0, 0.24), 0 2px 8px rgba(0, 0, 0, 0.28);
    --shadow-flyout: 0 8px 28px rgba(0, 0, 0, 0.5);
  }

  * { box-sizing: border-box; }

  html, body { height: 100%; margin: 0; }

  body {
    font-family: "Segoe UI Variable Text", "Segoe UI",
                 "Microsoft YaHei UI", "Microsoft YaHei",
                 system-ui, -apple-system, sans-serif;
    font-size: 14px;
    line-height: 1.45;
    color: var(--text-primary);
    background: var(--bg);
    transition: background-color .25s ease, color .25s ease;
    user-select: none;
    -webkit-user-select: none;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }

  ::-webkit-scrollbar { width: 12px; height: 12px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb {
    background: var(--stroke-strong);
    border: 3px solid transparent;
    background-clip: content-box;
    border-radius: 6px;
  }

  .selectable { user-select: text; -webkit-user-select: text; }

  /* ---------------- Title bar ---------------- */
  .titlebar {
    flex: none;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-left: 14px;
    background: var(--bg);
    transition: background-color .25s ease;
  }

  .titlebar-left {
    display: flex;
    align-items: center;
    gap: 9px;
    pointer-events: none;
  }

  .app-glyph {
    width: 16px;
    height: 16px;
    color: var(--accent);
    display: block;
  }

  .titlebar-title {
    font-size: 12px;
    color: var(--text-secondary);
    letter-spacing: 0.2px;
  }

  .window-controls {
    display: flex;
    align-items: stretch;
  }

  .wc-btn {
    width: 46px;
    height: 40px;
    border: none;
    background: transparent;
    color: var(--text-primary);
    display: grid;
    place-items: center;
    cursor: pointer;
    transition: background-color .1s var(--ease), color .1s var(--ease);
  }

  .wc-btn:hover { background: var(--hover); }
  .wc-btn:active { background: var(--pressed); }
  .wc-btn.close:hover { background: #C42B1C; color: #FFFFFF; }
  .wc-btn.close:active { background: #B12A1C; color: #FFFFFF; }
  .wc-btn:focus-visible { outline: 1px solid var(--accent); outline-offset: -2px; }

  /* ---------------- Shell ---------------- */
  .app-body {
    flex: 1;
    display: flex;
    min-height: 0;
  }

  .sidebar {
    flex: none;
    width: 220px;
    padding: 4px 8px 8px;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .nav-item {
    position: relative;
    height: 38px;
    border-radius: 5px;
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 0 12px;
    font-size: 14px;
    color: var(--text-primary);
    cursor: pointer;
    transition: background-color .12s var(--ease), color .12s var(--ease);
  }

  .nav-item:hover { background: var(--hover); }
  .nav-item:active { background: var(--pressed); }
  .nav-item.active { background: var(--hover); font-weight: 600; }

  .nav-item.active::before {
    content: "";
    position: absolute;
    left: 2px;
    top: 50%;
    transform: translateY(-50%);
    width: 3px;
    height: 16px;
    border-radius: 2px;
    background: var(--accent);
    transition: background-color .25s ease;
  }

  .nav-icon {
    flex: none;
    color: var(--text-secondary);
    transition: color .12s var(--ease);
  }

  .nav-item.active .nav-icon { color: var(--accent); }

  .content {
    flex: 1;
    min-width: 0;
    overflow-y: auto;
    padding: 8px 28px 32px 16px;
  }

  /* ---------------- Pages ---------------- */
  .page { display: none; }

  .page.active {
    display: block;
    animation: pageIn .24s var(--ease) both;
  }

  @keyframes pageIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .page-title {
    margin: 0;
    font-size: 28px;
    font-weight: 600;
    letter-spacing: -0.2px;
  }

  .page-subtitle {
    margin: 6px 0 0;
    font-size: 13px;
    color: var(--text-secondary);
  }

  /* ---------------- Cards ---------------- */
  .card {
    background: var(--card);
    border: 1px solid var(--stroke);
    border-radius: 8px;
    padding: 16px 18px;
    box-shadow: var(--shadow-card);
    transition: background-color .25s ease, border-color .25s ease, box-shadow .25s ease;
  }

  .card-title {
    font-size: 14px;
    font-weight: 600;
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
    gap: 12px;
  }

  .stat-label {
    font-size: 12px;
    color: var(--text-secondary);
  }

  .stat-value {
    margin-top: 6px;
    font-size: 20px;
    font-weight: 600;
  }

  .stat-caption {
    margin-top: 4px;
    font-size: 12px;
    color: var(--text-tertiary);
  }

  .row {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  /* ---------------- Controls ---------------- */
  .btn {
    height: 32px;
    padding: 0 14px;
    border-radius: 4px;
    border: 1px solid var(--stroke-strong);
    background: transparent;
    color: var(--text-primary);
    font-family: inherit;
    font-size: 14px;
    cursor: pointer;
    transition: background-color .1s var(--ease), border-color .1s var(--ease), color .1s var(--ease);
  }

  .btn:hover { background: var(--hover); }
  .btn:active { background: var(--pressed); }

  .btn:focus-visible {
    outline: 1px solid var(--accent);
    outline-offset: 1px;
  }

  .btn.primary {
    background: var(--accent);
    border-color: transparent;
    color: var(--accent-text);
    font-weight: 600;
  }

  .btn.primary:hover { filter: brightness(1.08); }
  .btn.primary:active { filter: brightness(0.94); }

  .input {
    flex: 1;
    height: 32px;
    padding: 0 11px;
    border-radius: 4px;
    border: 1px solid var(--stroke-strong);
    border-bottom: 1px solid var(--text-tertiary);
    background: var(--input-bg);
    color: var(--text-primary);
    font-family: inherit;
    font-size: 14px;
    user-select: text;
    -webkit-user-select: text;
    transition: background-color .25s ease, border-color .16s var(--ease), color .25s ease;
  }

  .input::placeholder { color: var(--text-tertiary); }

  .input:focus {
    outline: none;
    border-color: var(--accent);
    border-bottom-color: var(--accent);
  }

  .icon-btn {
    flex: none;
    width: 28px;
    height: 28px;
    border: none;
    border-radius: 4px;
    background: transparent;
    color: var(--text-secondary);
    display: grid;
    place-items: center;
    cursor: pointer;
    transition: background-color .1s var(--ease), color .1s var(--ease);
  }

  .icon-btn:hover { background: var(--hover); color: var(--text-primary); }
  .icon-btn:active { background: var(--pressed); }
  .icon-btn:focus-visible { outline: 1px solid var(--accent); outline-offset: -1px; }

  /* ---------------- Notes ---------------- */
  .notes-list { margin-top: 6px; }

  .note-item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 12px 0;
    border-bottom: 1px solid var(--stroke);
    transition: border-color .25s ease;
  }

  .note-item:last-child { border-bottom: none; }

  .note-main { flex: 1; min-width: 0; }

  .note-text {
    font-size: 14px;
    word-break: break-word;
    white-space: pre-wrap;
  }

  .note-meta {
    margin-top: 4px;
    font-size: 12px;
    color: var(--text-tertiary);
  }

  .empty {
    display: none;
    padding: 20px 0 6px;
    font-size: 13px;
    color: var(--text-tertiary);
    text-align: center;
  }

  /* ---------------- Settings ---------------- */
  .setting-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
  }

  .setting-title { font-size: 14px; }

  .setting-caption {
    margin-top: 2px;
    font-size: 12px;
    color: var(--text-secondary);
  }

  .switch {
    position: relative;
    flex: none;
    width: 40px;
    height: 20px;
    display: block;
  }

  .switch input {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    margin: 0;
    opacity: 0;
    cursor: pointer;
    z-index: 2;
  }

  .switch-track {
    position: absolute;
    inset: 0;
    border-radius: 10px;
    border: 1px solid var(--text-tertiary);
    background: transparent;
    transition: background-color .16s var(--ease), border-color .16s var(--ease);
  }

  .switch-thumb {
    position: absolute;
    top: 2px;
    left: 3px;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: var(--text-secondary);
    transition: transform .16s var(--ease), background-color .16s var(--ease);
  }

  .switch input:checked + .switch-track {
    background: var(--accent);
    border-color: var(--accent);
  }

  .switch input:checked + .switch-track .switch-thumb {
    transform: translateX(18px);
    background: var(--accent-text);
  }

  .switch input:focus-visible + .switch-track {
    outline: 1px solid var(--accent);
    outline-offset: 2px;
  }

  .info-row {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 20px;
    padding: 10px 0;
    border-bottom: 1px solid var(--stroke);
    transition: border-color .25s ease;
  }

  .info-row:last-child { border-bottom: none; }

  .info-key {
    font-size: 13px;
    color: var(--text-secondary);
  }

  .info-value {
    font-family: "Cascadia Code", "Consolas", monospace;
    font-size: 12px;
    color: var(--text-primary);
    text-align: right;
    word-break: break-all;
  }
</style>
</head>
<body>

  <div class="titlebar pywebview-drag-region">
    <div class="titlebar-left">
      <svg class="app-glyph" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round">
        <path d="M5.2 2.8h6.3L15.6 7v10.2a1 1 0 0 1-1 1H5.2a1 1 0 0 1-1-1V3.8a1 1 0 0 1 1-1Z"/>
        <path d="M11.4 2.9V7.2h4.1"/>
      </svg>
      <span class="titlebar-title">Fluent Notes</span>
    </div>
    <div class="window-controls">
      <button class="wc-btn" id="btn-min" title="Minimize">
        <svg width="10" height="10" viewBox="0 0 10 10"><rect x="0" y="4.5" width="10" height="1" fill="currentColor"/></svg>
      </button>
      <button class="wc-btn" id="btn-max" title="Maximize">
        <svg width="10" height="10" viewBox="0 0 10 10"><rect x="0.5" y="0.5" width="9" height="9" fill="none" stroke="currentColor" stroke-width="1"/></svg>
      </button>
      <button class="wc-btn close" id="btn-close" title="Close">
        <svg width="10" height="10" viewBox="0 0 10 10"><path d="M1 1l8 8M9 1l-8 8" stroke="currentColor" stroke-width="1.1" fill="none"/></svg>
      </button>
    </div>
  </div>

  <div class="app-body">
    <nav class="sidebar">
      <div class="nav-item active" data-page="home">
        <svg class="nav-icon" width="18" height="18" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round">
          <path d="M3.2 9.3 10 3.4l6.8 5.9V16a1 1 0 0 1-1 1h-3.6v-4.6H7.8V17H4.2a1 1 0 0 1-1-1V9.3Z"/>
        </svg>
        <span>Home</span>
      </div>
      <div class="nav-item" data-page="notes">
        <svg class="nav-icon" width="18" height="18" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round">
          <path d="M5.2 2.8h6.3L15.6 7v10.2a1 1 0 0 1-1 1H5.2a1 1 0 0 1-1-1V3.8a1 1 0 0 1 1-1Z"/>
          <path d="M11.4 2.9V7.2h4.1M6.8 11h6M6.8 14h4" stroke-linecap="round"/>
        </svg>
        <span>Notes</span>
      </div>
      <div class="nav-item" data-page="settings">
        <svg class="nav-icon" width="18" height="18" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
          <path d="M6 3v4.8M6 12.2V17M14 3v2.8M14 10.2V17"/>
          <circle cx="6" cy="10" r="2.2"/>
          <circle cx="14" cy="8" r="2.2"/>
        </svg>
        <span>Settings</span>
      </div>
    </nav>

    <main class="content">

      <section class="page active" id="page-home">
        <h1 class="page-title">Home</h1>
        <p class="page-subtitle">A single-file pywebview app with Windows 11 Fluent styling.</p>

        <div class="grid" style="margin-top: 20px;">
          <div class="card">
            <div class="stat-label">Notes</div>
            <div class="stat-value" id="stat-notes">0</div>
            <div class="stat-caption">Stored as JSON by Python</div>
          </div>
          <div class="card">
            <div class="stat-label">Theme</div>
            <div class="stat-value" id="stat-theme">Light</div>
            <div class="stat-caption">Switch it in Settings</div>
          </div>
          <div class="card">
            <div class="stat-label">Runtime</div>
            <div class="stat-value" id="stat-runtime">Python</div>
            <div class="stat-caption" id="stat-runtime-caption">pywebview</div>
          </div>
        </div>

        <div class="card" style="margin-top: 12px;">
          <div class="card-title">Quick actions</div>
          <div class="row" style="margin-top: 12px;">
            <button class="btn primary" id="btn-sample">Add a sample note</button>
            <button class="btn" id="btn-clear">Clear all notes</button>
          </div>
        </div>
      </section>

      <section class="page" id="page-notes">
        <h1 class="page-title">Notes</h1>
        <p class="page-subtitle">Everything you type here is written to disk by the Python side.</p>

        <div class="card" style="margin-top: 20px;">
          <div class="row">
            <input class="input" id="note-input" type="text" maxlength="200"
                   placeholder="Write a note and press Enter" />
            <button class="btn primary" id="btn-add">Add</button>
          </div>
          <div class="notes-list" id="notes-list"></div>
          <div class="empty" id="notes-empty">No notes yet.</div>
        </div>
      </section>

      <section class="page" id="page-settings">
        <h1 class="page-title">Settings</h1>
        <p class="page-subtitle">Appearance and environment information.</p>

        <div class="card" style="margin-top: 20px;">
          <div class="setting-row">
            <div>
              <div class="setting-title">Dark theme</div>
              <div class="setting-caption">Switch between the light and dark Fluent palettes.</div>
            </div>
            <label class="switch">
              <input type="checkbox" id="theme-switch" />
              <span class="switch-track"><span class="switch-thumb"></span></span>
            </label>
          </div>
        </div>

        <div class="card" style="margin-top: 12px;">
          <div class="card-title">About</div>
          <div style="margin-top: 6px;">
            <div class="info-row">
              <span class="info-key">Python</span>
              <span class="info-value selectable" id="info-python">-</span>
            </div>
            <div class="info-row">
              <span class="info-key">Platform</span>
              <span class="info-value selectable" id="info-platform">-</span>
            </div>
            <div class="info-row">
              <span class="info-key">pywebview</span>
              <span class="info-value selectable" id="info-webview">-</span>
            </div>
            <div class="info-row">
              <span class="info-key">Data file</span>
              <span class="info-value selectable" id="info-datafile">-</span>
            </div>
          </div>
        </div>
      </section>

    </main>
  </div>

<script>
(function () {
  "use strict";

  var state = {
    notes: [],
    settings: { theme: "light" },
    app: {}
  };

  var initialised = false;
  var maximized = false;

  var ICON_MAX = '<svg width="10" height="10" viewBox="0 0 10 10"><rect x="0.5" y="0.5" width="9" height="9" fill="none" stroke="currentColor" stroke-width="1"/></svg>';
  var ICON_RESTORE = '<svg width="10" height="10" viewBox="0 0 10 10"><rect x="0.5" y="2.5" width="7" height="7" fill="none" stroke="currentColor" stroke-width="1"/><path d="M2.5 2.5V0.5h7v7h-2" fill="none" stroke="currentColor" stroke-width="1"/></svg>';

  function apiReady() {
    return !!(window.pywebview && window.pywebview.api);
  }

  function call(name) {
    var args = Array.prototype.slice.call(arguments, 1);
    if (!apiReady() || typeof window.pywebview.api[name] !== "function") {
      return Promise.resolve(null);
    }
    try {
      return Promise.resolve(window.pywebview.api[name].apply(window.pywebview.api, args));
    } catch (err) {
      return Promise.resolve(null);
    }
  }

  function $(id) {
    return document.getElementById(id);
  }

  function formatTime(value) {
    try {
      var date = new Date(value);
      if (isNaN(date.getTime())) { return ""; }
      return date.toLocaleString();
    } catch (err) {
      return "";
    }
  }

  function showPage(name) {
    var items = document.querySelectorAll(".nav-item");
    for (var i = 0; i < items.length; i++) {
      items[i].classList.toggle("active", items[i].getAttribute("data-page") === name);
    }
    var pages = document.querySelectorAll(".page");
    for (var j = 0; j < pages.length; j++) {
      pages[j].classList.toggle("active", pages[j].id === "page-" + name);
    }
  }

  function applyTheme(theme, persist) {
    var next = theme === "dark" ? "dark" : "light";
    state.settings.theme = next;
    document.documentElement.setAttribute("data-theme", next);
    $("theme-switch").checked = next === "dark";
    renderStats();
    if (persist !== false) {
      call("save_settings", { theme: next });
    }
  }

  function renderStats() {
    $("stat-notes").textContent = String(state.notes.length);
    $("stat-theme").textContent = state.settings.theme === "dark" ? "Dark" : "Light";
    $("stat-runtime").textContent = state.app && state.app.python
      ? "Python " + state.app.python
      : "Python";
    $("stat-runtime-caption").textContent = state.app && state.app.pywebview
      ? "pywebview " + state.app.pywebview
      : "pywebview";
  }

  function renderInfo() {
    $("info-python").textContent = state.app.python || "-";
    $("info-platform").textContent = state.app.platform || "-";
    $("info-webview").textContent = state.app.pywebview || "-";
    $("info-datafile").textContent = state.app.data_file || "-";
  }

  function renderNotes() {
    var list = $("notes-list");
    var empty = $("notes-empty");
    list.innerHTML = "";

    if (!state.notes.length) {
      empty.style.display = "block";
      return;
    }
    empty.style.display = "none";

    for (var i = 0; i < state.notes.length; i++) {
      (function (note) {
        var item = document.createElement("div");
        item.className = "note-item";

        var main = document.createElement("div");
        main.className = "note-main";

        var text = document.createElement("div");
        text.className = "note-text selectable";
        text.textContent = note.text || "";

        var meta = document.createElement("div");
        meta.className = "note-meta";
        meta.textContent = formatTime(note.created);

        main.appendChild(text);
        main.appendChild(meta);

        var remove = document.createElement("button");
        remove.className = "icon-btn";
        remove.title = "Delete note";
        remove.innerHTML = '<svg width="14" height="14" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M4 6h12M8 6V4h4v2M6.2 6l.7 10.1a1 1 0 0 0 1 .9h4.2a1 1 0 0 0 1-.9L13.8 6"/></svg>';
        remove.addEventListener("click", function () {
          deleteNote(note.id);
        });

        item.appendChild(main);
        item.appendChild(remove);
        list.appendChild(item);
      })(state.notes[i]);
    }
  }

  function persistNotes() {
    call("save_notes", state.notes);
    renderNotes();
    renderStats();
  }

  function addNote(raw) {
    var value = String(raw || "").trim();
    if (!value) { return; }
    state.notes.unshift({
      id: String(Date.now()) + "-" + Math.random().toString(36).slice(2, 7),
      text: value,
      created: new Date().toISOString()
    });
    persistNotes();
  }

  function deleteNote(id) {
    var next = [];
    for (var i = 0; i < state.notes.length; i++) {
      if (state.notes[i].id !== id) { next.push(state.notes[i]); }
    }
    state.notes = next;
    persistNotes();
  }

  function submitNote() {
    var input = $("note-input");
    addNote(input.value);
    input.value = "";
    input.focus();
  }

  function toggleMaximize() {
    call("toggle_maximize").then(function (res) {
      maximized = !!res;
      $("btn-max").innerHTML = maximized ? ICON_RESTORE : ICON_MAX;
      $("btn-max").title = maximized ? "Restore" : "Maximize";
    });
  }

  function bindEvents() {
    var navItems = document.querySelectorAll(".nav-item");
    for (var i = 0; i < navItems.length; i++) {
      (function (item) {
        item.addEventListener("click", function () {
          showPage(item.getAttribute("data-page"));
        });
      })(navItems[i]);
    }

    $("btn-min").addEventListener("click", function () { call("minimize"); });
    $("btn-max").addEventListener("click", toggleMaximize);
    $("btn-close").addEventListener("click", function () { call("close"); });

    document.querySelector(".titlebar").addEventListener("dblclick", function (event) {
      if (event.target.closest(".window-controls")) { return; }
      toggleMaximize();
    });

    $("btn-add").addEventListener("click", submitNote);
    $("note-input").addEventListener("keydown", function (event) {
      if (event.key === "Enter") { submitNote(); }
    });

    $("btn-sample").addEventListener("click", function () {
      addNote("Sample note created at " + new Date().toLocaleTimeString());
      showPage("notes");
    });

    $("btn-clear").addEventListener("click", function () {
      state.notes = [];
      persistNotes();
    });

    $("theme-switch").addEventListener("change", function (event) {
      applyTheme(event.target.checked ? "dark" : "light", true);
    });
  }

  function init() {
    if (initialised) { return; }
    initialised = true;

    call("load_state").then(function (res) {
      if (res && typeof res === "object") {
        state.notes = Array.isArray(res.notes) ? res.notes : [];
        var settings = res.settings && typeof res.settings === "object" ? res.settings : {};
        state.settings.theme = settings.theme === "dark" ? "dark" : "light";
      }
      applyTheme(state.settings.theme, false);
      renderNotes();
      renderStats();
    });

    call("get_app_info").then(function (info) {
      state.app = info && typeof info === "object" ? info : {};
      renderInfo();
      renderStats();
    });
  }

  bindEvents();
  applyTheme(document.documentElement.getAttribute("data-theme") || "light", false);
  renderNotes();
  renderStats();

  if (apiReady()) {
    init();
  }
  window.addEventListener("pywebviewready", init);
})();
</script>
</body>
</html>
"""


def main():
    store = Store(DATA_FILE)
    api = Api(store)
    window = webview.create_window(
        APP_NAME,
        html=HTML,
        js_api=api,
        width=1080,
        height=720,
        min_size=(900, 600),
        background_color=LIGHT_BG,
        frameless=True,
        easy_drag=False,
        resizable=True,
        text_select=True,
    )
    api.attach(window)
    webview.start()


if __name__ == "__main__":
    main()