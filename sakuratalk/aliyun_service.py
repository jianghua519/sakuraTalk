import json
import threading
import time
import dashscope
from dashscope import Generation
from dashscope.audio.asr import Recognition
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入配置
from config import Config



class AliyunSTT:
    """
    阿里云语音识别服务
    """
    def __init__(self):
        # 初始化DashScope
        dashscope.api_key = Config.DASHSCOPE_API_KEY
    
    def recognize_voice(self, audio_file_path=None):
        """
        识别语音数据
        :param audio_file_path: 音频文件路径
        :return: 识别结果
        """
        try:
            # 使用DashScope的ASR功能进行语音识别
            if audio_file_path is None:
                # 如果没有提供音频文件路径，返回示例结果
                # 在实际应用中，这里应该处理真实的音频输入
                return {
                    'result': 'こんにちは、元気ですか？',
                    'confidence': 0.92
                }
            
            # 对于实际的音频文件，使用阿里云的语音识别服务
            # 创建Recognition实例
            recognition = Recognition(
                model='paraformer-realtime-v2',
                format='wav',
                sample_rate=16000,
                callback=None  # 简单场景下可以不使用回调
            )
            
            # 调用语音识别服务
            response = recognition.call(file=audio_file_path)
            
            # 检查响应状态
            if response.status_code == 200 and response.output:
                return {
                    'result': response.output.text,
                    'confidence': response.output.confidence
                }
            else:
                raise Exception(f"语音识别失败: {response.message}")
                
        except Exception as e:
            # 出现错误时返回错误信息
            print(f"语音识别错误: {str(e)}")
            return {
                'error': str(e)
            }

class AliyunTTS:
    """
    阿里云语音合成服务
    """
    def __init__(self):
        # 初始化DashScope
        dashscope.api_key = Config.DASHSCOPE_API_KEY
    
    def synthesize_text(self, text, language='zh'):
        """
        将文本合成为语音
        :param text: 要合成的文本
        :param language: 语言代码
        :return: 音频文件URL或数据
        """
        try:
            # 使用DashScope的TTS功能
            # 注意：实际部署时需要处理音频文件的存储和访问
            response = dashscope.audio.tts.SpeechSynthesizer.call(
                model='sambert-zhichu-v1',
                text=text,
                speech_rate=0,
                volume=50,
                output_format='wav'
            )
            
            # 检查响应是否成功并包含音频数据
            if response.get_audio_data() is not None:
                # 保存音频数据到文件
                audio_filename = f"synthesized_{int(time.time())}.wav"
                audio_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'audio')
                
                # 确保audio目录存在
                os.makedirs(audio_path, exist_ok=True)
                
                # 保存音频文件
                full_audio_path = os.path.join(audio_path, audio_filename)
                with open(full_audio_path, 'wb') as f:
                    f.write(response.get_audio_data())
                
                # 返回音频文件的URL
                audio_url = f'/static/audio/{audio_filename}'
                return {
                    'audio_url': audio_url,
                    'format': 'wav'
                }
            else:
                # 如果没有音频数据，尝试从response中获取错误信息
                if hasattr(response, 'message'):
                    raise Exception(f"语音合成失败: {response.message}")
                else:
                    raise Exception("语音合成失败: 未知错误")
                
        except Exception as e:
            # 出现错误时返回错误信息
            print(f"语音合成错误: {str(e)}")
            return {
                'error': str(e)
            }