import os
import sys

# 添加sakuratalk目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'sakuratalk'))

from sakuratalk.app import create_app
from sakuratalk.config import Config

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    # 检查是否需要启用HTTPS
    use_https = Config.USE_HTTPS
    
    if use_https:
        # 获取SSL证书和密钥路径
        ssl_cert = Config.SSL_CERT
        ssl_key = Config.SSL_KEY
        
        # 检查证书文件是否存在
        if os.path.exists(ssl_cert) and os.path.exists(ssl_key):
            # 启用HTTPS
            app.run(debug=True, host='0.0.0.0', port=5050, 
                   ssl_context=(ssl_cert, ssl_key))
        else:
            print("警告: SSL证书或密钥文件未找到，使用HTTP运行")
            app.run(debug=True, host='0.0.0.0', port=5050)
    else:
        # 默认HTTP运行
        app.run(debug=True, host='0.0.0.0', port=5050)