import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataAnalyzer:
    """数据分析类"""

    def __init__(self, df):
        """
        初始化分析器

        Args:
            df: pandas DataFrame对象
        """
        self.df = df
        self.analysis_results = {}

    def analyze_by_district(self):
        """按行政区分析"""
        logger.info("执行按行政区分析...")

        if '行政区' not in self.df.columns or '总价(万元)' not in self.df.columns:
            logger.warning("缺少必需列")
            return None

        district_analysis = self.df.groupby('行政区').agg({
            '总价(万元)': ['count', 'mean', 'min', 'max'],
        }).round(2)

        self.analysis_results['district'] = district_analysis
        return district_analysis

    def analyze_orientation(self):
        """分析房屋朝向分布"""
        logger.info("执行朝向分析...")

        if '朝向' not in self.df.columns:
            logger.warning("未找到朝向字段")
            return None

        orientation = self.df['朝向'].value_counts()
        self.analysis_results['orientation'] = orientation
        return orientation

    def analyze_building_age(self):
        """分析建筑年龄分布"""
        logger.info("执行建筑年龄分析...")

        if '建筑年份' not in self.df.columns:
            logger.warning("未找到建筑年份字段")
            return None

        current_year = 2026
        self.df['房龄(年)'] = current_year - pd.to_numeric(self.df['建筑年份'], errors='coerce')

        age_distribution = pd.cut(self.df['房龄(年)'],
                                  bins=[0, 5, 10, 20, 30, 100],
                                  labels=['0-5年', '6-10年', '11-20年', '21-30年', '30年以上']).value_counts()

        self.analysis_results['building_age'] = age_distribution
        return age_distribution

    def analyze_price_distribution(self):
        """分析价格分布"""
        logger.info("执行价格分布分析...")

        if '总价(万元)' not in self.df.columns:
            logger.warning("未找到价格字段")
            return None

        price_data = pd.to_numeric(self.df['总价(万元)'], errors='coerce').dropna()

        price_stats = {
            'mean': float(price_data.mean()),
            'median': float(price_data.median()),
            'std': float(price_data.std()),
            'min': float(price_data.min()),
            'max': float(price_data.max())
        }

        self.analysis_results['price'] = price_stats
        return price_stats

    def analyze_area_distribution(self):
        """分析面积分布"""
        logger.info("执行面积分布分析...")

        if '面积(㎡)' not in self.df.columns:
            logger.warning("未找到面积字段")
            return None

        area_data = pd.to_numeric(self.df['面积(㎡)'], errors='coerce').dropna()
        area_bins = area_data.quantile([0, 0.25, 0.5, 0.75, 1.0])
        area_distribution = pd.cut(area_data, bins=area_bins, include_lowest=True).value_counts()

        self.analysis_results['area'] = area_distribution
        return area_distribution

    def correlation_analysis(self):
        """相关性分析"""
        logger.info("执行相关性分析...")

        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        correlation = self.df[numeric_cols].corr()

        self.analysis_results['correlation'] = correlation
        return correlation

    def get_top_n_expensive_districts(self, n=5):
        """获取最昂贵的N个行政区"""
        if '行政区' not in self.df.columns or '单价(元/㎡)' not in self.df.columns:
            logger.warning("缺少必需列")
            return None

        unit_price_data = pd.to_numeric(self.df['单价(元/㎡)'], errors='coerce')
        top_districts = self.df.groupby('行政区').apply(
            lambda x: unit_price_data[x.index].mean()
        ).nlargest(n)

        return top_districts

    def get_district_summary(self):
        """获取行政区综合摘要"""
        logger.info("获取行政区摘要...")

        if '行政区' not in self.df.columns:
            logger.warning("未找到行政区字段")
            return None

        agg_dict = {}

        if '总价(万元)' in self.df.columns:
            agg_dict['总价(万元)'] = 'mean'
        if '单价(元/㎡)' in self.df.columns:
            agg_dict['单价(元/㎡)'] = 'mean'
        if '面积(㎡)' in self.df.columns:
            agg_dict['面积(㎡)'] = 'mean'

        if not agg_dict:
            logger.warning("没有可聚合的列")
            return None

        summary = self.df.groupby('行政区').agg(agg_dict).round(2)

        # 重命名列
        summary.columns = ['平均' + col for col in summary.columns]

        return summary