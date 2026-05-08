# 📡 5G 信号可视化看板

基于 **Streamlit + PyDeck** 构建的 5G 路测数据交互式可视化分析平台。

---

## 功能特性

| 功能 | 说明 |
|---|---|
| **信号覆盖地图** | 2D 散点地图，采样点根据 RSRP 信号强度着色（绿/橙/红） |
| **3D 柱状地图** | 3D 视图，柱体高度随下载速率变化，直观展示数据分布 |
| **侧边栏筛选** | 频段多选、RSRP 范围滑动条、终端类型多选，实时联动更新 |
| **数据概览** | 总采样点数、平均 RSRP、平均下载速率指标卡片 |
| **频段分布图** | 柱状图展示各频段 (n28/n41/n78) 的采样点数量 |
| **终端类型占比** | 饼图展示 Smartphone / CPE / IoT 的分布比例 |
| **RSRP 直方图** | 信号强度分布直方图，按 5dBm 区间分组 |

---

## 快速开始

### 环境要求

- Python 3.9+
- pip

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动应用

```bash
streamlit run app.py
```

浏览器将自动打开 `http://localhost:8501`，即可看到 5G 信号可视化看板。

---

## 数据说明

数据集 `data/signal_samples.csv` 包含 500 条 5G 路测模拟数据，覆盖上海市区范围。

| 字段 | 说明 | 示例值 |
|---|---|---|
| Latitude | 纬度 | 31.209 |
| Longitude | 经度 | 121.483 |
| CellID | 小区标识 | 1926 |
| Band | 频段 | n28 / n41 / n78 |
| RSRP_dBm | 参考信号接收功率 | -94.94 |
| SINR_dB | 信噪比 | 5.44 |
| TerminalType | 终端类型 | Smartphone / CPE / IoT |
| Download_Mbps | 下载速率 | 138.21 |

### 颜色规则

- 🟢 **绿色**: RSRP > -90 dBm（信号良好）
- 🟠 **橙色**: -110 ≤ RSRP ≤ -90 dBm（信号中等）
- 🔴 **红色**: RSRP < -110 dBm（弱覆盖）

---

## 使用指南

1. **查看信号分布**：启动后默认显示 2D 散点地图，所有 500 个采样点按信号强度着色。
2. **筛选数据**：使用左侧侧边栏的筛选器，按频段、RSRP 范围或终端类型过滤数据，地图和图表实时更新。
3. **切换 3D 视图**：在侧边栏将"地图模式"切换为"3D 柱状图"，柱体高度表示下载速率。
4. **查看统计**：向下滚动查看频段分布、终端占比和 RSRP 直方图。

---

## 项目结构

```
code-with-ai-contest/
├── app.py                 # Streamlit 主应用
├── requirements.txt       # Python 依赖
├── data/
│   └── signal_samples.csv # 5G 信号采样数据
├── tests/
│   └── test_dashboard.py  # 单元测试
└── README.md              # 项目文档
```

---

## 运行测试

```bash
pytest tests/ -v
```

测试覆盖：
- RSRP 颜色分类逻辑（绿/橙/红）
- 频段、RSRP 范围、终端类型筛选
- 真实 CSV 数据加载集成验证

---

## 技术栈

- **Streamlit** — Web 应用框架
- **PyDeck** — 交互式地图 (2D/3D)
- **Pandas** — 数据处理
- **Matplotlib** — 饼图渲染
- **NumPy** — 数值计算

---

## 运行截图

> *(请在此处贴上 2-3 张应用运行截图)*

---

<p align="center">Built for "Code with AI" Contest</p>
