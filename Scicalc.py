# 科学计算器（Windows 11 Fluent Design / pywebview 单文件桌面应用）
# 依赖安装：pip install pywebview
# 运行命令：python 科学计算器.py

import tkinter as tk

import webview
import winreg


class Api:
    # 读取系统浅色/深色主题
    def system_theme(self):
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return "light" if value == 1 else "dark"
        except OSError:
            return "light"

    # 剪贴板兜底（WebView2 剪贴板接口不可用时使用）
    def copy_text(self, text):
        try:
            root = tk.Tk()
            root.withdraw()
            root.clipboard_clear()
            root.clipboard_append(text)
            root.update()
            root.destroy()
            return True
        except Exception:
            return False


HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>科学计算器</title>
<style>
:root{
  --bg:#F3F3F3;
  --card:rgba(255,255,255,.72);
  --text:#1A1A1A;
  --text-2:#616161;
  --text-3:#8A8A8A;
  --stroke:rgba(0,0,0,.06);
  --stroke-strong:rgba(0,0,0,.11);
  --accent:#0067C0;
  --on-accent:#FFFFFF;
  --hover:rgba(0,0,0,.037);
  --pressed:rgba(0,0,0,.074);
  --key-bg:rgba(255,255,255,.78);
  --key-fn:rgba(255,255,255,.5);
  --accent-soft:rgba(0,103,192,.12);
  --danger:#C42B1C;
  --card-shadow:0 1px 2px rgba(0,0,0,.04),0 2px 8px rgba(0,0,0,.045);
  --overlay-shadow:0 8px 28px rgba(0,0,0,.16);
}
html[data-theme="dark"]{
  --bg:#202020;
  --card:rgba(255,255,255,.045);
  --text:#FFFFFF;
  --text-2:#C8C8C8;
  --text-3:#9A9A9A;
  --stroke:rgba(255,255,255,.06);
  --stroke-strong:rgba(255,255,255,.11);
  --accent:#60CDFF;
  --on-accent:#00334D;
  --hover:rgba(255,255,255,.055);
  --pressed:rgba(255,255,255,.09);
  --key-bg:rgba(255,255,255,.05);
  --key-fn:rgba(255,255,255,.033);
  --accent-soft:rgba(96,205,255,.16);
  --danger:#FF99A4;
  --card-shadow:0 1px 2px rgba(0,0,0,.22),0 2px 8px rgba(0,0,0,.26);
  --overlay-shadow:0 8px 28px rgba(0,0,0,.55);
}
*{box-sizing:border-box;margin:0;padding:0;}
html,body{height:100%;}
body{
  background:var(--bg);
  color:var(--text);
  font-family:"Segoe UI Variable Text","Segoe UI","Microsoft YaHei UI","Microsoft YaHei",system-ui,-apple-system,sans-serif;
  font-size:14px;
  overflow:hidden;
  user-select:none;
  transition:background-color .25s ease,color .25s ease;
}
button{font-family:inherit;}
.app{
  height:100vh;
  display:flex;
  flex-direction:column;
  padding:6px 16px 14px;
  max-width:1000px;
  margin:0 auto;
}
/* 顶部标题栏 */
.titlebar{
  height:40px;
  display:flex;
  align-items:center;
  justify-content:space-between;
  flex:none;
}
.app-title{font-size:12px;color:var(--text-3);font-weight:600;letter-spacing:.4px;}
.title-actions{display:flex;align-items:center;gap:6px;}
.mode-badge{
  font-size:11px;
  font-weight:600;
  color:var(--text-2);
  border:1px solid var(--stroke-strong);
  border-radius:10px;
  padding:2px 9px;
  margin-right:2px;
  transition:all .25s ease;
}
.icon-btn{
  width:32px;height:32px;
  border:1px solid transparent;
  border-radius:4px;
  background:transparent;
  color:var(--text-2);
  display:flex;align-items:center;justify-content:center;
  cursor:pointer;
  transition:background-color .12s cubic-bezier(.2,0,0,1);
}
.icon-btn:hover{background:var(--hover);}
.icon-btn:active{background:var(--pressed);}
.icon-btn:focus-visible{outline:1px solid var(--stroke-strong);outline-offset:1px;}
.icon-btn svg{width:16px;height:16px;}
.icon-btn .icon-sun{display:none;}
html[data-theme="dark"] .icon-btn .icon-sun{display:block;}
html[data-theme="dark"] .icon-btn .icon-moon{display:none;}
/* 主区域 */
.content{position:relative;flex:1;display:flex;flex-direction:column;min-height:0;
  animation:fadeUp .24s cubic-bezier(.2,0,0,1);}
