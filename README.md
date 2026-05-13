# 历史粘贴板

Windows 剪贴板历史管理工具。自动记录所有复制内容（文字+图片），支持搜索、置顶、多选删除、过期自动清理。

**Python 3.12 + PyQt5 + SQLite**，打包为独立 exe，无 Python 环境也能运行。

---

## 功能

- **自动记录** — 启动后静默监听剪贴板，文字和图片自动保存
- **智能去重** — 文字按内容、图片按 MD5 去重，不记录重复内容
- **全文搜索** — 输入关键词实时筛选历史文字
- **点击即复制** — 点击卡片内容直接回到剪贴板，支持粘贴到桌面/文件夹
- **多选批量删除** — 复选框 + 全选/取消全选
- **置顶** — 重要记录固定在列表顶部
- **存储期限** — 1/3/5 天可选，过期标记不自动删除，可一键清理
- **字体调节** — A+/A- 实时调整 20~50px
- **窗口可缩放** — 拖动边框自定义尺寸

## 界面

淡蓝色主题，卡片式布局。顶部搜索栏 + 存储期限设置，中间卡片列表滚动浏览，底部工具栏。

```
┌─────────────────────────────┐
│  📋 历史粘贴板    [搜索...] │
│  存储期限: ○1天 ○3天 ○5天  │
│                             │
│  ┌ 2026-05-14 15:30 ──────┐ │
│  │ 这是一段复制的文字...   │ │
│  │ [📌置顶] [📋复制] [🗑] │ │
│  └─────────────────────────┘ │
│  ┌ 2026-05-14 15:28 ──────┐ │
│  │ [图片缩略图]           │ │
│  └─────────────────────────┘ │
│                             │
│  共 128 条  [全选] [删除选中]│
│  [🗑 删除全部] [🧹 清理过期]│
└─────────────────────────────┘
```

## 快速开始

### 方式一：下载 exe（推荐）

从 [Releases](https://github.com/superhgh/ClipboardHistory/releases) 下载 `ClipboardHistory.exe`，双击运行即可，无需安装 Python。

### 方式二：源码运行

```bash
# 1. 克隆项目
git clone https://github.com/superhgh/ClipboardHistory.git
cd ClipboardHistory

# 2. 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行
python src/main.py
```

### 方式三：自己打包

```bash
pip install pyinstaller
pyinstaller 历史粘贴板.spec
# 输出: dist/ClipboardHistory/ClipboardHistory.exe
```

## 技术架构

```
src/
├── main.py              # 应用入口
├── main_window.py       # 主窗口 UI + 事件处理
├── card_widget.py       # 卡片组件（文字/图片）
├── clipboard_monitor.py # 500ms 定时轮询剪贴板
├── data_manager.py      # 业务逻辑层
├── database.py          # SQLite 数据层
├── image_utils.py       # 图片保存与缩略图
├── styles.py            # QSS 样式表
└── paths.py             # 路径管理（开发/打包）
```

数据流：`剪贴板轮询 → 去重判断 → 数据库入库 → UI 刷新卡片`

## 开发

```bash
# 运行全部测试 (64 tests)
pytest tests/ -v

# 运行单个测试文件
pytest tests/test_database.py -v

# 运行性能基准
python tests/test_performance.py
```

## 许可证

MIT
