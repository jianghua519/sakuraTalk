import os
import sys

# 添加sakuratalk目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'sakuratalk'))

from sakuratalk.app import create_app
from sakuratalk.config import Config

# 创建应用实例
app = create_app()

def run_https():
    """启动HTTPS服务"""
    ssl_cert = Config.SSL_CERT
    ssl_key = Config.SSL_KEY
    if os.path.exists(ssl_cert) and os.path.exists(ssl_key):
        print("启动 HTTPS 服务...")
        app.run(debug=True, host='0.0.0.0', port=5050, ssl_context=(ssl_cert, ssl_key))
    else:
        raise FileNotFoundError(f"SSL证书或密钥文件缺失: {ssl_cert}, {ssl_key}")

def run_http():
    """启动HTTP服务"""
    print("启动 HTTP 服务...")
    app.run(debug=True, host='0.0.0.0', port=5050)

if __name__ == '__main__':
    try:
        if Config.USE_HTTPS:
            run_https()
        else:
            run_http()
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)