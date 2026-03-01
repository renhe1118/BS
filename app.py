from flask import Flask, render_template, request, jsonify
import os
import sys
import logging
from config import config
from src.data_processor import DataProcessor
from src.data_analyzer import DataAnalyzer
from src.visualizer import Visualizer

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 初始化Flask应用
app = Flask(__name__)
app.config.from_object(config['development'])

# 全局变量存储处理后的数据
processed_df = None
analyzer = None
visualizer = None
load_error = None


def load_data():
    """加载和处理数据"""
    global processed_df, analyzer, visualizer, load_error

    if processed_df is not None:
        return True

    try:
        # 检查data目录
        data_dir = app.config['RAW_DATA_PATH']
        logger.info(f"数据目录: {data_dir}")

        # 查找数据文件（支持 .xlsx, .xls, .csv）
        data_file = None
        for filename in ['shanghai_house.xlsx', 'shanghai_house.xls', 'shanghai_house.csv']:
            candidate = os.path.join(data_dir, filename)
            if os.path.exists(candidate):
                data_file = candidate
                logger.info(f"找到数据文件: {data_file}")
                break

        if not data_file:
            load_error = f"在 {data_dir} 目录中未找到数据文件 (shanghai_house.xlsx/xls/csv)"
            logger.warning(load_error)
            return False

        # 数据处理流程
        logger.info("=" * 50)
        logger.info("开始加载和处理数据...")
        logger.info("=" * 50)

        processor = DataProcessor(data_file)
        processor.load_data()
        processor.check_data_quality()
        processor.clean_data()
        processor.handle_missing_values(strategy='drop')

        processed_df = processor.df

        # 验证数据
        logger.info(f"处理后数据形状: {processed_df.shape}")
        logger.info(f"处理后列名: {processed_df.columns.tolist()}")

        analyzer = DataAnalyzer(processed_df)
        visualizer = Visualizer(processed_df, app.config['CHARTS_OUTPUT_PATH'])

        logger.info("=" * 50)
        logger.info("数据加载和处理完成！")
        logger.info("=" * 50)
        return True

    except Exception as e:
        load_error = f"数据加载失败: {str(e)}"
        logger.error(load_error, exc_info=True)
        return False


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    """数据仪表板"""
    if not load_data():
        return render_template('error.html', error=load_error or '数据加载失败')

    return render_template('dashboard.html')


@app.route('/api/data/summary')
def get_data_summary():
    """获取数据摘要统计"""
    if processed_df is None:
        if not load_data():
            return jsonify({'error': load_error or '数据未加载'}), 400

    try:
        summary = {
            'total_records': len(processed_df),
            'total_districts': processed_df['行政区'].nunique() if '行政区' in processed_df.columns else 0,
            'avg_price': float(
                processed_df['总价(万元)'].mean().round(2)) if '总价(万元)' in processed_df.columns else 0,
            'avg_unit_price': float(
                processed_df['单价(元/㎡)'].mean().round(2)) if '单价(元/㎡)' in processed_df.columns else 0,
            'avg_area': float(processed_df['面积(㎡)'].mean().round(2)) if '面积(㎡)' in processed_df.columns else 0,
        }
        return jsonify(summary)
    except Exception as e:
        logger.error(f"获取数据摘要失败: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/data/district-stats')
def get_district_stats():
    """获取行政区统计"""
    if processed_df is None:
        if not load_data():
            return jsonify({'error': load_error or '数据未加载'}), 400

    try:
        stats = analyzer.get_district_summary()

        if stats is None:
            return jsonify({'error': '无法生成行政区统计'}), 500

        return jsonify({
            'columns': stats.columns.tolist(),
            'index': stats.index.tolist(),
            'data': stats.values.tolist()
        })
    except Exception as e:
        logger.error(f"获取行政区统计失败: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/charts/generate', methods=['POST'])
def generate_charts():
    """生成所有图表"""
    if visualizer is None:
        if not load_data():
            return jsonify({'error': load_error or '可视化器未初始化'}), 400

    try:
        results = visualizer.plot_all()
        return jsonify({
            'success': True,
            'message': '图表生成成功',
            'charts': list(results.keys())
        })
    except Exception as e:
        logger.error(f"生成图表失败: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/charts/<chart_name>')
def get_chart(chart_name):
    """获取指定图表的HTML内容"""
    chart_file = os.path.join(app.config['CHARTS_OUTPUT_PATH'], f'{chart_name}.html')

    if not os.path.exists(chart_file):
        logger.warning(f"图表文件不存在: {chart_file}")
        return jsonify({'error': f'图表不存在: {chart_name}'}), 404

    try:
        with open(chart_file, 'r', encoding='utf-8') as f:
            content = f.read()
        return {'html': content}
    except Exception as e:
        logger.error(f"读取图表失败: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/analysis/price-distribution')
def get_price_distribution():
    """获取价格分布分析"""
    if processed_df is None:
        if not load_data():
            return jsonify({'error': load_error or '分析器未初始化'}), 400

    try:
        price_stats = analyzer.analyze_price_distribution()

        if price_stats is None:
            return jsonify({'error': '无法生成价格分布统计'}), 500

        return jsonify({
            'mean': float(price_stats['mean']),
            'median': float(price_stats['median']),
            'std': float(price_stats['std']),
            'min': float(price_stats['min']),
            'max': float(price_stats['max'])
        })
    except Exception as e:
        logger.error(f"获取价格分布失败: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/analysis/top-districts')
def get_top_districts():
    """获取最昂贵的行政区"""
    if processed_df is None:
        if not load_data():
            return jsonify({'error': load_error or '分析器未初始化'}), 400

    try:
        top = analyzer.get_top_n_expensive_districts(n=10)

        if top is None:
            return jsonify({'error': '无法生成最昂贵行政区统计'}), 500

        return jsonify({
            'districts': top.index.tolist(),
            'prices': top.values.round(2).tolist()
        })
    except Exception as e:
        logger.error(f"获取最昂贵行政区失败: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({'error': '页面不存在'}), 404


@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    logger.error(f"服务器错误: {str(error)}", exc_info=True)
    return jsonify({'error': '服务器内部错误'}), 500


if __name__ == '__main__':
    # 应用启动时加载数据
    logger.info("=" * 50)
    logger.info("应用启动中...")
    logger.info("=" * 50)
    load_data()

    app.run(
        host=app.config['FLASK_HOST'],
        port=app.config['FLASK_PORT'],
        debug=app.config['DEBUG']
    )