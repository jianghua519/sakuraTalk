import sys
import os
import time
import pyttsx3
from typing import Dict, Any

from .tts_base import TTSBaseService


class LocalTTSService(TTSBaseService):
    """
    本地文本转语音服务，优化语速与音色（pitch）
    """
    def __init__(self):
        """
        初始化本地TTS服务
        """
        super().__init__()
        self.engine = pyttsx3.init()
        # 加快语速，例如设置为 240
        self.engine.setProperty('rate', 300)
        # 最大音量
        self.engine.setProperty('volume', 1.0)
        self._set_japanese_voice()

    def _set_japanese_voice(self):
        """
        设置日语语音
        """
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if 'japanese' in voice.name.lower() or 'jp' in voice.id.lower():
                self.engine.setProperty('voice', voice.id)
                self.logger.info(f"已找到并设置日语语音: {voice.name}")
                break
        else:
            self.logger.warning("未找到日语语音包，将使用系统默认语音。")

    def synthesize_text(self, text: str, language: str = 'ja') -> Dict[str, Any]:
        """
        合成语音并保存
        :param text: 要合成的文本
        :param language: 语言代码
        :return: 音频文件信息
        """
        try:
            audio_filename = f"local_synth_{int(time.time())}.wav"
            audio_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'static', 'audio')
            os.makedirs(audio_path, exist_ok=True)
            full_audio_path = os.path.join(audio_path, audio_filename)

            self.engine.save_to_file(text, full_audio_path)
            self.engine.runAndWait()

            audio_url = f'/static/audio/{audio_filename}'
            self.logger.info(f"语音合成成功: {full_audio_path}")
            return {'audio_url': audio_url, 'format': 'wav'}

        except Exception as e:
            self.logger.error(f"本地语音合成错误: {str(e)}")
            return {'error': str(e)}