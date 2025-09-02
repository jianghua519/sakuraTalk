from abc import ABC, abstractmethod
import logging
from typing import Dict, Any, Optional

# 配置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class STTBaseService(ABC):
    """
    STT服务基类
    """
    
    def __init__(self):
        """
        初始化STT服务
        """
        self.logger = logger
    
    @abstractmethod
    def recognize_voice(self, audio_file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        识别语音数据
        
        :param audio_file_path: 音频文件路径
        :return: 识别结果
        """
        pass