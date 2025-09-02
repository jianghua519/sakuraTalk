# SakuraTalk - 日语对话练习助手

SakuraTalk 是一个基于AI的日语对话练习Web应用，帮助用户练习日语口语。

## 功能特性

- AI对话练习
- 语音识别和文本转语音
- 发音评分
- 多场景练习（问候、购物、餐厅、问路）
- 支持多种LLM API（DashScope、OpenAI、Gemini、Ollama）
- 支持多种语音API（阿里云、本地STT/TTS）

## 环境要求

- Python 3.8+
- 阿里云API密钥（可选）
- DashScope API密钥（可选）
- OpenAI API密钥（可选）
- Gemini API密钥（可选）

## 安装步骤

1. 克隆项目代码
2. 安装依赖：`pip install -r requirements.txt`
3. 配置环境变量（见下方）

## 环境变量配置

在项目根目录创建 `.env` 文件，包含以下内容：

```
# 基础配置
ALIYUN_ACCESS_KEY_ID=your_aliyun_access_key_id
ALIYUN_ACCESS_KEY_SECRET=your_aliyun_access_key_secret
DASHSCOPE_API_KEY=your_dashscope_api_key

# LLM API选择 (可选: dashscope, openai, gemini, ollama)
LLM_PROVIDER=dashscope

# OpenAI配置（如果LLM_PROVIDER=openai）
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=https://api.openai.com/v1

# Gemini配置（如果LLM_PROVIDER=gemini）
GEMINI_API_KEY=your_gemini_api_key

# Ollama配置（如果LLM_PROVIDER=ollama）
OLLAMA_API_BASE=http://localhost:11434/api

# 语音服务配置
STT_PROVIDER=dashscope  # 可选: dashscope, local
TTS_PROVIDER=dashscope  # 可选: dashscope, local

# HTTPS配置（可选）
# USE_HTTPS=true
# SSL_CERT=path/to/your/cert.pem
# SSL_KEY=path/to/your/key.pem
```

## 运行应用

### HTTP模式（默认）

```bash
python run.py
```

访问地址：http://localhost:5050

### HTTPS模式

要启用HTTPS，需要先生成SSL证书和密钥文件。

#### 生成自签名证书

使用以下命令生成自签名证书（需要安装OpenSSL）：

```bash
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

#### 启用HTTPS

在 `.env` 文件中添加以下配置：

```
USE_HTTPS=true
```

然后运行应用：

```bash
python run.py
```

访问地址：https://localhost:5050

注意：如果使用自签名证书，浏览器可能会显示安全警告，可以选择继续访问。

## 自定义SSL证书路径

默认情况下，程序会在项目根目录查找 `cert.pem` 和 `key.pem` 文件。如果证书文件在其他位置，可以在 `.env` 文件中指定：

```
USE_HTTPS=true
SSL_CERT=path/to/your/cert.pem
SSL_KEY=path/to/your/key.pem
```

## 使用不同的LLM API

可以通过修改 `.env` 文件中的 `LLM_PROVIDER` 配置来切换不同的LLM API：

```
# 使用DashScope（通义千问）
LLM_PROVIDER=dashscope

# 使用OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key

# 使用Gemini
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key

# 使用Ollama（需要先运行Ollama服务）
LLM_PROVIDER=ollama
```

## 使用不同的语音API

可以通过修改 `.env` 文件中的 `STT_PROVIDER` 和 `TTS_PROVIDER` 配置来切换不同的语音API：

```
# 使用阿里云语音服务
STT_PROVIDER=dashscope
TTS_PROVIDER=dashscope

# 使用本地语音服务（需要安装额外依赖）
STT_PROVIDER=local
TTS_PROVIDER=local
```

注意：使用本地语音服务需要安装额外的依赖：
- Windows: `pip install pyttsx3 SpeechRecognition pyaudio`
- macOS: `pip install pyttsx3 SpeechRecognition` 和 `brew install portaudio`
- Linux: `pip install pyttsx3 SpeechRecognition` 和 `sudo apt-get install portaudio19-dev python3-pyaudio`

## 安装日语语音包

如果在使用本地TTS服务时遇到"未找到日语语音包，将使用系统默认语音"的提示，需要手动安装日语语音包：

### Windows系统

1. 打开"设置" -> "时间和语言" -> "语言" 
2. 点击"首选语言"下的"日语"（如果没有，点击"添加语言"并添加日语）
3. 点击日语，选择"选项"
4. 在"语音"部分，点击"添加语音包"并安装日语语音包
5. 安装完成后，可能需要重启系统

### macOS系统

macOS系统通常自带日语语音，如果没有，可以尝试以下步骤：

1. 打开"系统偏好设置" -> "辅助功能" -> "语音"
2. 点击"系统语音"下的"自定"
3. 在弹出的窗口中查找是否有日语语音，如果没有可以尝试添加

### Linux系统

在基于Debian的系统（如Ubuntu）上：

```bash
# 安装日语语音包
sudo apt-get install festival festvox-kallpc16k
sudo apt-get install espeak-ng espeak-ng-data

# 对于日语支持
sudo apt-get install festvox-hts
```

### 验证语音包安装

可以通过以下Python脚本验证是否成功安装日语语音包：

```python
import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')

for voice in voices:
    print(f"Voice ID: {voice.id}")
    print(f"Name: {voice.name}")
    print(f"Languages: {voice.languages}")
    print("---")

# 测试日语语音
japanese_text = "こんにちは、これはテストです。"
engine.say(japanese_text)
engine.runAndWait()
```

如果成功安装了日语语音包，应该能在输出中看到包含日语标识的语音，并且能够正确播放日语。