@keyframes fadeUp{from{opacity:0;transform:translateY(8px);}to{opacity:1;transform:none;}}
/* 显示屏 */
.display{
  background:var(--card);
  border:1px solid var(--stroke);
  border-radius:8px;
  box-shadow:var(--card-shadow);
  padding:12px 18px;
  display:flex;
  flex-direction:column;
  align-items:flex-end;
  justify-content:center;
  gap:2px;
  min-height:96px;
  margin-bottom:10px;
  transition:background-color .25s ease,border-color .25s ease;
}
.expr{
  width:100%;
  font-family:"Cascadia Code","Consolas",monospace;
  font-size:20px;
  color:var(--text-2);
  text-align:right;
  white-space:nowrap;
  overflow-x:auto;
  overflow-y:hidden;
  scrollbar-width:none;
  user-select:text;
  min-height:26px;
  direction:rtl;
}
.expr::-webkit-scrollbar{display:none;}
.result-row{display:flex;align-items:center;gap:6px;max-width:100%;min-height:38px;}
.result{
  font-family:"Cascadia Code","Consolas",monospace;
  font-size:28px;
  font-weight:600;
  text-align:right;
  color:var(--text-3);
  white-space:nowrap;
  overflow:hidden;
  user-select:text;
}
.result.final{color:var(--text);}
.result.error{color:var(--danger);font-size:20px;font-family:inherit;}
.copy-btn{
  width:28px;height:28px;
  border:none;border-radius:4px;
  background:transparent;color:var(--text-3);
  display:flex;align-items:center;justify-content:center;
  cursor:pointer;opacity:0;
  transition:opacity .12s ease,background-color .12s ease;
  flex:none;
}
.result-row:hover .copy-btn{opacity:1;}
.copy-btn:hover{background:var(--hover);color:var(--text-2);}
.copy-btn svg{width:14px;height:14px;}
/* 键盘区 */
.pad{
  flex:1;
  display:grid;
  grid-template-columns:3fr 2fr;
  gap:10px;
  min-height:0;
}
.sci-keys,.std-keys{display:grid;gap:6px;}
.sci-keys{grid-template-columns:repeat(6,1fr);grid-template-rows:repeat(5,1fr);}
.std-keys{grid-template-columns:repeat(4,1fr);grid-template-rows:repeat(5,1fr);}
.key{
  height:100%;
  min-height:0;
  border:1px solid var(--stroke);
  border-radius:4px;
  background:var(--key-bg);
  color:var(--text);
  font-size:15px;
  cursor:pointer;
  transition:background-color .1s cubic-bezier(.2,0,0,1),color .1s ease,border-color .25s ease;
}
.sci-keys .key{
  background:var(--key-fn);
  color:var(--text-2);
  font-size:13.5px;
}
.key:hover{background:var(--hover);color:var(--text);}
.key:active{background:var(--pressed);}
.key:focus-visible{outline:1px solid var(--stroke-strong);outline-offset:1px;}
.key.op{color:var(--accent);}
.key.danger{color:var(--danger);}
.key.eq{
  background:var(--accent);
  color:var(--on-accent);
  border-color:transparent;
  font-size:17px;
}
.key.eq:hover{filter:brightness(1.08);background:var(--accent);color:var(--on-accent);}
.key.eq:active{filter:brightness(.95);}
.key.toggle.active{
  background:var(--accent-soft);
  color:var(--accent);
  border-color:var(--accent);
}
.key:disabled{opacity:.38;pointer-events:none;}
.key.wide-letter{font-size:12.5px;letter-spacing:.2px;}
/* 历史记录抽屉 */
.history{
  position:absolute;
  top:0;right:0;bottom:0;
  width:300px;
  background:var(--bg);
  border-left:1px solid var(--stroke-strong);
  box-shadow:var(--overlay-shadow);
  border-radius:8px 0 0 8px;
  display:flex;
  flex-direction:column;
  transform:translateX(105%);
  transition:transform .25s cubic-bezier(.2,0,0,1);
  z-index:20;
}
.history.open{transform:translateX(0);}
.history-head{
  display:flex;align-items:center;justify-content:space-between;
  padding:14px 16px 10px;flex:none;
}
.history-head span{font-size:15px;font-weight:600;}
.history-clear{
  border:none;background:transparent;color:var(--danger);
  font-size:12px;cursor:pointer;border-radius:4px;padding:4px 8px;
  transition:background-color .12s ease;
}
.history-clear:hover{background:var(--hover);}
.history-list{flex:1;overflow-y:auto;padding:0 10px 12px;}
.h-item{
  width:100%;text-align:right;
  background:var(--card);
  border:1px solid var(--stroke);
  border-radius:6px;
  padding:8px 12px;margin-bottom:6px;
  cursor:pointer;
  transition:background-color .12s ease;
}
.h-item:hover{background:var(--hover);}
.h-expr{
  font-family:"Cascadia Code","Consolas",monospace;
  font-size:12px;color:var(--text-3);
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
  direction:rtl;
}
.h-result{
  font-family:"Cascadia Code","Consolas",monospace;
  font-size:16px;font-weight:600;color:var(--text);
  margin-top:2px;
}
.history-empty{
  display:flex;align-items:center;justify-content:center;
  color:var(--text-3);font-size:13px;
  position:absolute;top:50%;left:0;right:0;text-align:center;
  pointer-events:none;
}
/* 轻提示 */
.toast{
  position:absolute;
  bottom:18px;left:50%;
  transform:translateX(-50%) translateY(10px);
  background:var(--text);
  color:var(--bg);
  font-size:12px;
  padding:7px 16px;
  border-radius:6px;
  box-shadow:var(--overlay-shadow);
  opacity:0;pointer-events:none;
  transition:opacity .16s ease,transform .16s ease;
  z-index:30;
}
.toast.show{opacity:1;transform:translateX(-50%) translateY(0);}
</style>
</head>
<body>
<div class="app">
  <header class="titlebar">
    <div class="app-title">科学计算器</div>
    <div class="title-actions">
      <span class="mode-badge" id="modeBadge">DEG</span>
      <button class="icon-btn" id="historyBtn" title="历史记录" aria-label="历史记录">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>
      </button>
      <button class="icon-btn" id="themeBtn" title="切换主题" aria-label="切换主题">
        <svg class="icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"><path d="M20 14.5A8 8 0 1 1 9.5 4 6.5 6.5 0 0 0 20 14.5z"/></svg>
        <svg class="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
      </button>
    </div>
  </header>

  <main class="content">
    <section class="display">
      <div class="expr" id="expr"></div>
      <div class="result-row">
        <div class="result" id="result"></div>
        <button class="copy-btn" id="copyBtn" title="复制结果" aria-label="复制结果">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h10"/></svg>
        </button>
      </div>
    </section>

    <section class="pad">
      <div class="sci-keys">
        <button class="key toggle" id="secondKey" data-action="second">2nd</button>
        <button class="key toggle active" id="modeKey" data-action="mode">DEG</button>
        <button class="key" data-kind="open" data-ins="(">(</button>
        <button class="key" data-kind="close" data-ins=")">)</button>
        <button class="key wide-letter" id="mcKey" data-action="mc">MC</button>
        <button class="key wide-letter" id="mrKey" data-action="mr">MR</button>

        <button class="key" data-alt="1" data-label="sin" data-label2="sin⁻¹" data-kind="func" data-ins="sin(" data-ins2="asin(">sin</button>
        <button class="key" data-alt="1" data-label="cos" data-label2="cos⁻¹" data-kind="func" data-ins="cos(" data-ins2="acos(">cos</button>
        <button class="key" data-alt="1" data-label="tan" data-label2="tan⁻¹" data-kind="func" data-ins="tan(" data-ins2="atan(">tan</button>
        <button class="key" data-kind="const" data-ins="π">π</button>
        <button class="key" data-kind="const" data-ins="e">e</button>
        <button class="key" data-kind="post" data-ins="!">x!</button>

        <button class="key" data-alt="1" data-label="x²" data-label2="x³" data-kind="post" data-ins="^2" data-ins2="^3">x²</button>
        <button class="key" data-alt="1" data-label="√" data-label2="∛" data-kind="func" data-ins="sqrt(" data-ins2="cbrt(">√</button>
        <button class="key" data-kind="post" data-ins="^(−1)">1/x</button>
        <button class="key" data-alt="1" data-label="ln" data-label2="eˣ" data-kind="func" data-ins="ln(" data-ins2="exp(">ln</button>
        <button class="key" data-alt="1" data-label="log" data-label2="10ˣ" data-kind="func" data-ins="log(" data-ins2="pow10(">log</button>
        <button class="key op" data-kind="op" data-ins="^">xʸ</button>

        <button class="key" data-kind="func" data-ins="abs(">|x|</button>
        <button class="key op wide-letter" data-kind="op" data-ins="mod">mod</button>
        <button class="key wide-letter" data-kind="ee" data-ins="E">EE</button>
        <button class="key wide-letter" data-action="rand">Rand</button>
        <button class="key wide-letter" data-action="mplus">M+</button>
        <button class="key wide-letter" data-action="mminus">M−</button>

        <button class="key wide-letter" data-kind="func" data-ins="floor(">floor</button>
        <button class="key wide-letter" data-kind="func" data-ins="ceil(">ceil</button>
        <button class="key" data-kind="func" data-ins="pow2(">2ˣ</button>
        <button class="key wide-letter" data-kind="func" data-ins="log2(">log₂</button>
        <button class="key wide-letter" data-action="ms">MS</button>
        <button class="key wide-letter" data-kind="const" data-ins="Ans">Ans</button>
      </div>

      <div class="std-keys">
        <button class="key danger" data-action="ac">AC</button>
        <button class="key" data-action="back">⌫</button>
        <button class="key op" data-kind="post" data-ins="%">%</button>
        <button class="key op" data-kind="op" data-ins="÷">÷</button>

        <button class="key" data-kind="num" data-ins="7">7</button>
        <button class="key" data-kind="num" data-ins="8">8</button>
        <button class="key" data-kind="num" data-ins="9">9</button>
        <button class="key op" data-kind="op" data-ins="×">×</button>

        <button class="key" data-kind="num" data-ins="4">4</button>
        <button class="key" data-kind="num" data-ins="5">5</button>
        <button class="key" data-kind="num" data-ins="6">6</button>
        <button class="key op" data-kind="op" data-ins="−">−</button>

        <button class="key" data-kind="num" data-ins="1">1</button>
        <button class="key" data-kind="num" data-ins="2">2</button>
        <button class="key" data-kind="num" data-ins="3">3</button>
        <button class="key op" data-kind="op" data-ins="+">+</button>

        <button class="key" data-action="sign">±</button>
        <button class="key" data-kind="num" data-ins="0">0</button>
        <button class="key" data-kind="dot" data-ins=".">.</button>
        <button class="key eq" data-action="eq">=</button>
      </div>
    </section>

    <aside class="history" id="historyPanel">
      <div class="history-head">
        <span>历史记录</span>
        <button class="history-clear" id="clearHistory">清空</button>
      </div>
      <div class="history-list" id="historyList"></div>
      <div class="history-empty" id="historyEmpty">暂无历史记录</div>
    </aside>

    <div class="toast" id="toast"></div>
  </main>
