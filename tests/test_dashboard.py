"""5G 信号可视化看板 - 单元测试"""

import pandas as pd
import pytest
from app import add_rsrp_color_column, filter_dataframe, load_data


@pytest.fixture
def sample_df():
    """构建一个包含三种 RSRP 等级的样本 DataFrame"""
    return pd.DataFrame(
        {
            "Latitude": [31.21, 31.22, 31.23],
            "Longitude": [121.47, 121.48, 121.49],
            "CellID": [1001, 1002, 1003],
            "Band": ["n28", "n41", "n78"],
            "RSRP_dBm": [-80, -100, -115],
            "SINR_dB": [15, 10, 5],
            "TerminalType": ["Smartphone", "CPE", "IoT"],
            "Download_Mbps": [200, 500, 800],
        }
    )


class TestColorClassification:
    """测试 RSRP 信号强度颜色分类逻辑"""

    def test_color_good_signal(self, sample_df):
        """RSRP > -90 dBm 应标记为绿色"""
        result = add_rsrp_color_column(sample_df)
        assert result.loc[0, "rsrp_color"] == [0, 200, 0, 160]

    def test_color_medium_signal(self, sample_df):
        """-110 <= RSRP <= -90 dBm 应标记为橙色"""
        result = add_rsrp_color_column(sample_df)
        assert result.loc[1, "rsrp_color"] == [255, 165, 0, 160]

    def test_color_weak_signal(self, sample_df):
        """RSRP < -110 dBm 应标记为红色"""
        result = add_rsrp_color_column(sample_df)
        assert result.loc[2, "rsrp_color"] == [200, 0, 0, 160]

    def test_color_column_added(self, sample_df):
        """验证颜色列被正确添加到 DataFrame"""
        result = add_rsrp_color_column(sample_df)
        assert "rsrp_color" in result.columns
        assert len(result) == len(sample_df)


class TestFiltering:
    """测试数据筛选逻辑"""

    def test_filter_band(self):
        """按频段筛选：仅返回选定频段的数据"""
        df = pd.DataFrame(
            {
                "Band": ["n28", "n41", "n78"],
                "RSRP_dBm": [-80, -90, -100],
                "TerminalType": ["Smartphone", "CPE", "IoT"],
            }
        )
        result = filter_dataframe(df, ["n41"], (-120, -70), ["Smartphone", "CPE", "IoT"])
        assert len(result) == 1
        assert result.iloc[0]["Band"] == "n41"

    def test_filter_rsrp_range(self):
        """按 RSRP 范围筛选：仅返回范围内的数据"""
        df = pd.DataFrame(
            {
                "Band": ["n28", "n28", "n28"],
                "RSRP_dBm": [-80, -100, -115],
                "TerminalType": ["Smartphone", "Smartphone", "Smartphone"],
            }
        )
        result = filter_dataframe(df, ["n28"], (-110, -85), ["Smartphone"])
        assert len(result) == 1
        assert result.iloc[0]["RSRP_dBm"] == -100

    def test_filter_terminal(self):
        """按终端类型筛选：仅返回选定类型的数据"""
        df = pd.DataFrame(
            {
                "Band": ["n28", "n28", "n28"],
                "RSRP_dBm": [-80, -90, -100],
                "TerminalType": ["CPE", "IoT", "CPE"],
            }
        )
        result = filter_dataframe(df, ["n28"], (-120, -70), ["CPE"])
        assert len(result) == 2

    def test_filter_empty_result(self):
        """筛选无匹配数据时返回空 DataFrame"""
        df = pd.DataFrame(
            {
                "Band": ["n28"],
                "RSRP_dBm": [-80],
                "TerminalType": ["Smartphone"],
            }
        )
        result = filter_dataframe(df, ["n41"], (-120, -70), ["Smartphone"])
        assert len(result) == 0


class TestIntegration:
    """集成测试：验证真实 CSV 数据加载"""

    def test_load_real_csv(self):
        """验证真实 CSV 文件能正确加载并包含颜色列"""
        df = load_data("data/signal_samples.csv")
        assert len(df) == 500
        assert "rsrp_color" in df.columns
        assert set(df["Band"].unique()) == {"n28", "n41", "n78"}
        assert set(df["TerminalType"].unique()) == {"Smartphone", "CPE", "IoT"}
