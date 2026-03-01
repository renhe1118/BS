"""
上海二手房数据分析系统
Shanghai Secondhand House Data Analysis System

这个包包含数据处理、分析和可视化模块
"""

__version__ = '1.0.0'
__author__ = '任敬仰'
__email__ = '202205110149@email.com'

# 导入主要模块
from .data_processor import DataProcessor
from .data_analyzer import DataAnalyzer
from .visualizer import Visualizer
from .utils import (
    export_to_json,
    export_to_excel,
    get_timestamp,
    format_large_number,
    validate_dataframe
)

__all__ = [
    'DataProcessor',
    'DataAnalyzer',
    'Visualizer',
    'export_to_json',
    'export_to_excel',
    'get_timestamp',
    'format_large_number',
    'validate_dataframe'
]