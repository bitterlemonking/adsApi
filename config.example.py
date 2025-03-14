"""
配置文件示例
复制此文件为config.py并填入您的Google Ads API凭据
"""

# Flask应用配置
DEBUG = True
SECRET_KEY = 'your-secret-key'

# Google Ads API配置
GOOGLE_ADS = {
    'developer_token': 'YOUR_DEVELOPER_TOKEN',
    'client_id': 'YOUR_CLIENT_ID',
    'client_secret': 'YOUR_CLIENT_SECRET',
    'refresh_token': 'YOUR_REFRESH_TOKEN',
    'login_customer_id': 'YOUR_CUSTOMER_ID_WITHOUT_DASHES',  # 可选
    'use_proto_plus': True  # 使用Proto Plus库进行序列化/反序列化
}

# 应用配置
DEFAULT_COUNTRY = 'US'  # 默认国家
CACHE_TIMEOUT = 3600  # 缓存超时时间（秒） 