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

    # OpenAI配置
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY') or 'YOUR_OPENAI_API_KEY'
    OPENAI_API_BASE = os.environ.get('OPENAI_API_BASE') or 'https://api.openai.com/v1'

    # Gemini配置
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or 'YOUR_GEMINI_API_KEY'

    # Ollama配置
    OLLAMA_API_BASE = os.environ.get('OLLAMA_API_BASE') or 'http://localhost:11434/api'

    # 选择使用的API
    LLM_PROVIDER = os.environ.get('LLM_PROVIDER') or 'dashscope'  # 可选: dashscope, openai, gemini, ollama
    
    # 语音服务配置
    STT_PROVIDER = os.environ.get('STT_PROVIDER') or 'dashscope'  # 可选: dashscope, openai, gemini, local
    TTS_PROVIDER = os.environ.get('TTS_PROVIDER') or 'dashscope'  # 可选: dashscope, openai, gemini, local

    # HTTPS配置
    USE_HTTPS = os.environ.get('USE_HTTPS', 'false').lower() == 'true'
    SSL_CERT = os.environ.get('SSL_CERT', 'cert.pem')
    SSL_KEY = os.environ.get('SSL_KEY', 'key.pem')

    # API端点
    NLS_ENDPOINT = 'wss://nls-gateway.cn-shanghai.aliyuncs.com/ws/v1'
    DASHSCOPE_API_ENDPOINT = 'https://dashscope.aliyuncs.com/api/v1'