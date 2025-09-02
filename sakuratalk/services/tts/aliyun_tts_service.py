import json
import threading
import time
import dashscope
from dashscope import Generation
from dashscope.audio.asr import Recognition
import sys
import os
from typing import Dict, Any

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入配置
from ...config import Config
from ...exceptions import ServiceCallError
from .tts_base import TTSBaseService


class AliyunTTSService(TTSBaseService):
    """
    阿里云语音合成服务
    """
    def __init__(self):
        """
        初始化阿里云TTS服务
        """
        super().__init__()
        # 初始化DashScope
        dashscope.api_key = Config.DASHSCOPE_API_KEY
    
    def synthesize_text(self, text: str, language: str = 'zh') -> Dict[str, Any]:
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
                audio_path = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'audio')
                
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
                    raise ServiceCallError(f"语音合成失败: {response.message}")
                else:
                    raise ServiceCallError("语音合成失败: 未知错误")
                
        except Exception as e:
            # 出现错误时返回错误信息
            self.logger.error(f"语音合成错误: {str(e)}")
            return {
                'error': str(e)
            }