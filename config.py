import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """基础配置"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    DEBUG = os.getenv('DEBUG', False)

    # 数据路径
    RAW_DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'raw')
    PROCESSED_DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'processed')

    # 可视化输出路径
    CHARTS_OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'static', 'charts')

    # Flask配置
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}