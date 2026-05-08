import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pydeck as pdk


@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    """加载CSV数据并添加信号强度颜色分类列"""
    df = pd.read_csv(path)
    df = add_rsrp_color_column(df)
    return df


def add_rsrp_color_column(df: pd.DataFrame) -> pd.DataFrame:
    """根据 RSRP 信号强度添加颜色分类列

    颜色规则:
    - RSRP > -90 dBm  → 绿色 [0, 200, 0]  (信号良好)
    - -110 <= RSRP <= -90 dBm → 橙色 [255, 165, 0] (信号中等)
    - RSRP < -110 dBm → 红色 [200, 0, 0] (弱覆盖)
    """

    def rsrp_to_color(rsrp):
        if rsrp > -90:
            return [0, 200, 0, 160]
        elif rsrp < -110:
            return [200, 0, 0, 160]
        else:
            return [255, 165, 0, 160]

    df = df.copy()
    df["rsrp_color"] = df["RSRP_dBm"].apply(rsrp_to_color)
    return df


def filter_dataframe(
    df: pd.DataFrame, bands: list, rsrp_range: tuple, terminals: list
) -> pd.DataFrame:
    """根据频段、RSRP 范围和终端类型筛选数据"""
    mask = (
        df["Band"].isin(bands)
        & (df["RSRP_dBm"] >= rsrp_range[0])
        & (df["RSRP_dBm"] <= rsrp_range[1])
        & df["TerminalType"].isin(terminals)
    )
    return df[mask]


def build_tooltip() -> dict:
    """构建地图悬浮提示 HTML"""
    return {
        "html": """
            <b>小区ID:</b> {CellID}<br/>
            <b>频段:</b> {Band}<br/>
            <b>RSRP:</b> {RSRP_dBm} dBm<br/>
            <b>SINR:</b> {SINR_dB} dB<br/>
            <b>下载速率:</b> {Download_Mbps} Mbps<br/>
            <b>终端类型:</b> {TerminalType}
        """,
        "style": {"backgroundColor": "steelblue", "color": "white"},
    }


def build_scatter_map(df: pd.DataFrame) -> pdk.Deck:
    """构建 2D 散点信号地图

    使用 pydeck ScatterplotLayer 在地图上绘制采样点，
    点颜色由 RSRP 信号强度决定（绿/橙/红）。
    """
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["Longitude", "Latitude"],
        get_fill_color="rsrp_color",  # 使用预计算的 RGBA 颜色列
        get_radius=50,  # 点半径 (米)
        pickable=True,  # 启用鼠标悬浮交互
        opacity=0.6,
        auto_highlight=True,
    )
    view_state = pdk.ViewState(
        latitude=df["Latitude"].mean(),
        longitude=df["Longitude"].mean(),
        zoom=12,
        pitch=0,  # 2D 俯视角度
    )
    return pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip=build_tooltip(),
    )


def build_column_map(df: pd.DataFrame) -> pdk.Deck:
    """构建 3D 柱状信号地图

    使用 pydeck ColumnLayer 以 3D 柱状图展示信号点，
    柱体高度与下载速率 (Download_Mbps) 成正比，
    柱体颜色由 RSRP 信号强度决定。
    """
    layer = pdk.Layer(
        "ColumnLayer",
        data=df,
        get_position=["Longitude", "Latitude"],
        get_elevation="Download_Mbps",  # 柱体高度对应下载速率
        elevation_scale=2,  # 高度缩放系数 (米/Mbps)
        radius=40,  # 柱体半径 (米)
        get_fill_color="rsrp_color",
        pickable=True,
        auto_highlight=True,
    )
    view_state = pdk.ViewState(
        latitude=df["Latitude"].mean(),
        longitude=df["Longitude"].mean(),
        zoom=12,
        pitch=60,  # 3D 倾斜视角
    )
    return pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip=build_tooltip(),
    )


