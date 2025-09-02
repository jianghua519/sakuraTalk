# SakuraTalk 项目规划文档

## 1. 项目概述

SakuraTalk 是一个基于阿里云AI服务的日语对话练习小程序，以《标准日本语》教材为蓝本，为初学者提供沉浸式、可纠错的口语练习环境。该项目采用现代化架构，结合人工智能技术，为日语学习者打造智能化的语言练习平台。

## 2. 项目目标

1. 提供基于《标准日本语》教材的场景化日语对话练习
2. 实现AI驱动的实时对话响应和纠错功能
3. 支持多种学习场景（问候、购物、餐厅等）
4. 集成语音识别(STT)和语音合成(TTS)功能
5. 提供实时语法和发音纠错
6. 给出个性化学习建议和指导

## 3. 技术架构

### 3.1 整体架构

```
+-------------------+       +---------------------+
|                   |       |                     |
|     前端界面      |<----->|     后端服务          |
| (Web/HTML/CSS/JS) |       | (Python Flask)        |
|                   |       |                     |
+-------------------+       +-----------+---------+
                                          |
                     +-------------------v------------------+
                     |                                      |
                     |     AI服务层                         |
                     | (阿里云智能语音交互 + 通义千问)      |
                     |                                      |
                     +--------------------------------------+
```

### 3.2 技术选型

| 层级        | 技术选型                          | 说明                                                                 |
|-------------|-----------------------------------|----------------------------------------------------------------------|
| 前端        | HTML5/CSS3/JavaScript            | 使用Web Speech API实现浏览器端录音和播放功能                           |
| 后端框架    | Python Flask                     | 轻量级Web框架，适合API服务                                           |
| API调用     | DashScope SDK 1.23.9+            | 调用通义千问大语言模型                                               |
| 语音识别    | 阿里云智能语音交互 SDK 2.6.5      | 实时语音识别服务                                                     |
| 语音合成    | 阿里云智能语音交互 SDK 2.6.5      | 文本转语音服务                                                       |
| 环境管理    | python-dotenv 1.0.0             | 管理环境变量                                                         |
| 包管理      | pip 23.0+                       | 依赖管理                                                             |
| 构建工具    | setuptools 65.0+                | 项目打包                                                             |
| 文档        | Markdown                        | 项目文档                                                             |

### 3.3 API服务集成

#### 3.3.1 阿里云智能语音交互
- **语音识别 (STT)**: 使用Paraformer实时语音识别
- **语音合成 (TTS)**: 使用CosyVoice/Sambert语音合成
- **SDK版本**: 2.6.5
- **文档**: https://help.aliyun.com/document_detail/182053.html

#### 3.3.2 DashScope通义千问
- **大语言模型**: qwen-plus
- **语音对话模型**: Qwen-TTS
- **SDK版本**: 1.23.9+
- **文档**: https://help.aliyun.com/zh/model-studio/qwen-tts-realtime-python-sdk

## 4. 功能模块设计

### 4.1 核心模块

1. **用户界面模块**
   - 主页界面
   - 场景选择界面
   - 对话历史显示
   - 语音状态指示

2. **语音处理模块**
   - 语音识别(STT)：将用户语音转换为文本
   - 语音合成(TTS)：将AI回复转换为语音
   - 录音控制：浏览器端录音功能

3. **AI对话模块**
   - 智能对话：基于通义千问的自然语言处理
   - 语法纠错：检测并纠正用户日语语法错误
   - 学习建议：提供个性化学习指导

4. **场景管理模块**
   - 问候场景
   - 购物场景
   - 餐厅场景
   - 问路场景

5. **数据管理模块**
   - 用户学习进度跟踪
   - 对话历史记录
   - 错误统计分析

## 5. API接口设计

### 5.1 后端API接口

#### 5.1.1 对话相关
- **POST /api/chat**
  - 请求参数：{ "message": "用户输入" }
  - 响应参数：{ 
    "response": "AI回复",
    "pronunciation_score": 90,
    "correction": "纠正建议",
    "translation": "中文翻译"
  }

#### 5.1.2 语音相关
- **POST /api/speech_to_text**
  - 请求参数：音频数据
  - 响应参数：{ "text": "识别结果", "confidence": 0.95 }

- **POST /api/text_to_speech**
  - 请求参数：{ "text": "要合成的文本" }
  - 响应参数：{ "audio_url": "音频文件URL" }

#### 5.1.3 场景相关
- **GET /api/scenarios**
  - 获取支持的练习场景列表

- **POST /api/scenario**
  - 切换场景：{ "scenario": "greeting" }

## 6. 项目结构

```
sakuratalk/
├── app.py              # 应用主文件
├── config.py           # 配置文件
├── aliyun_service.py   # 阿里云服务接口
├── dashscope_service.py # DashScope服务接口
├── static/             # 静态资源文件
│   ├── styles.css      # 样式文件
│   └── app.js          # 前端JavaScript
├── templates/          # HTML模板
│   └── index.html      # 主页模板
├── requirements.txt    # 依赖列表
├── run.py              # 应用启动文件
└── .env                # 环境变量配置
```

## 7. 开发计划

### 7.1 第一阶段：基础架构搭建 (1周)
- 创建项目结构
- 配置开发环境
- 实现基本的Flask服务
- 创建前端基础界面

### 7.2 第二阶段：核心功能开发 (2周)
- 集成阿里云语音识别服务
- 集成阿里云语音合成服务
- 集成通义千问大语言模型
- 实现基本对话功能

### 7.3 第三阶段：场景化功能开发 (1周)
- 添加多场景支持
- 实现场景相关的对话逻辑
- 优化语音交互体验

### 7.4 第四阶段：测试与优化 (1周)
- 进行功能测试
- 优化UI交互
- 修复已知问题
- 完善文档

## 8. 部署方案

### 8.1 本地开发部署
- 使用Flask内置服务器
- 通过`python run.py`启动应用
- 访问`http://localhost:5000`

### 8.2 生产环境部署
- 使用Gunicorn作为WSGI服务器
- 使用Nginx进行反向代理
- 部署到阿里云ECS实例
- 使用阿里云SLB进行负载均衡

### 8.3 Docker部署
- 创建Docker镜像
- 使用Docker Compose管理服务
- 部署到阿里云Kubernetes服务

## 9. 安全与认证

- 使用HTTPS加密通信
- 对API密钥进行安全管理
- 使用环境变量存储敏感信息
- 实现API调用限流机制

## 10. 后续优化方向

1. 完善阿里云实时语音识别功能的实现
2. 增加发音评分功能
3. 添加更多学习场景
4. 实现用户学习进度跟踪
5. 增加多语言支持
6. 开发移动端应用
7. 添加用户账户系统
8. 实现对话历史回顾功能

## 11. 依赖库版本说明

```text
Flask==2.3.3
python-dotenv==1.0.0
requests==2.31.0
dashscope==1.23.9
websocket-client==1.6.1
```

## 12. 环境变量配置

```text
ACCESS_KEY_ID=your_access_key_id
ACCESS_KEY_SECRET=your_access_key_secret
DASHSCOPE_API_KEY=your_dashscope_api_key
NLS_APPKEY=your_nls_appkey
```

## 13. 运行说明

```bash
# 安装依赖
pip install -r requirements.txt

# 运行应用
python run.py

# 访问应用
http://localhost:5000
```