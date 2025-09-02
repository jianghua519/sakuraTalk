import sys
import os
import time
import pyttsx3

class LocalTTSService:
    """
    本地文本转语音服务，优化语速与音色（pitch）
    """
    def __init__(self):
        self.engine = pyttsx3.init()
        # 加快语速，例如设置为 240
        self.engine.setProperty('rate', 300)
        # 最大音量
        self.engine.setProperty('volume', 1.0)
        self._set_japanese_voice()

    def _set_japanese_voice(self):
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if 'japanese' in voice.name.lower() or 'jp' in voice.id.lower():
                self.engine.setProperty('voice', voice.id)
                print(f"已找到并设置日语语音: {voice.name}")
                break
        else:
            print("未找到日语语音包，将使用系统默认语音。")

    def synthesize_text(self, text, language='ja', pitch_percent=0):
        """
        合成语音并保存，同时可调整 pitch（仅在支持 SSML 引擎上有效）
        :param pitch_percent: 音高调整百分比，如 +20 或 -10
        """
        try:
            audio_filename = f"local_synth_{int(time.time())}.wav"
            audio_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'audio')
            os.makedirs(audio_path, exist_ok=True)
            full_audio_path = os.path.join(audio_path, audio_filename)

            # 如果 pitch_percent 参数非 0，则使用 SSML 标签包装文本
            if pitch_percent:
                text = f'<pitch middle="{pitch_percent:+d}%">{text}</pitch>'

            self.engine.save_to_file(text, full_audio_path)
            self.engine.runAndWait()

            audio_url = f'/static/audio/{audio_filename}'
            print(f"语音合成成功: {full_audio_path}")
            return {'audio_url': audio_url, 'format': 'wav'}

        except Exception as e:
            print(f"本地语音合成错误: {str(e)}")
            return {'error': str(e)}
