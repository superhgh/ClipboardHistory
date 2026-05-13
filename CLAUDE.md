# 历史粘贴板 - 项目手册

## 项目简介
Windows 10 历史粘贴板软件，自动记录复制内容（文字+图片），支持搜索、管理、过期清理。
使用 Python 3.12 + PyQt5 + SQLite 开发。

## 项目路径
- 主目录：`d:/AI/ClipboardHistory/`
- 源代码：`src/`
- 文档：`docs/`
- 日志：`logs/`
- 数据：`data/`（自动创建）
- 打包输出：`dist/ClipboardHistory/ClipboardHistory.exe`

## 启动方式
- 开发：双击 `run.bat`
- 打包后：双击 `dist/ClipboardHistory/ClipboardHistory.exe`

## 文档索引

| 文档 | 路径 |
|------|------|
| 开发需求 | [docs/01-开发需求.md](docs/01-开发需求.md) |
| 技术方案 | [docs/02-技术方案.md](docs/02-技术方案.md) |
| 设计规范 | [docs/03-设计规范.md](docs/03-设计规范.md) |
| 开发步骤 | [docs/04-开发步骤.md](docs/04-开发步骤.md) |
| 测试规范 | [docs/05-测试规范.md](docs/05-测试规范.md) |
| 开发日志 | [logs/](./logs/) |

## 架构概览

```
src/
├── main.py              # 应用入口，启动 QApplication + 全局样式
├── main_window.py       # 主窗口：搜索、存储期限、多选、复制/删除/置顶
├── card_widget.py       # 卡片组件：TextCard / ImageCard / ClickableLabel
├── clipboard_monitor.py # 剪贴板监听（500ms 定时轮询，多途径图片检测）
├── data_manager.py      # 业务逻辑：CRUD、去重、过期标记
├── database.py          # SQLite 底层操作
├── image_utils.py       # 图片保存与缩略图（QBuffer 中转）
├── styles.py            # build_qss(font_size) 动态样式表
└── paths.py             # 统一路径（开发/打包后）
```

## 已有功能清单
- 自动记录复制文字和图片（文字 MD5 去重，图片内容 MD5 去重）
- 卡片按时间倒序排列，置顶优先
- 点击卡片内容直接复制（绿色高亮+文字反馈）
- 多选（复选框/全选/取消全选）+ 批量删除
- 一键删除全部
- 存储期限 1/3/5 天，过期标记不自动删除
- 一键清理过期
- 全文搜索
- 字体 A+/A- 实时调节（范围 20~50px，默认 24px）
- 图片粘贴到桌面→文件（QMimeData + 文件 URL）
- 窗口可拖动边框调整大小

## 开发规范
1. 代码注释、界面文字、说明文档均使用简体中文
2. 遵循 PEP 8
3. 每个功能模块完成后立即测试
4. 每日结束前更新开发日志
5. 需求/设计变更时同步更新 docs/ 文档

## 已知技术要点
- PyQt5 启动前必须设置 `QT_QPA_PLATFORM_PLUGIN_PATH` 指向插件目录
- 新版 Pillow 移除了 `ImageQt`，改用 `QBuffer` 中转 QImage→PNG→PIL
- 剪贴板监听用 500ms 定时轮询替代 `dataChanged` 信号（Windows 兼容性）
- 图片去重用内容 MD5，不能用 `cacheKey()`（每次变化）
- PyInstaller 打包必须在英文路径下（Qt 钩子不支持中文路径）
- 用户数据目录通过 `sys.frozen` 判断：开发时=项目根/data，打包后=exe所在目录/data
