---
name: Fluent-Python-App
description: Generate single-file Python desktop applications with Windows 11 Fluent style. The HTML/CSS/JS interface is embedded as a string inside the Python file. The PyWry library loads the content inside a native window instead of opening a web browser. Activate this skill when the user mentions "Python desktop app", "Fluent-style Python GUI", "HTML embedded as interface inside Python window", or "Windows 11-style desktop application". Ensure triple quotes are properly closed so the full runnable Python code is output without truncation.
---

# Fluent Python Desktop App Generator

## When to Use This Skill

Enable this skill for any of the following scenarios:
- Building desktop applications with Python
- Creating UI with HTML/CSS/JS
- Implementing Windows 11 Fluent Design visual style
- Building single-file Python desktop programs with embedded HTML strings
- Adding light/dark theme switching functionality

## Mandatory Output Requirements

1. Always output complete, runnable code that can be saved directly as a `.py` file.
2. No `...`, omissions, placeholders like `[omitted]`, `TODO`, or `[code omitted]`.
3. Include a comment at the top of the file with the installation command: `pip install PyWry`. Use the PyWry library to render HTML content.
4. All triple quotes must be properly paired and closed. All HTML tags, `<style>`, and `<script>` blocks must be fully closed.
5. Only include functional code comments; no extra explanatory text.

## Fluent Design Specifications

### Color Tokens

Light Mode:
- Background: `#F3F3F3`
- Card background: `rgba(255,255,255,0.72)`
- Primary text: `#1A1A1A`; Secondary text: `#616161`; Tertiary text: `#8A8A8A`
- Border: `rgba(0,0,0,0.06)`; Strong border: `rgba(0,0,0,0.11)`
- Accent color: `#0067C0`; Accent text: `#FFFFFF`
- Hover state: `rgba(0,0,0,0.037)`; Pressed state: `rgba(0,0,0,0.074)`

Dark Mode:
- Background: `#202020`
- Card background: `rgba(255,255,255,0.045)`
- Primary text: `#FFFFFF`; Secondary text: `#C8C8C8`; Tertiary text: `#9A9A9A`
- Border: `rgba(255,255,255,0.06)`; Strong border: `rgba(255,255,255,0.11)`
- Accent color: `#60CDFF`; Accent text: `#00334D`
- Hover state: `rgba(255,255,255,0.055)`; Pressed state: `rgba(255,255,255,0.09)`

All colors must be defined as CSS variables. Theme switching only modifies the `html[data-theme]` attribute.

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
- [ ] Interface readiness is checked before JS calls Python

## Packaging Configuration

Generate the `.py` file first, then ask the user whether they want an exe package. If so, package it using `pyinstaller --onefile --windowed`.
