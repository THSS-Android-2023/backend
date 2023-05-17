# -*- coding: utf-8 -*-
"""
Flask 配置文件
"""


class Config(object):
    """
    通用配置
    """
    SECRET_KEY = 'woluanxiede'
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class DevelopmentConfig(Config):
    """
    开发模式配置
    """
    TYPE = 'dev'
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = "sqlite:///android-develop.db"

    JWT_KEY = '123456'


class ProductionConfig(Config):
    """
    生产模式配置
    """
    TYPE = 'prod'
    DEBUG = False

    SQLALCHEMY_DATABASE_URI = "sqlite:///android.db"

    JWT_KEY = '123456'


configs = {
    "default": DevelopmentConfig,
    "dev": DevelopmentConfig,
    "prod": ProductionConfig,
}