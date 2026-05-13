"""
样式表模块 - 淡蓝色主题 QSS
支持动态调整字体大小
"""


def build_qss(font_size=30):
    """根据基础字体大小生成样式表"""
    s = font_size
    sm = max(20, s - 4)   # 小字
    lg = s + 6            # 大字
    xs = max(18, s - 6)   # 超小字

    return f"""
    /* 全局 */
    QWidget {{
        font-family: "Microsoft YaHei UI", "微软雅黑", sans-serif;
        font-size: {s}px;
        color: #333333;
    }}

    /* 主窗口 */
    QMainWindow, QWidget#centralWidget {{
        background-color: #F0F4F8;
    }}

    /* 顶部搜索区域 */
    QWidget#headerWidget {{
        background-color: #B3D9FF;
        border-bottom: 2px solid #99C8F0;
    }}

    /* 搜索框 */
    QLineEdit#searchEdit {{
        background-color: #FFFFFF;
        border: 2px solid #CCE0F5;
        border-radius: 24px;
        padding: 12px 24px;
        font-size: {s}px;
        color: #333333;
        min-height: 48px;
        selection-background-color: #B3D9FF;
    }}
    QLineEdit#searchEdit:focus {{
        border: 3px solid #7FBAFF;
    }}

    /* 存储期限标签 */
    QLabel#expiryLabel {{
        font-size: {sm}px;
        color: #666666;
    }}

    /* 存储期限单选按钮 */
    QRadioButton {{
        font-size: {sm}px;
        color: #666666;
        spacing: 10px;
    }}
    QRadioButton::indicator {{
        width: 24px;
        height: 24px;
        border-radius: 12px;
        border: 3px solid #B3D9FF;
        background-color: #FFFFFF;
    }}
    QRadioButton::indicator:checked {{
        background-color: #7FBAFF;
        border: 3px solid #7FBAFF;
    }}

    /* 字体调节按钮 */
    QPushButton#fontBtn {{
        background-color: #7FBAFF;
        color: #FFFFFF;
        border-radius: 6px;
        padding: 4px 12px;
        font-size: {sm}px;
        min-height: 36px;
        min-width: 40px;
    }}
    QPushButton#fontBtn:hover {{
        background-color: #5DA0E0;
    }}

    /* 字体大小显示 */
    QLabel#fontSizeLabel {{
        font-size: {sm}px;
        color: #333333;
        font-weight: bold;
        min-width: 50px;
    }}

    /* 复选框 */
    QCheckBox {{
        font-size: {sm}px;
        spacing: 8px;
    }}
    QCheckBox::indicator {{
        width: 24px;
        height: 24px;
        border-radius: 5px;
        border: 3px solid #B3D9FF;
        background-color: #FFFFFF;
    }}
    QCheckBox::indicator:checked {{
        background-color: #7FBAFF;
        border: 3px solid #7FBAFF;
    }}

    /* 卡片区域滚动 */
    QScrollArea {{
        border: none;
        background-color: transparent;
    }}
    QScrollBar:vertical {{
        background-color: #E8EEF4;
        width: 14px;
        border-radius: 7px;
    }}
    QScrollBar::handle:vertical {{
        background-color: #B3D9FF;
        border-radius: 7px;
        min-height: 50px;
    }}
    QScrollBar::handle:vertical:hover {{
        background-color: #7FBAFF;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    /* 卡片容器 */
    QWidget#cardContainer {{
        background-color: transparent;
    }}

    /* 卡片基础 */
    QFrame#cardFrame {{
        background-color: #FFFFFF;
        border: 2px solid #E0E8F0;
        border-radius: 12px;
        padding: 6px;
    }}
    QFrame#cardFrame:hover {{
        border: 2px solid #B3D9FF;
    }}

    /* 过期卡片 */
    QFrame#cardFrame[expired="true"] {{
        background-color: #FFF5F0;
        border: 2px solid #FFD5C0;
    }}

    /* 置顶卡片 */
    QFrame#cardFrame[pinned="true"] {{
        border-left: 5px solid #FFD700;
    }}

    /* 卡片时间标签 */
    QLabel#timeLabel {{
        font-size: {xs}px;
        color: #999999;
    }}

    /* 卡片内容标签 */
    QLabel#contentLabel {{
        font-size: {s}px;
        color: #333333;
        line-height: 1.5;
    }}

    /* 按钮通用 */
    QPushButton {{
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-size: {sm}px;
        min-height: 44px;
    }}
    QPushButton:hover {{
        background-color: #E8EEF4;
    }}
    QPushButton:pressed {{
        background-color: #D0DCE8;
    }}

    /* 主要按钮 */
    QPushButton#primaryBtn {{
        background-color: #B3D9FF;
        color: #FFFFFF;
    }}
    QPushButton#primaryBtn:hover {{
        background-color: #7FBAFF;
    }}

    /* 危险按钮 */
    QPushButton#dangerBtn {{
        color: #FF6B6B;
    }}
    QPushButton#dangerBtn:hover {{
        background-color: #FFE8E8;
    }}

    /* 复制按钮 */
    QPushButton#copyBtn {{
        color: #7FBAFF;
    }}
    QPushButton#copyBtn:hover {{
        background-color: #E8F4FF;
    }}

    /* 置顶按钮 */
    QPushButton#pinBtn {{
        color: #FFD700;
    }}
    QPushButton#pinBtn:hover {{
        background-color: #FFF8E0;
    }}
    QPushButton#pinBtn[pinned="true"] {{
        color: #FFA500;
    }}

    /* 清理按钮 */
    QPushButton#cleanBtn {{
        background-color: #FFE0CC;
        color: #FF6B6B;
        border-radius: 10px;
        padding: 14px 32px;
        font-size: {sm}px;
        min-height: 48px;
    }}
    QPushButton#cleanBtn:hover {{
        background-color: #FFC8A8;
    }}

    /* 底部操作栏按钮 */
    QPushButton#bottomBtn {{
        background-color: #FFE0CC;
        color: #FF6B6B;
        border-radius: 10px;
        padding: 14px 28px;
        font-size: {sm}px;
        min-height: 48px;
    }}
    QPushButton#bottomBtn:hover {{
        background-color: #FFC8A8;
    }}

    /* 空状态提示 */
    QLabel#emptyLabel {{
        font-size: {s}px;
        color: #999999;
        padding: 80px;
    }}

    /* 状态栏标签 */
    QLabel#statusLabel {{
        font-size: {xs}px;
        color: #999999;
        padding: 8px 20px;
    }}

    /* 复制成功反馈 */
    QLabel#copyToast {{
        font-size: {s}px;
        color: #4CAF50;
        font-weight: bold;
        padding: 8px 20px;
    }}
    """