def main():
    """Streamlit 主入口：构建 5G 信号可视化看板"""
    st.set_page_config(page_title="5G 信号可视化看板", layout="wide")

    st.title("📡 5G 信号可视化看板")
    st.markdown("基于路测数据的 5G 信号覆盖与质量交互式分析平台")

    # ---- 数据加载 ----
    df = load_data("data/signal_samples.csv")

    # ========================
    # 侧边栏筛选器
    # ========================
    st.sidebar.header("🔍 筛选器")

    # 频段多选
    available_bands = sorted(df["Band"].unique().tolist())
    selected_bands = st.sidebar.multiselect(
        "选择频段",
        options=available_bands,
        default=available_bands,
    )

    # RSRP 范围滑动条
    rsrp_range = st.sidebar.slider(
        "RSRP 范围 (dBm)",
        min_value=-120,
        max_value=-70,
        value=(-120, -70),
        step=1,
    )

    # 终端类型多选
    available_terminals = sorted(df["TerminalType"].unique().tolist())
    selected_terminals = st.sidebar.multiselect(
        "选择终端类型",
        options=available_terminals,
        default=available_terminals,
    )

    # 地图模式切换
    map_mode = st.sidebar.radio(
        "地图模式",
        options=["2D 散点图", "3D 柱状图"],
    )

    # 颜色图例
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 图例")
    st.sidebar.markdown("🟢 RSRP > -90 dBm (良好)")
    st.sidebar.markdown("🟠 -110 ~ -90 dBm (中等)")
    st.sidebar.markdown("🔴 RSRP < -110 dBm (弱覆盖)")

    # ---- 应用筛选条件 ----
    filtered_df = filter_dataframe(
        df, selected_bands, rsrp_range, selected_terminals
    )

    st.sidebar.markdown("---")
    st.sidebar.metric("筛选结果", f"{len(filtered_df)} 个采样点")

    # ========================
    # 主体区域：信号覆盖地图
    # ========================
    st.subheader("📡 信号覆盖地图")

    if len(filtered_df) == 0:
        st.warning("当前筛选条件下无数据，请调整筛选器。")
    else:
        if map_mode == "2D 散点图":
            st.pydeck_chart(build_scatter_map(filtered_df))
        else:
            st.pydeck_chart(build_column_map(filtered_df))

    # ========================
    # 数据概览指标
    # ========================
    st.subheader("📊 数据概览")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总采样点数", len(filtered_df))
    with col2:
        avg_rsrp = filtered_df["RSRP_dBm"].mean() if len(filtered_df) > 0 else 0
        st.metric("平均 RSRP", f"{avg_rsrp:.1f} dBm")
    with col3:
        avg_dl = filtered_df["Download_Mbps"].mean() if len(filtered_df) > 0 else 0
        st.metric("平均下载速率", f"{avg_dl:.1f} Mbps")

    # ========================
    # 频段分布柱状图
    # ========================
    st.subheader("📶 各频段基站分布")
    if len(filtered_df) > 0:
        band_counts = filtered_df["Band"].value_counts()
        st.bar_chart(band_counts)
    else:
        st.info("无数据可显示")

    # ========================
    # 双列布局：终端类型饼图 + RSRP 分布直方图
    # ========================
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📱 终端类型占比")
        if len(filtered_df) > 0:
            fig, ax = plt.subplots()
            terminal_counts = filtered_df["TerminalType"].value_counts()
            ax.pie(
                terminal_counts.values,
                labels=terminal_counts.index,
                autopct="%1.1f%%",
            )
            ax.axis("equal")
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.info("无数据可显示")

    with col_right:
        st.subheader("📉 RSRP 分布直方图")
        if len(filtered_df) > 0:
            hist, bin_edges = np.histogram(
                filtered_df["RSRP_dBm"].dropna(),
                bins=range(-120, -65, 5),
            )
            hist_df = pd.DataFrame(
                {"采样数": hist},
                index=[f"{bin_edges[i]}~{bin_edges[i+1]}" for i in range(len(hist))],
            )
            st.bar_chart(hist_df)
        else:
            st.info("无数据可显示")


if __name__ == "__main__":
    main()
