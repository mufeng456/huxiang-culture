import logging
from logging.handlers import RotatingFileHandler
import os


def setup_logging(app):
    """配置应用日志"""
    if not app.debug and not app.testing:
        # 创建logs目录
        if not os.path.exists('logs'):
            os.mkdir('logs')
            
        # 配置文件日志处理器
        file_handler = RotatingFileHandler(
            'logs/huxiang_culture.log', 
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('湖湘文化平台启动')