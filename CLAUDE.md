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

## 避坑指南（踩过才懂）

### PyQt5
- **启动前必须设 `QT_QPA_PLATFORM_PLUGIN_PATH`** 指向 PyQt5 的 `Qt5/plugins` 目录，否则 `qwindows.dll` 找不到
- **高 DPI 属性用 try/except**：`AA_EnableHighDpiScaling` 等在新/旧版 Qt 中可能不存在，直接调用崩溃
- **QPixmap 不会自动导入**：即使已 `from PyQt5.QtGui import QImage`，用到 QPixmap 时需显式再 import
- **Windows 剪贴板别用 `dataChanged` 信号**：回调不稳定，用 `QTimer` 500ms 定时轮询

### 图片处理
- **去重不可用 `QImage.cacheKey()`**：每次返回不同值，必须对内容做 MD5 哈希
- **新版 Pillow 没有 `ImageQt`**：用 `QBuffer` 中转 → QImage 存为 PNG 字节 → BytesIO → PIL.Image
- **先存图再入库**：反过来会导致 INSERT 成功但文件缺失的脏记录

### 数据库
- **`conn.total_changes` 不准确**：统计连接生命周期全部变更，用 `cursor.rowcount` 获取本次影响行数
- **所有操作 try/finally 关连接**：否则 SQLite 文件锁不释放
- **开启 WAL 模式**：`PRAGMA journal_mode=WAL`，读写并发性能远好于默认 delete 模式

### PyInstaller 打包
- **必须在英文路径下运行**：Qt 钩子无法处理中文路径
- **hiddenimports 显式声明**：PyQt5、PIL.Image、sqlite3 不会被自动检测
- **`sys.frozen` 判断环境**：打包后数据目录用 `os.path.dirname(sys.executable)`，开发时用项目根

### 测试
- **SQLite 时间戳精度只到秒**：同一秒插入多条记录排序不可靠，测试用不同显式时间戳
- **Windows 下 PIL 图片要显式 close()**：否则临时文件清理时 PermissionError
- **缩略图瘦身验证**：原图必须大于缩略图上限 200x200，否则尺寸相同断言失败

### Git / GitHub
- **邮箱隐私保护拦截推送**：用 `ID+username@users.noreply.github.com` 替代私人邮箱
- **国内需配代理**：`git config --local http.proxy http://127.0.0.1:端口`
- **gh CLI 需 winget 安装**：`winget install GitHub.cli`，装完新终端才生效

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
