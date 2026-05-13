# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目简介
Windows 10 历史粘贴板软件，自动记录复制文字和图片，支持搜索、置顶、多选删除、过期管理。
**技术栈**: Python 3.12 + PyQt5 + SQLite

## 常用命令

### 开发运行
```bash
# 启动应用（开发模式）
venv/Scripts/python src/main.py

# Windows 用户：直接双击 run.bat
```

### 测试
```bash
# 运行全部测试（64 tests）
venv/Scripts/python -m pytest tests/ -v

# 仅运行单个测试文件
venv/Scripts/python -m pytest tests/test_database.py -v

# 运行性能基准测试
venv/Scripts/python tests/test_performance.py
```

### 代码检查
```bash
# 语法检查（git commit 时自动触发）
venv/Scripts/python -m py_compile src/*.py tests/*.py
```

### 打包
```bash
# PyInstaller 打包（必须在英文路径下执行）
pyinstaller 历史粘贴板.spec
# 输出: dist/ClipboardHistory/ClipboardHistory.exe
```

## 架构概览

```
src/
├── main.py              # 应用入口，设置 QT_QPA_PLATFORM_PLUGIN_PATH + QApplication
├── main_window.py       # 主窗口：搜索、存储期限、多选、复制/删除/置顶
├── card_widget.py       # CardBase → TextCard / ImageCard / ClickableLabel
├── clipboard_monitor.py # 500ms 定时轮询剪贴板，MD5 内容去重，多途径图片检测
├── data_manager.py      # 业务逻辑层：CRUD、文字/图片去重、过期标记
├── database.py          # SQLite 底层（WAL 模式，所有方法 try/finally 保护）
├── image_utils.py       # QImage→PIL→PNG（QBuffer 中转），缩略图 200x200
├── styles.py            # build_qss(font_size) 淡蓝色主题动态样式表
└── paths.py             # sys.frozen 判断开发/打包路径
```

**数据流**: `剪贴板轮询 → data_manager 去重 → database 入库 → main_window 刷新卡片`

## 已知技术要点

- **PyQt5 启动前**必须设置 `QT_QPA_PLATFORM_PLUGIN_PATH` 指向 PyQt5 Qt5/plugins 目录
- **剪贴板监听**用 500ms 定时轮询替代 `dataChanged` 信号（Windows 兼容性问题）
- **图片去重**用内容 MD5，不可用 `QImage.cacheKey()`（每次返回不同值）
- **PIL/Qt 转换**: 新版 Pillow 移除 `ImageQt`，改用 `QBuffer` 中转 QImage→PNG 字节→PIL
- **图片复制到剪贴板**: 同时设置图片数据 + 文件 URL（QMimeData），方便粘贴到桌面/文件夹
- **PyInstaller** 必须在英文路径下运行（Qt 钩子不支持中文路径）
- **用户数据目录**: 通过 `sys.frozen` 判断，开发时=项目根/data，打包后=exe 所在目录/data
- **自身复制抑制**: `clipboard_monitor.skip_next_change()` 防止软件的复制操作被自己记录
- **默认字体 24px**，A+/A- 按钮动态调整范围 20~50px（2px 步进）

## 项目约定

- 所有代码注释、UI 文字、文档均使用**简体中文**
- .claude/settings.json 已配置预提交 hook：`git commit` 前自动 `py_compile` 语法检查，失败则阻止提交
- 文字过长（>100000 字符）自动截断存储
- 置顶记录不被过期清理删除

## 测试结构

```
tests/
├── test_database.py       # 18 tests: CRUD、过期、搜索、排序、连接失败
├── test_data_manager.py   # 13 tests: 文字/图片添加、MD5 去重、置顶、文件删除
├── test_image_utils.py    # 5 tests: QImage 转换、保存、缩略图
├── test_performance.py    # 基准：10000 条查询 <0.06s
└── test_acceptance.py     # 15 tests: 全量功能验收
```
