---
name: fluent-pywebview-app
description: Generates a Windows 11 Fluent-style, single-file Python + pywebview desktop application. HTML/CSS/JS is embedded as interface strings inside the Python file and displayed in a native window rather than opened in a browser. Use when the user mentions "pywebview desktop app", "Fluent-style Python GUI", "HTML embedded as UI in a Python window", "single-file Python desktop program", or "Windows 11 style desktop app". HTML strings must prevent unclosed triple quotes, ensuring the output is complete, runnable Python code.
---

# Fluent pywebview Desktop App Generator

## When to Use

Activate this skill when the user requests any of the following scenarios:

- Creating a desktop app with pywebview
- Building the UI with HTML/CSS/JS
- Windows 11 Fluent Design style
- A single-file Python desktop program with HTML embedded as strings
- Light/dark theme switching required

## Mandatory Output Requirements

1. Must output complete code that can be saved directly as a `.py` file and run.
2. No `...`, "omitted", "same as above", `TODO`, or "abbreviated here" placeholders are allowed.
3. A comment at the top of the file must state the dependency installation command (e.g., `pip install pywebview`).
4. All triple quotes must be closed in pairs; all HTML tags, `<style>`, and `<script>` blocks must be closed.
5. Write only functional comments—no other commentary.

## Fluent Design Specifications

### Color Tokens

Light theme:
- Background `#F3F3F3`
- Card `rgba(255,255,255,0.72)`
- Primary text `#1A1A1A`, secondary `#616161`, tertiary `#8A8A8A`
- Stroke `rgba(0,0,0,0.06)`, strong stroke `rgba(0,0,0,0.11)`
- Accent `#0067C0`, accent text `#FFFFFF`
- Hover `rgba(0,0,0,0.037)`, pressed `rgba(0,0,0,0.074)`

Dark theme:
- Background `#202020`
- Card `rgba(255,255,255,0.045)`
- Primary text `#FFFFFF`, secondary `#C8C8C8`, tertiary `#9A9A9A`
- Stroke `rgba(255,255,255,0.06)`, strong stroke `rgba(255,255,255,0.11)`
- Accent `#60CDFF`, accent text `#00334D`
- Hover `rgba(255,255,255,0.055)`, pressed `rgba(255,255,255,0.09)`

All colors must go through CSS variables; theme switching only changes `html[data-theme]`.

### Typography

```css
font-family: "Segoe UI Variable Text", "Segoe UI",
             "Microsoft YaHei UI", "Microsoft YaHei",
             system-ui, -apple-system, sans-serif;
```

Use `"Cascadia Code", "Consolas", monospace` for monospaced content.

### Sizing and Border Radius

- Nav item height 38px, border radius 5px
- Button height 32px, border radius 4px
- Card border radius 8px, padding 16px 18px
- Toggle switch 40×20, border radius 10px, thumb 14px
- Page title 28px / 600, body text 14px / 400, caption 12px

### Motion

- General easing `cubic-bezier(0.2, 0, 0, 1)`
- Theme switching `transition: background-color .25s ease, color .25s ease`
- Hover / pressed states 0.1s ~ 0.16s
- Page transition: fade in and slide up over 0.24s

### Shadows and Glass

- Card shadow `0 1px 2px rgba(0,0,0,0.04), 0 2px 8px rgba(0,0,0,0.045)`
- Flyout/overlay shadow `0 8px 28px rgba(0,0,0,0.16)`, deepened in dark mode
- Simulate acrylic with semi-transparent solid colors

### Interaction Details

- Text selection disabled by default (`user-select: none`), except for input areas and information values
- Close button hover color `#C42B1C`
- Focus state uses a stroke rather than an outer glow

### Python-Side Responsibilities

Implement as much functionality as possible in HTML; use Python to supplement anything that cannot be done there.

### Default Window Configuration

- Centered on screen
- Native system title bar

## Self-Check Checklist (verify each item before output)

- [ ] All `"""` are closed in pairs
- [ ] Colors go through CSS variables, and theme switching has transitions

## Packaging Configuration

Generate the `.py` file first, then ask the user whether they want an exe package. If so, package it using `pyinstaller --onefile --windowed`.
