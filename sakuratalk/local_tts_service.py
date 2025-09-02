import sys
import os
import time
import pyttsx3
from config import Config

class LocalTTSService:
    """
    本地文本转语音服务（使用pyttsx3库）
    """
    def __init__(self):
        self.engine = pyttsx3.init()
        # 设置日语语音（如果可用）
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if 'japanese' in voice.name.lower() or 'jp' in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
    
    def synthesize_text(self, text, language='ja'):
        """
        将文本合成为语音
        :param text: 要合成的文本
        :param language: 语言代码
        :return: 音频文件信息
        """
        try:
            # 生成音频文件名
            audio_filename = f"local_synthesized_{int(time.time())}.wav"
            audio_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'audio')
            
            # 确保audio目录存在
            os.makedirs(audio_path, exist_ok=True)
            
            # 保存音频文件的完整路径
            full_audio_path = os.path.join(audio_path, audio_filename)
            
            # 设置语音参数
            if language == 'ja':
                # 尝试设置日语参数
                self.engine.setProperty('rate', 150)  # 语速
                self.engine.setProperty('volume', 0.9)  # 音量
            
            # 保存到文件
            self.engine.save_to_file(text, full_audio_path)
            self.engine.runAndWait()
            
            # 返回音频文件的URL
            audio_url = f'/static/audio/{audio_filename}'
            return {
                'audio_url': audio_url,
                'format': 'wav'
            }
                
        except Exception as e:
            # 出现错误时返回错误信息
            print(f"本地语音合成错误: {str(e)}")
            return {
                'error': str(e)
            }