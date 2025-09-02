import json
import threading
import time
import dashscope
from dashscope import Generation
from dashscope.audio.asr import Recognition
import sys
import os
from typing import Dict, Any, Optional

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入配置
from ...config import Config
from ...exceptions import ServiceCallError
from .stt_base import STTBaseService


class AliyunSTTService(STTBaseService):
    """
    阿里云语音识别服务
    """
    def __init__(self):
        """
        初始化阿里云STT服务
        """
        super().__init__()
        # 初始化DashScope
        dashscope.api_key = Config.DASHSCOPE_API_KEY
    
    def recognize_voice(self, audio_file_path: Optional[str] = None) -> Dict[str, Any]:
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
                raise ServiceCallError(f"语音识别失败: {response.message}")
                
        except Exception as e:
            # 出现错误时返回错误信息
            self.logger.error(f"语音识别错误: {str(e)}")
            return {
                'error': str(e)
            }