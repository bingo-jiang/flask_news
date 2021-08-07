class BaseConfig(object):
    DEBUG = True
    # SERVER_NAME='0.0.0.0:5000'
    SECRET_KEY = 'jaibhakfbasf'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True#自动提交数据库操作



class DevelopConfig(BaseConfig):
    DEBUG = False
    # 数据库配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:jjb000522@127.0.0.1:3306/flask_news'
    SQLALCHEMY_POOL_SIZE = 5
    SQLALCHEMY_POOL_TIMEOUT = 30
    SQLALCHEMY_POOL_RECYCLE = -1
    # Redis配置
    REDIS_HOST = '10.210.53.162'
    REDIS_PORT = 6379
    REDIS_PASSWORD = 'jjb000522'

    # session配置
    from redis import Redis
    from datetime import timedelta
    SESSION_TYPE = "redis"  # 设置session替换为redis
    SESSION_REDIS = Redis(host='10.210.53.162', port=6379, password='jjb000522')  # 连接Redis
    SESSION_USE_SIGNER = True  # 加密存储
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)  # 设置session的有效时长
    # 日志配置
    import logging
    LEVEL_NAME = logging.DEBUG


class ProductConfig(BaseConfig):
    DEBUG = False
    # 日志配置
    import logging
    LEVEL_NAME = logging.ERROR
    # 数据库配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:jjb000522@127.0.0.1:3306/flask_news'
    SQLALCHEMY_POOL_SIZE = 5
    SQLALCHEMY_POOL_TIMEOUT = 30
    SQLALCHEMY_POOL_RECYCLE = -1
    # Redis配置
    # REDIS_HOST = '10.210.53.162'
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    REDIS_PASSWORD = 'jjb000522'

    # session配置
    from redis import Redis
    from datetime import timedelta
    SESSION_TYPE = "redis"  # 设置session替换为redis
    # SESSION_REDIS = Redis(host='10.210.53.162', port=6379, password='jjb000522')  # 连接Redis
    SESSION_REDIS = Redis(host='127.0.0.1', port=6379, password='jjb000522')  # 连接Redis
    SESSION_USE_SIGNER = True  # 加密存储
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)  # 设置session的有效时长


class TestConfig(BaseConfig):
    pass


config_dict = {
    'develop': DevelopConfig,
    'product': ProductConfig,
    'test': TestConfig
}