</div>

<script>
(function(){
  "use strict";
  var $ = function(id){ return document.getElementById(id); };
  var exprEl = $("expr"), resultEl = $("result"), toastEl = $("toast");
  var modeKey = $("modeKey"), modeBadge = $("modeBadge");
  var secondKey = $("secondKey"), mcKey = $("mcKey"), mrKey = $("mrKey");
  var historyPanel = $("historyPanel"), historyList = $("historyList"), historyEmpty = $("historyEmpty");

  var expr = "";
  var justEvaluated = false;
  var deg = true;
  var second = false;
  var ans = 0;
  var mem = 0;
  var memHas = false;
  var history = [];
  var MAX_EXPR = 150;

  var store = {
    get: function(k, d){
      try { var v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); }
      catch(e){ return d; }
    },
    set: function(k, v){
      try { localStorage.setItem(k, JSON.stringify(v)); } catch(e){}
    }
  };

  history = store.get("scicalc_history", []);
  mem = store.get("scicalc_mem", 0);
  memHas = store.get("scicalc_mem_has", false);

  /* ---------------- 表达式求值引擎 ---------------- */

  var D2R = Math.PI / 180;
  var R2D = 180 / Math.PI;

  function clampUnit(x){
    if (x > 1 && x <= 1 + 1e-12) return 1;
    if (x < -1 && x >= -1 - 1e-12) return -1;
    return x;
  }

  var FUNCS = {
    sin: function(x){ return Math.sin(deg ? x * D2R : x); },
    cos: function(x){ return Math.cos(deg ? x * D2R : x); },
    tan: function(x){
      if (deg && Math.abs((x % 180) - 90) < 1e-9) return NaN;
      if (deg && Math.abs((x % 180) + 90) < 1e-9) return NaN;
      return Math.tan(deg ? x * D2R : x);
    },
    asin: function(x){ x = clampUnit(x); var r = Math.asin(x); return isNaN(r) ? NaN : (deg ? r * R2D : r); },
    acos: function(x){ x = clampUnit(x); var r = Math.acos(x); return isNaN(r) ? NaN : (deg ? r * R2D : r); },
    atan: function(x){ var r = Math.atan(x); return deg ? r * R2D : r; },
    sqrt: Math.sqrt,
    cbrt: Math.cbrt,
    ln: Math.log,
    log: Math.log10,
    exp: Math.exp,
    pow10: function(x){ return Math.pow(10, x); },
    log2: Math.log2,
    pow2: function(x){ return Math.pow(2, x); },
    abs: Math.abs,
    floor: Math.floor,
    ceil: Math.ceil
  };

  function factorial(n){
    if (n < 0 || !Number.isInteger(n)) throw new Error("fact");
    if (n > 170) return Infinity;
    var r = 1;
    for (var i = 2; i <= n; i++) r *= i;
    return r;
  }

  function smartPow(a, b){
    var r = Math.pow(a, b);
    if (!isNaN(r) && isFinite(r)) return r;
    if (a < 0) {
      var p = Math.pow(-a, b);
      if (isFinite(p)) {
        var inv = 1 / b;
        var n = Math.round(inv);
        if (Math.abs(inv - n) < 1e-9 && n % 2 === 1) return -p;
      }
    }
    return r;
  }

  function isDigit(c){ return c >= "0" && c <= "9"; }
  function isAlpha(c){ return c >= "a" && c <= "z" || c >= "A" && c <= "Z"; }

  /* 按长度从长到短匹配函数名，避免 log2 被拆成 log + 2 */
  var FUNC_NAMES = Object.keys(FUNCS).sort(function(a, b){ return b.length - a.length; });

  function matchFunc(s, i){
    for (var n = 0; n < FUNC_NAMES.length; n++) {
      var name = FUNC_NAMES[n];
      if (s.substr(i, name.length).toLowerCase() === name) return name;
    }
    return null;
  }

  function valueContext(toks){
    var t = toks[toks.length - 1];
    return !!t && (t.type === "num" || t.type === "const" || t.type === ")" || t.postfix === true);
  }

  function tokenize(s){
    var toks = [], i = 0;
    while (i < s.length) {
      var c = s.charAt(i);
      if (c === " ") { i++; continue; }
      if (isDigit(c) || (c === "." && isDigit(s.charAt(i + 1)))) {
        var j = i + 1;
        while (j < s.length && (isDigit(s.charAt(j)) || s.charAt(j) === ".")) j++;
        if (s.charAt(j) === "E") {
          var k = j + 1;
          if (s.charAt(k) === "+" || s.charAt(k) === "−" || s.charAt(k) === "-") k++;
          if (isDigit(s.charAt(k))) {
            while (k < s.length && isDigit(s.charAt(k))) k++;
            j = k;
          }
        }
        var raw = s.slice(i, j).replace(/−/g, "-");
        var val = Number(raw);
        if (isNaN(val)) throw new Error("number");
        toks.push({ type: "num", value: val });
        i = j;
        continue;
      }
      if (c === "π") { toks.push({ type: "const", name: "pi" }); i++; continue; }
      if (isAlpha(c)) {
        var fname = matchFunc(s, i);
        if (fname) {
          toks.push({ type: "func", name: fname });
          i += fname.length;
          continue;
        }
        var p = i + 1;
        while (p < s.length && isAlpha(s.charAt(p))) p++;
        var word = s.slice(i, p).toLowerCase();
        if (word === "mod") toks.push({ type: "op", name: "mod" });
        else if (word === "pi") toks.push({ type: "const", name: "pi" });
        else if (word === "e" || word === "ans") toks.push({ type: "const", name: word });
        else throw new Error("name");
        i = p;
        continue;
      }
      switch (c) {
        case "+":
          if (!valueContext(toks)) { i++; continue; }
          toks.push({ type: "op", name: "+" });
          break;
        case "-":
        case "−":
          toks.push({ type: "op", name: valueContext(toks) ? "-" : "u-" });
          break;
        case "×":
        case "*":
          toks.push({ type: "op", name: "*" });
          break;
        case "÷":
        case "/":
          toks.push({ type: "op", name: "/" });
          break;
        case "^":
          toks.push({ type: "op", name: "^" });
          break;
        case "!":
          toks.push({ type: "op", name: "!", postfix: true });
          break;
        case "%":
          toks.push({ type: "op", name: "%", postfix: true });
          break;
        case "(":
          toks.push({ type: "(" });
          break;
        case ")":
          toks.push({ type: ")" });
          break;
        default:
          throw new Error("char");
      }
      i++;
    }
    return toks;
  }

  function needsMul(a, b){
    var left = a.type === "num" || a.type === "const" || a.type === ")" || a.postfix === true;
    var right = b.type === "num" || b.type === "const" || b.type === "func" || b.type === "(";
    return left && right;
  }

  var PREC = { "!": 7, "%": 7, "u-": 5, "^": 4, "*": 3, "/": 3, "mod": 3, "+": 2, "-": 2 };
  var RIGHT = { "u-": true, "^": true };

  function toRPN(toks){
    var out = [], stack = [];
    for (var i = 0; i < toks.length; i++) {
      var tk = toks[i];
      if (tk.type === "num" || tk.type === "const") {
        out.push(tk);
      } else if (tk.type === "func") {
        stack.push(tk);
      } else if (tk.postfix === true) {
        out.push(tk);
      } else if (tk.type === "op") {
        while (stack.length) {
          var top = stack[stack.length - 1];
          if (top.type === "(") break;
          if (top.type === "func") { out.push(stack.pop()); continue; }
          var tp = top.name;
          if (PREC[tp] > PREC[tk.name] || (PREC[tp] === PREC[tk.name] && !RIGHT[tk.name])) {
            out.push(stack.pop());
          } else break;
        }
        stack.push(tk);
      } else if (tk.type === "(") {
        stack.push(tk);
      } else if (tk.type === ")") {
        var found = false;
        while (stack.length) {
          if (stack[stack.length - 1].type === "(") { found = true; break; }
          out.push(stack.pop());
        }
        if (!found) throw new Error("paren");
        stack.pop();
        if (stack.length && stack[stack.length - 1].type === "func") out.push(stack.pop());
      }
    }
    while (stack.length) {
      var t = stack.pop();
      if (t.type === "(") throw new Error("unclosed");
      out.push(t);
    }
    return out;
  }

  function evalRPN(rpn){
    var st = [];
    for (var i = 0; i < rpn.length; i++) {
      var t = rpn[i];
      if (t.type === "num") {
        st.push(t.value);
      } else if (t.type === "const") {
        if (t.name === "pi") st.push(Math.PI);
        else if (t.name === "e") st.push(Math.E);
        else st.push(ans);
      } else if (t.type === "func") {
        var a = st.pop();
        if (a === undefined) throw new Error("arg");
        var r = FUNCS[t.name](a);
        if (typeof r !== "number" || isNaN(r)) throw new Error("domain");
        st.push(r);
      } else if (t.postfix === true) {
        var v = st.pop();
        if (v === undefined) throw new Error("arg");
        if (t.name === "!") st.push(factorial(v));
        else st.push(v / 100);
      } else if (t.name === "u-") {
        var n = st.pop();
        if (n === undefined) throw new Error("operand");
        st.push(-n);
      } else {
        var b = st.pop(), x = st.pop();
        if (b === undefined || x === undefined) throw new Error("operand");
        switch (t.name) {
          case "+": st.push(x + b); break;
          case "-": st.push(x - b); break;
          case "*": st.push(x * b); break;
          case "/":
            if (b === 0) throw new Error("zero");
            st.push(x / b);
            break;
          case "mod":
            if (b === 0) throw new Error("zero");
            st.push(x % b);
            break;
          case "^": st.push(smartPow(x, b)); break;
        }
      }
    }
    if (st.length !== 1) throw new Error("expr");
    return st[0];
  }

  function parseEval(s){
    var toks = tokenize(s);
    if (!toks.length) throw new Error("empty");
    var filled = [];
    for (var i = 0; i < toks.length; i++) {
      if (i > 0 && needsMul(toks[i - 1], toks[i])) filled.push({ type: "op", name: "*" });
      filled.push(toks[i]);
    }
    return evalRPN(toRPN(filled));
  }

  function prepareExpression(s){
    s = s.trim();
    var openCount = (s.match(/\(/g) || []).length - (s.match(/\)/g) || []).length;
    if (openCount > 0) s += new Array(openCount + 1).join(")");
    s = s.replace(/\s+$/, "");
    while (/[×÷+−^]$/.test(s) || /mod$/.test(s)) {
      if (/mod$/.test(s)) s = s.slice(0, -3);
      else s = s.slice(0, -1);
      s = s.trim();
    }
    return s;
  }

  function formatNumber(x){
    if (isNaN(x)) return "错误";
    if (!isFinite(x)) return "溢出";
    if (Math.abs(x) < 1e-14) x = 0;
    var r = parseFloat(x.toPrecision(13));
    var a = Math.abs(r);
    if (a !== 0 && (a >= 1e15 || a < 1e-10)) {
      return r.toExponential(8).replace(/(\.\d*?)0+e/, "$1e").replace(/\.e/, "e");
    }
    return String(r);
  }

  function numberToExpression(x){
    return formatNumber(x).replace(/-/g, "−").replace(/e/g, "E");
  }

  /* ---------------- 输入处理 ---------------- */

  function beginEdit(useResult){
    if (justEvaluated) {
      justEvaluated = false;
      resultEl.className = "result";
      resultEl.textContent = "";
      expr = useResult ? numberToExpression(ans) : "";
    }
  }

  function inputNumber(d){
    beginEdit(false);
    if (expr.length >= MAX_EXPR) return;
    expr += d;
    render();
  }

  function inputDot(){
    beginEdit(false);
    var tail = (expr.match(/\d*\.?\d*(?:E[+\-−]?\d+)?$/) || [""])[0];
    if (tail.indexOf(".") !== -1) return;
    if (!/\d$/.test(expr)) expr += "0";
    expr += ".";
    render();
  }

  function inputEE(){
    beginEdit(true);
    if (!/\d$/.test(expr)) return;
    var seg = (expr.match(/\d+(?:\.\d+)?(?:E[+\-−]?\d+)?$/) || [""])[0];
    if (seg.indexOf("E") !== -1) return;
    expr += "E";
    render();
  }

  function inputOp(op){
    beginEdit(true);
    expr = expr.replace(/\s+$/, "");
    do {
      if (/mod$/i.test(expr)) { expr = expr.slice(0, -3); continue; }
      if (/[×÷+−^]$/.test(expr)) { expr = expr.slice(0, -1); continue; }
      break;
    } while (true);
    if ((!expr || /\($/.test(expr)) && op !== "−") { render(); return; }
    expr += op;
    render();
  }

  function inputPost(p){
    beginEdit(true);
    if (expr.length >= MAX_EXPR) return;
    if (!expr || /[×÷+−^(]$/.test(expr)) { render(); return; }
    expr += p;
    render();
  }

  function inputFunc(f){
    if (justEvaluated) {
      expr = f + numberToExpression(ans) + ")";
      justEvaluated = false;
      resultEl.className = "result";
      resultEl.textContent = "";
    } else {
      if (expr.length >= MAX_EXPR) return;
      expr += f;
    }
    render();
  }

  function inputConst(c){
    beginEdit(false);
    if (expr.length >= MAX_EXPR) return;
    expr += c;
    render();
  }

  function inputOpen(){
    beginEdit(false);
    if (expr.length >= MAX_EXPR) return;
    expr += "(";
    render();
  }

  function inputClose(){
    beginEdit(true);
    var opens = (expr.match(/\(/g) || []).length - (expr.match(/\)/g) || []).length;
    if (opens <= 0) return;
    expr += ")";
    render();
  }

  function insertRandom(){
    beginEdit(false);
    expr += String(Math.random());
    render();
  }

  function toggleSign(){
    if (justEvaluated) {
      var t = numberToExpression(ans);
      expr = t.charAt(0) === "−" ? t.slice(1) : "−" + t;
      justEvaluated = false;
      resultEl.className = "result";
      resultEl.textContent = "";
      render();
      return;
    }
    var m = expr.match(/(\d+(?:\.\d*)?(?:E[+\-−]?\d+)?)$/);
    if (!m) return;
    var idx = expr.length - m[0].length;
    if (idx > 0 && expr.charAt(idx - 1) === "−") {
      var before = expr.charAt(idx - 2);
      if (before === "" || "×÷+−^(".indexOf(before) !== -1) {
        expr = expr.slice(0, idx - 1) + expr.slice(idx);
        render();
        return;
      }
    }
    expr = expr.slice(0, idx) + "−" + expr.slice(idx);
    render();
  }

  function backspace(){
    if (justEvaluated) {
      justEvaluated = false;
      resultEl.className = "result";
      resultEl.textContent = "";
      expr = "";
      render();
      return;
    }
    var tail = expr.match(/(?:[a-zA-Z]+\(|Ans|mod|π)$/);
    expr = tail ? expr.slice(0, -tail[0].length) : expr.slice(0, -1);
    render();
  }

  function clearAll(){
    expr = "";
    justEvaluated = false;
    resultEl.className = "result";
    resultEl.textContent = "";
    render();
  }

  /* ---------------- 求值与历史 ---------------- */

  function showError(msg){
    resultEl.className = "result error";
    resultEl.textContent = msg;
  }

  function errorText(err){
    var m = err && err.message;
    if (m === "zero") return "除数不能为零";
    if (m === "domain") return "超出定义域";
    if (m === "fact") return "阶乘需非负整数";
    return "表达式错误";
  }

  function evaluate(){
    if (!expr.trim()) return;
    var s = prepareExpression(expr);
    var v;
    try { v = parseEval(s); }
    catch (e) { showError(errorText(e)); return; }
    if (typeof v !== "number" || isNaN(v)) { showError("数学错误"); return; }
    if (!isFinite(v)) { showError("结果溢出"); return; }
    var out = formatNumber(v);
    ans = v;
    pushHistory(expr, out);
    resultEl.className = "result final";
    resultEl.textContent = out;
    justEvaluated = true;
  }

  function pushHistory(e, r){
    if (history.length && history[0].expr === e && history[0].result === r) return;
    history.unshift({ expr: e, result: r });
    if (history.length > 50) history.length = 50;
    store.set("scicalc_history", history);
    renderHistory();
  }

  function renderHistory(){
    historyList.innerHTML = "";
    historyEmpty.style.display = history.length ? "none" : "block";
    history.forEach(function(item){
      var div = document.createElement("div");
      div.className = "h-item";
      var eDiv = document.createElement("div");
      eDiv.className = "h-expr";
      eDiv.textContent = item.expr;
      var rDiv = document.createElement("div");
      rDiv.className = "h-result";
      rDiv.textContent = "= " + item.result;
      div.appendChild(eDiv);
      div.appendChild(rDiv);
      div.addEventListener("click", function(){
        expr = item.expr;
        justEvaluated = true;
        ans = Number(item.result.replace(/−/g, "-")) || ans;
        resultEl.className = "result final";
        resultEl.textContent = item.result;
        render();
        closeHistory();
      });
      historyList.appendChild(div);
    });
  }

  /* ---------------- 内存功能 ---------------- */

  function currentValueForMemory(){
    if (justEvaluated) return ans;
    try {
      var v = parseEval(prepareExpression(expr));
      if (typeof v === "number" && isFinite(v)) return v;
    } catch (e) {}
    return null;
  }

  function updateMemKeys(){
    mcKey.disabled = !memHas;
    mrKey.disabled = !memHas;
  }

  function memoryRecall(){
    if (!memHas) return;
    beginEdit(false);
    expr += numberToExpression(mem);
    render();
  }

  function memoryStore(sign){
    var v = currentValueForMemory();
    if (v === null) { showError("无可存储的值"); return; }
    if (sign === "set") mem = v;
    else if (sign === "add") mem = (memHas ? mem : 0) + v;
    else if (sign === "sub") mem = (memHas ? mem : 0) - v;
    memHas = true;
    store.set("scicalc_mem", mem);
    store.set("scicalc_mem_has", true);
    updateMemKeys();
    toast("已存入内存");
  }

  /* ---------------- 界面渲染 ---------------- */

  function render(){
    exprEl.textContent = expr;
    exprEl.scrollLeft = exprEl.scrollWidth;
    updateMemKeys();
    if (!justEvaluated) updatePreview();
  }

  function updatePreview(){
    if (!expr.trim()) { resultEl.className = "result"; resultEl.textContent = ""; return; }
    var v;
    try { v = parseEval(prepareExpression(expr)); }
    catch (e) { resultEl.textContent = ""; return; }
    if (typeof v !== "number" || isNaN(v) || !isFinite(v)) { resultEl.textContent = ""; return; }
    resultEl.className = "result";
    resultEl.textContent = "= " + formatNumber(v);
  }

  function setSecond(v){
    second = v;
    secondKey.classList.toggle("active", v);
    var altKeys = document.querySelectorAll("[data-ins2]");
    altKeys.forEach(function(b){
      b.textContent = v ? b.dataset.label2 : b.dataset.label;
    });
  }

  function toggleMode(){
    deg = !deg;
    var label = deg ? "DEG" : "RAD";
    modeKey.textContent = label;
    modeBadge.textContent = label;
    modeKey.classList.toggle("active", deg);
    if (!justEvaluated) updatePreview();
  }

  var toastTimer = null;
  function toast(msg){
    toastEl.textContent = msg;
    toastEl.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function(){ toastEl.classList.remove("show"); }, 1200);
  }

  function copyResult(){
    var text = resultEl.textContent;
    if (!text) return;
    if (text.charAt(0) === "=" && text.charAt(1) === " ") text = text.slice(2);
    var done = function(){ toast("已复制"); };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done).catch(function(){ fallbackCopy(text, done); });
    } else {
      fallbackCopy(text, done);
    }
  }

  function fallbackCopy(text, done){
    if (window.pywebview && window.pywebview.api && typeof window.pywebview.api.copy_text === "function") {
      window.pywebview.api.copy_text(text).then(function(ok){ if (ok) done(); });
    }
  }

  /* ---------------- 历史面板开关 ---------------- */

  function openHistory(){ renderHistory(); historyPanel.classList.add("open"); }
  function closeHistory(){ historyPanel.classList.remove("open"); }

  /* ---------------- 按键与键盘事件 ---------------- */

  function handleButton(b){
    var action = b.dataset.action;
    if (action) {
      switch (action) {
        case "ac": clearAll(); break;
        case "back": backspace(); break;
        case "eq": evaluate(); break;
        case "sign": toggleSign(); break;
        case "second": setSecond(!second); break;
        case "mode": toggleMode(); break;
        case "rand": insertRandom(); break;
        case "mc": mem = 0; memHas = false; store.set("scicalc_mem", 0); store.set("scicalc_mem_has", false); updateMemKeys(); break;
        case "mr": memoryRecall(); break;
        case "ms": memoryStore("set"); break;
        case "mplus": memoryStore("add"); break;
        case "mminus": memoryStore("sub"); break;
      }
      return;
    }
    var kind = b.dataset.kind;
    var ins = b.dataset.ins;
    if (second && b.dataset.ins2) ins = b.dataset.ins2;
    switch (kind) {
      case "num": inputNumber(ins); break;
      case "dot": inputDot(); break;
      case "ee": inputEE(); break;
      case "op": inputOp(ins); break;
      case "post": inputPost(ins); break;
      case "func": inputFunc(ins); break;
      case "const": inputConst(ins); break;
      case "open": inputOpen(); break;
      case "close": inputClose(); break;
    }
    if (b.dataset.alt === "1") setSecond(false);
  }

  document.querySelector(".pad").addEventListener("click", function(e){
    var b = e.target.closest("button.key");
    if (b) handleButton(b);
  });

  document.addEventListener("keydown", function(e){
    if (e.ctrlKey || e.altKey || e.metaKey) return;
    var k = e.key;
    if (/^[0-9]$/.test(k)) { inputNumber(k); e.preventDefault(); return; }
    if (k === ".") { inputDot(); e.preventDefault(); return; }
    if (k === "+") { inputOp("+"); e.preventDefault(); return; }
    if (k === "-") { inputOp("−"); e.preventDefault(); return; }
    if (k === "*") { inputOp("×"); e.preventDefault(); return; }
    if (k === "/") { inputOp("÷"); e.preventDefault(); return; }
    if (k === "^") { inputOp("^"); e.preventDefault(); return; }
    if (k === "%") { inputPost("%"); e.preventDefault(); return; }
    if (k === "!") { inputPost("!"); e.preventDefault(); return; }
    if (k === "(") { inputOpen(); e.preventDefault(); return; }
    if (k === ")") { inputClose(); e.preventDefault(); return; }
    if (k === "Enter" || k === "=") { evaluate(); e.preventDefault(); return; }
    if (k === "Backspace") { backspace(); e.preventDefault(); return; }
    if (k === "Escape") { clearAll(); e.preventDefault(); return; }
    if (k === "p" || k === "P") { inputConst("π"); e.preventDefault(); return; }
  });

  $("historyBtn").addEventListener("click", function(){
    historyPanel.classList.contains("open") ? closeHistory() : openHistory();
  });
  $("clearHistory").addEventListener("click", function(){
    history = [];
    store.set("scicalc_history", []);
    renderHistory();
  });
  $("copyBtn").addEventListener("click", copyResult);
  $("themeBtn").addEventListener("click", function(){
    var cur = document.documentElement.getAttribute("data-theme") === "dark" ? "dark" : "light";
    applyTheme(cur === "dark" ? "light" : "dark", true);
  });

  /* ---------------- 主题 ---------------- */

  function applyTheme(theme, manual){
    document.documentElement.setAttribute("data-theme", theme);
    if (manual) store.set("scicalc_theme", theme);
  }

  function whenPywebviewReady(){
    return new Promise(function(resolve){
      if (window.pywebview && window.pywebview.api) { resolve(); return; }
      window.addEventListener("pywebviewready", function(){ resolve(); });
      setTimeout(resolve, 1800);
    });
  }

  async function initTheme(){
    var saved = store.get("scicalc_theme", null);
    if (saved === "light" || saved === "dark") { applyTheme(saved); return; }
    var theme = null;
    await whenPywebviewReady();
    try {
      if (window.pywebview && window.pywebview.api && typeof window.pywebview.api.system_theme === "function") {
        theme = await window.pywebview.api.system_theme();
      }
    } catch (e) { theme = null; }
    if (theme !== "light" && theme !== "dark") {
      theme = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    }
    applyTheme(theme);
  }

  /* ---------------- 初始化 ---------------- */

  modeKey.classList.toggle("active", deg);
  updateMemKeys();
  renderHistory();
  render();
  initTheme();
})();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    api = Api()
    default_theme = api.system_theme()

    webview.create_window(
        "科学计算器",
        html=HTML,
        js_api=api,
        width=900,
        height=580,
        min_size=(760, 520),
        background_color="#202020" if default_theme == "dark" else "#F3F3F3",
    )
    webview.start()
