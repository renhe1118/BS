import pandas as pd
import numpy as np
from pathlib import Path
import logging
import chardet

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataProcessor:
    """数据处理类"""

    def __init__(self, file_path):
        """
        初始化数据处理器

        Args:
            file_path: Excel或CSV文件路径
        """
        self.file_path = file_path
        self.df = None
        self.original_shape = None

    @staticmethod
    def detect_encoding(file_path):
        """自动检测文件编码"""
        try:
            with open(file_path, 'rb') as f:
                result = chardet.detect(f.read())
                encoding = result.get('encoding', 'utf-8')
                logger.info(f"检测到文件编码: {encoding}")
                return encoding
        except Exception as e:
            logger.warning(f"编码检测失败: {str(e)}，使用GB2312")
            return 'gb2312'

    def load_data(self):
        """读取原始数据，自动检测格式"""
        try:
            logger.info(f"尝试加载数据: {self.file_path}")

            # 判断文件类型
            if self.file_path.endswith('.xlsx') or self.file_path.endswith('.xls'):
                # Excel文件
                logger.info("检测到Excel文件格式")
                self.df = pd.read_excel(self.file_path)
            else:
                # CSV文件
                encoding = self.detect_encoding(self.file_path)

                # 尝试用检测到的编码加载
                try:
                    self.df = pd.read_csv(self.file_path, encoding=encoding)
                except:
                    # 如果失败，尝试其他常见编码
                    for enc in ['gb2312', 'gbk', 'cp1252', 'latin-1', 'utf-8']:
                        try:
                            logger.info(f"尝试编码: {enc}")
                            self.df = pd.read_csv(self.file_path, encoding=enc)
                            logger.info(f"成功使用编码: {enc}")
                            break
                        except:
                            continue

            self.original_shape = self.df.shape
            logger.info(f"数据加载成功，形状: {self.original_shape}")
            logger.info(f"列名: {self.df.columns.tolist()}")
            return self.df

        except FileNotFoundError:
            logger.error(f"文件不存在: {self.file_path}")
            raise
        except Exception as e:
            logger.error(f"数据加载失败: {str(e)}")
            raise

    def check_data_quality(self):
        """检查数据质量"""
        logger.info("=== 数据质量检查 ===")
        logger.info(f"总行数: {len(self.df)}")
        logger.info(f"总列数: {len(self.df.columns)}")
        logger.info(f"\n缺失值统计:\n{self.df.isnull().sum()}")
        logger.info(f"\n数据类型:\n{self.df.dtypes}")

        return {
            'total_rows': len(self.df),
            'total_columns': len(self.df.columns),
            'missing_values': self.df.isnull().sum().to_dict(),
            'data_types': self.df.dtypes.to_dict()
        }

    def remove_duplicates(self):
        """去除重复数据"""
        initial_rows = len(self.df)
        self.df = self.df.drop_duplicates()
        removed_rows = initial_rows - len(self.df)
        logger.info(f"已去除 {removed_rows} 条重复数据")
        return self.df

    def standardize_columns(self):
        """标准化列名和数据格式"""
        # 重命名列为标准格式
        column_mapping = {
            '小区名称': '小区名称',
            '行政区': '行政区',
            '朝向': '朝向',
            '房屋配置': '房屋配置',
            '面积(㎡)': '面积(㎡)',
            '面积': '面积(㎡)',
            '总价(万)': '总价(万元)',
            '总价': '总价(万元)',
            '均价(平)': '单价(元/㎡)',
            '单价': '单价(元/㎡)',
            '楼层': '楼层',
            '建筑年份': '建筑年份',
            '周边': '周边',
            '小区地址': '小区地址'
        }

        # 重命名已存在的列
        rename_dict = {}
        for old_col, new_col in column_mapping.items():
            if old_col in self.df.columns:
                rename_dict[old_col] = new_col

        if rename_dict:
            self.df = self.df.rename(columns=rename_dict)

        logger.info("列名已标准化")
        return self.df

    def clean_numeric_data(self):
        """清洗数值数据"""
        try:
            # 清洗面积
            if '面积(㎡)' in self.df.columns:
                self.df['面积(㎡)'] = pd.to_numeric(
                    self.df['面积(㎡)'].astype(str).str.replace('㎡', '').str.strip(),
                    errors='coerce'
                )
                logger.info("面积字段已标准化")

            # 清洗总价
            if '总价(万元)' in self.df.columns:
                self.df['总价(万元)'] = pd.to_numeric(
                    self.df['总价(万元)'].astype(str).str.replace('万', '').str.strip(),
                    errors='coerce'
                )
                logger.info("总价字段已标准化")

            # 清洗单价
            if '单价(元/㎡)' in self.df.columns:
                self.df['单价(元/㎡)'] = pd.to_numeric(
                    self.df['单价(元/㎡)'].astype(str).str.replace('元/㎡', '').str.strip(),
                    errors='coerce'
                )
                logger.info("单价字段已标准化")

            # 如果单价为空但有面积和总价，计算单价
            if '单价(元/㎡)' in self.df.columns and '面积(㎡)' in self.df.columns and '总价(万元)' in self.df.columns:
                mask = self.df['单价(元/㎡)'].isnull()
                self.df.loc[mask, '单价(元/㎡)'] = (
                        self.df.loc[mask, '总价(万元)'] * 10000 / self.df.loc[mask, '面积(㎡)']
                ).round(2)
                logger.info("已由总价和面积计算缺失的单价")

        except Exception as e:
            logger.warning(f"清洗数值数据失败: {str(e)}")

    def clean_building_year(self):
        """清洗建筑年份"""
        try:
            if '建筑年份' in self.df.columns:
                # 提取年份数字
                self.df['建筑年份'] = pd.to_numeric(
                    self.df['建筑年份'].astype(str).str.extract('(\d{4})', expand=False),
                    errors='coerce'
                ).astype('Int64')
                logger.info("建筑年份字段已标准化")
        except Exception as e:
            logger.warning(f"清洗建筑年份字段失败: {str(e)}")

    def standardize_district(self):
        """标准化行政区名称"""
        try:
            if '行政区' in self.df.columns:
                self.df['行政区'] = self.df['行政区'].astype(str).str.strip()
                logger.info("行政区字段已标准化")
        except Exception as e:
            logger.warning(f"标准化行政区字段失败: {str(e)}")

    def clean_data(self):
        """执行完整数据清洗流程"""
        try:
            logger.info("开始数据清洗...")
            self.standardize_columns()
            self.remove_duplicates()
            self.clean_numeric_data()
            self.clean_building_year()
            self.standardize_district()

            # 删除完全为空的行
            self.df = self.df.dropna(how='all')

            logger.info("数据清洗完成！")
            logger.info(f"清洗后列名: {self.df.columns.tolist()}")
            return self.df
        except Exception as e:
            logger.error(f"数据清洗失败: {str(e)}")
            raise

    def handle_missing_values(self, strategy='drop'):
        """
        处理缺失值

        Args:
            strategy: 'drop' 删除, 'fill_mean' 填充平均值
        """
        try:
            # 必需的列
            required_cols = ['总价(万元)', '面积(㎡)', '行政区']
            existing_required = [col for col in required_cols if col in self.df.columns]

            if strategy == 'drop':
                initial_rows = len(self.df)
                self.df = self.df.dropna(subset=existing_required)
                removed_rows = initial_rows - len(self.df)
                logger.info(f"删除了 {removed_rows} 行包含缺失值的数据")
            elif strategy == 'fill_mean':
                numeric_cols = self.df.select_dtypes(include=[np.number]).columns
                for col in numeric_cols:
                    if col in self.df.columns:
                        self.df[col] = self.df[col].fillna(self.df[col].mean())

            logger.info(f"缺失值已处理: 使用 {strategy} 策略")
            return self.df
        except Exception as e:
            logger.warning(f"处理缺失值失败: {str(e)}")
            return self.df

    def save_processed_data(self, output_path):
        """保存处理后的数据"""
        try:
            self.df.to_csv(output_path, index=False, encoding='utf-8')
            logger.info(f"数据已保存至: {output_path}")
        except Exception as e:
            logger.error(f"保存数据失败: {str(e)}")

    def get_summary_stats(self):
        """获取数据摘要统计"""
        return self.df.describe().to_dict()