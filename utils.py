import json
import pandas as pd
from datetime import datetime

def export_to_json(data, filename):
    """导出数据为JSON格式"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)

def export_to_excel(df, filename):
    """导出数据为Excel格式"""
    df.to_excel(filename, index=False, engine='openpyxl')

def get_timestamp():
    """获取当前时间戳"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def format_large_number(num, suffix=''):
    """格式化大数字"""
    if num >= 1000000:
        return f'{num/1000000:.2f}M{suffix}'
    elif num >= 1000:
        return f'{num/1000:.2f}K{suffix}'
    else:
        return f'{num:.2f}{suffix}'

def validate_dataframe(df, required_columns):
    """验证DataFrame是否包含必需列"""
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"缺少必需列: {missing_cols}")
    return True
