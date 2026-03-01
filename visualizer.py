import pandas as pd
from pyecharts.charts import Bar, Line, Pie, Scatter
from pyecharts import options as opts
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Visualizer:
    """可视化类"""

    def __init__(self, df, output_path='./static/charts'):
        """
        初始化可视化器

        Args:
            df: pandas DataFrame对象
            output_path: 图表输出路径
        """
        self.df = df
        self.output_path = output_path
        os.makedirs(output_path, exist_ok=True)

    def plot_district_count(self):
        """可视化各行政区房源数量分布"""
        logger.info("生成行政区房源数量柱状图...")

        if '行政区' not in self.df.columns:
            logger.warning("未找到行政区列")
            return None

        district_count = self.df['行政区'].value_counts().sort_values(ascending=False)

        bar = (
            Bar()
            .add_xaxis(district_count.index.tolist())
            .add_yaxis('房源数量', district_count.values.tolist())
            .set_global_opts(
                title_opts=opts.TitleOpts(title='上海各行政区二手房数量分布'),
                xaxis_opts=opts.AxisOpts(name='行政区'),
                yaxis_opts=opts.AxisOpts(name='房源数量'),
            )
        )

        output_file = os.path.join(self.output_path, 'district_count.html')
        bar.render(output_file)
        logger.info(f"图表已保存: {output_file}")
        return output_file

    def plot_district_avg_price(self):
        """可视化各行政区平均价格"""
        logger.info("生成行政区平均价格柱状图...")

        if '行政区' not in self.df.columns or '总价(万元)' not in self.df.columns:
            logger.warning("缺少必需列")
            return None

        avg_price = self.df.groupby('行政区')['总价(万元)'].mean().sort_values(ascending=False)

        bar = (
            Bar()
            .add_xaxis(avg_price.index.tolist())
            .add_yaxis('平均总价(万元)', avg_price.values.round(2).tolist())
            .set_global_opts(
                title_opts=opts.TitleOpts(title='上海各行政区二手房平均总价'),
                xaxis_opts=opts.AxisOpts(name='行政区'),
                yaxis_opts=opts.AxisOpts(name='平均总价(万元)'),
            )
        )

        output_file = os.path.join(self.output_path, 'district_avg_price.html')
        bar.render(output_file)
        logger.info(f"图表已保存: {output_file}")
        return output_file

    def plot_district_unit_price(self):
        """可视化各行政区平均单价"""
        logger.info("生成行政区平均单价柱状图...")

        if '行政区' not in self.df.columns or '单价(元/㎡)' not in self.df.columns:
            logger.warning("缺少必需列")
            return None

        unit_price = self.df.groupby('行政区')['单价(元/㎡)'].mean().sort_values(ascending=False)

        bar = (
            Bar()
            .add_xaxis(unit_price.index.tolist())
            .add_yaxis('平均单价(元/㎡)', unit_price.values.round(0).tolist())
            .set_global_opts(
                title_opts=opts.TitleOpts(title='上海各行政区二手房平均单价'),
                xaxis_opts=opts.AxisOpts(name='行政区'),
                yaxis_opts=opts.AxisOpts(name='平均单价(元/㎡)'),
            )
        )

        output_file = os.path.join(self.output_path, 'district_unit_price.html')
        bar.render(output_file)
        logger.info(f"图表已保存: {output_file}")
        return output_file

    def plot_orientation(self):
        """可视化房屋朝向分布"""
        logger.info("生成朝向分布饼图...")

        if '朝向' not in self.df.columns:
            logger.warning("未找到朝向字段")
            return None

        orientation = self.df['朝向'].value_counts()

        pie = (
            Pie()
            .add('', [(k, v) for k, v in orientation.items()])
            .set_global_opts(
                title_opts=opts.TitleOpts(title='二手房朝向分布'),
            )
        )

        output_file = os.path.join(self.output_path, 'orientation.html')
        pie.render(output_file)
        logger.info(f"图表已保存: {output_file}")
        return output_file

    def plot_building_year(self):
        """可视化建筑时间分布"""
        logger.info("生成建筑时间分布柱状图...")

        if '建筑年份' not in self.df.columns:
            logger.warning("未找到建筑年份字段")
            return None

        year_count = self.df['建筑年份'].value_counts().sort_index()

        line = (
            Line()
            .add_xaxis(year_count.index.astype(str).tolist())
            .add_yaxis('房源数量', year_count.values.tolist())
            .set_global_opts(
                title_opts=opts.TitleOpts(title='二手房建筑时间分布'),
                xaxis_opts=opts.AxisOpts(name='建筑年份'),
                yaxis_opts=opts.AxisOpts(name='房源数量'),
            )
        )

        output_file = os.path.join(self.output_path, 'building_year.html')
        line.render(output_file)
        logger.info(f"图表已保存: {output_file}")
        return output_file

    def plot_price_vs_area(self):
        """可视化价格与面积的关系"""
        logger.info("生成价格与面积散点图...")

        if '面积(㎡)' not in self.df.columns or '总价(万元)' not in self.df.columns:
            logger.warning("缺少必需列")
            return None

        # 转换为数值类型并去除NaN
        area = pd.to_numeric(self.df['面积(㎡)'], errors='coerce')
        price = pd.to_numeric(self.df['总价(万元)'], errors='coerce')

        # 去除NaN值
        valid_mask = ~(area.isna() | price.isna())
        area_clean = area[valid_mask].tolist()[:100]
        price_clean = price[valid_mask].tolist()[:100]

        scatter = (
            Scatter()
            .add_xaxis(area_clean)
            .add_yaxis('总价(万元)', price_clean)
            .set_global_opts(
                title_opts=opts.TitleOpts(title='房屋面积与总价关系'),
                xaxis_opts=opts.AxisOpts(name='面积(㎡)'),
                yaxis_opts=opts.AxisOpts(name='总价(万元)'),
            )
        )

        output_file = os.path.join(self.output_path, 'price_vs_area.html')
        scatter.render(output_file)
        logger.info(f"图表已保存: {output_file}")
        return output_file

    def plot_all(self):
        """生成所有图表"""
        logger.info("开始生成所有可视化图表...")
        results = {}

        chart_methods = [
            ('district_count', self.plot_district_count),
            ('district_avg_price', self.plot_district_avg_price),
            ('district_unit_price', self.plot_district_unit_price),
            ('orientation', self.plot_orientation),
            ('building_year', self.plot_building_year),
            ('price_vs_area', self.plot_price_vs_area),
        ]

        for name, method in chart_methods:
            try:
                result = method()
                if result:
                    results[name] = result
            except Exception as e:
                logger.error(f"生成 {name} 图表失败: {str(e)}")

        logger.info("所有图表生成完成！")
        return results