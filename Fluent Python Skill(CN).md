---
name: fluent-pywebview-app
description: 生成 Windows 11 Fluent 风格的、单文件 Python + pywebview 桌面应用。HTML/CSS/JS 作为界面字符串嵌入 Python 文件，在原生窗口内显示而非浏览器打开。当用户提到 "pywebview 桌面应用"、"Fluent 风格 Python GUI"、"HTML 作为界面嵌入 Python 窗口"、"单文件 Python 桌面程序"、"Windows 11 风格桌面应用" 时使用。HTML 字符串防止三引号未闭合，保证输出完整可运行py代码。
---

# Fluent pywebview 桌面应用生成器

## 何时使用

当用户要求以下任一场景时启用本技能：

- 用 pywebview 创建桌面应用
- 用 HTML/CSS/JS 做界面
- Windows 11 Fluent Design 风格
- 单文件 Python 桌面程序，HTML 以字符串形式内嵌
- 需要浅色/深色主题切换

## 输出硬性要求

1. 必须输出完整、可直接保存为 `.py` 并运行的代码。
2. 禁止出现 `...`、`省略`、`其余同上`、`TODO`、`此处略`。
3. 文件顶部注释写明依赖安装命令（如 `pip install pywebview`）。
4. 所有三引号必须成对闭合；所有 HTML 标签、`<style>`、`<script>` 必须闭合。
5. 只写功能的注释，不要其他注释

## Fluent 设计规范

### 颜色令牌

浅色：
- 背景 `#F3F3F3`
- 卡片 `rgba(255,255,255,0.72)`
- 文字主色 `#1A1A1A`，次要 `#616161`，三级 `#8A8A8A`
- 描边 `rgba(0,0,0,0.06)`，强描边 `rgba(0,0,0,0.11)`
- 强调色 `#0067C0`，强调文字 `#FFFFFF`
- 悬停 `rgba(0,0,0,0.037)`，按下 `rgba(0,0,0,0.074)`

深色：
- 背景 `#202020`
- 卡片 `rgba(255,255,255,0.045)`
- 文字主色 `#FFFFFF`，次要 `#C8C8C8`，三级 `#9A9A9A`
- 描边 `rgba(255,255,255,0.06)`，强描边 `rgba(255,255,255,0.11)`
- 强调色 `#60CDFF`，强调文字 `#00334D`
- 悬停 `rgba(255,255,255,0.055)`，按下 `rgba(255,255,255,0.09)`

所有颜色必须走 CSS 变量，主题切换只改 `html[data-theme]`。

### 字体

```css
font-family: "Segoe UI Variable Text", "Segoe UI",
             "Microsoft YaHei UI", "Microsoft YaHei",
             system-ui, -apple-system, sans-serif;
```

等宽内容用 `"Cascadia Code", "Consolas", monospace`。

### 尺寸与圆角

- 导航项高度 38px，圆角 5px
- 按钮高度 32px，圆角 4px
- 卡片圆角 8px，内边距 16px 18px
- 开关 40×20，圆角 10px，滑块 14px
- 分页标题 28px / 600，正文 14px / 400，辅助 12px

### 动效

- 通用缓动 `cubic-bezier(0.2, 0, 0, 1)`
- 主题切换 `transition: background-color .25s ease, color .25s ease`
- 悬停 / 按下 0.1s ~ 0.16s
- 页面切换淡入上移 0.24s

### 阴影与玻璃

- 卡片阴影 `0 1px 2px rgba(0,0,0,0.04), 0 2px 8px rgba(0,0,0,0.045)`
- 浮层阴影 `0 8px 28px rgba(0,0,0,0.16)`，深色下加深
- 半透明纯色模拟亚克力

### 交互细节

- 文本默认禁用选中（`user-select: none`），输入区和信息值除外
- 关闭按钮悬停色 `#C42B1C`
- 焦点态用描边而非外发光

### Python 端职责

功能尽量用 HTML 实现，实现不了的用 Python 补充。

### 默认窗口配置

- 屏幕居中显示
- 系统原生标题栏

## 自检清单（输出前逐项检查）

- [ ] 所有 `"""` 成对闭合
- [ ] 颜色走 CSS 变量，主题切换有过渡
- [ ] JS 调用 Python 前做了接口就绪检测

## 打包配置

先生成py文件，后询问用户是否要exe打包，如果需要，则使用pyinstaller --onefile --windowed 打包
