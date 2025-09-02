import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

class Config:
    # 阿里云配置
    ACCESS_KEY_ID = os.environ.get('ACCESS_KEY_ID') or 'YOUR_ACCESS_KEY_ID'
    ACCESS_KEY_SECRET = os.environ.get('ACCESS_KEY_SECRET') or 'YOUR_ACCESS_KEY_SECRET'
    NLS_APPKEY = os.environ.get('NLS_APPKEY') or 'YOUR_NLS_APPKEY'

    # DashScope配置
    DASHSCOPE_API_KEY = os.environ.get('DASHSCOPE_API_KEY') or 'YOUR_DASHSCOPE_API_KEY'

    # HTTPS配置
    USE_HTTPS = os.environ.get('USE_HTTPS', 'false').lower() == 'true'
    SSL_CERT = os.environ.get('SSL_CERT', 'cert.pem')
    SSL_KEY = os.environ.get('SSL_KEY', 'key.pem')

    # API端点
    NLS_ENDPOINT = 'wss://nls-gateway.cn-shanghai.aliyuncs.com/ws/v1'
    DASHSCOPE_API_ENDPOINT = 'https://dashscope.aliyuncs.com/api/v1'