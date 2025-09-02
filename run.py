import os
import sys

# 添加sakuratalk目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'sakuratalk'))

from sakuratalk.app import create_app

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)