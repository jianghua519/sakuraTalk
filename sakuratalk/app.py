import os
import sys
from flask import Flask, request, jsonify, render_template

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入自定义模块
from config import Config

# 根据配置导入相应的服务
# LLM服务
if Config.LLM_PROVIDER == 'dashscope':
    from dashscope_service import DashScopeService
    ai_service = DashScopeService()
elif Config.LLM_PROVIDER == 'openai':
    from openai_service import OpenAIService
    ai_service = OpenAIService()
elif Config.LLM_PROVIDER == 'gemini':
    from gemini_service import GeminiService
    ai_service = GeminiService()
elif Config.LLM_PROVIDER == 'ollama':
    from ollama_service import OllamaService
    ai_service = OllamaService()
else:
    from dashscope_service import DashScopeService
    ai_service = DashScopeService()

# STT服务
if Config.STT_PROVIDER == 'dashscope':
    from aliyun_service import AliyunSTT
    stt_service = AliyunSTT()
elif Config.STT_PROVIDER == 'local':
    from local_stt_service import LocalSTTService
    stt_service = LocalSTTService()
else:
    from aliyun_service import AliyunSTT
    stt_service = AliyunSTT()

# TTS服务
if Config.TTS_PROVIDER == 'dashscope':
    from aliyun_service import AliyunTTS
    tts_service = AliyunTTS()
elif Config.TTS_PROVIDER == 'local':
    from local_tts_service import LocalTTSService
    tts_service = LocalTTSService()
else:
    from aliyun_service import AliyunTTS
    tts_service = AliyunTTS()

def create_app():
    """
    创建Flask应用
    """
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'),
                static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'))
    
    # 加载配置
    app.config.from_object(Config)
    
    @app.route('/')
    def index():
        """
        主页
        """
        return render_template('index.html')
    
    @app.route('/api/chat', methods=['POST'])
    def chat():
        """
        处理聊天请求
        """
        try:
            data = request.get_json()
            user_message = data.get('message', '')
            
            # 调用配置的AI服务
            response = ai_service.get_chat_response(user_message)
            
            if 'error' in response:
                return jsonify({'error': response['error']}), 500
            
            # 构建返回结果，确保包含所有字段
            result = {
                'message': response['message'],
                'translation': response['translation'],
                'hiragana': response['hiragana'],
                'pronunciation_score': response['pronunciation_score'],
                'user_pronunciation_score': response['user_pronunciation_score'],
                'next_suggestion': response['next_suggestion'],
                'suggestion_hiragana': response['suggestion_hiragana'],
                'suggestion_translation': response['suggestion_translation']
            }
            
            return jsonify(result)
        except Exception as e:
            print(f"聊天处理错误: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/speech_to_text', methods=['POST'])
    def speech_to_text():
        """
        语音转文本
        """
        try:
            # 调用配置的STT服务
            response = stt_service.recognize_voice()
            
            if 'error' in response:
                return jsonify({'error': response['error']}), 500
                
            result = {
                'text': response['result'],
                'confidence': response['confidence']
            }
            
            return jsonify(result)
        except Exception as e:
            print(f"语音识别错误: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/text_to_speech', methods=['POST'])
    def text_to_speech():
        """
        文本转语音
        """
        try:
            data = request.get_json()
            text = data.get('text', '')
            
            # 调用配置的TTS服务
            response = tts_service.synthesize_text(text)
            
            if 'error' in response:
                return jsonify({'error': response['error']}), 500
                
            result = {
                'audio_url': response['audio_url'],
                'format': response['format']
            }
            
            return jsonify(result)
        except Exception as e:
            print(f"语音合成错误: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    return app