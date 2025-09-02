from abc import ABC, abstractmethod
import logging
from typing import Dict, Any

# 配置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class TTSBaseService(ABC):
    """
    TTS服务基类
    """
    
    def __init__(self):
        """
        初始化TTS服务
        """
        self.logger = logger
    
    @abstractmethod
    def synthesize_text(self, text: str, language: str = 'zh') -> Dict[str, Any]:
        """
        将文本合成为语音
        
        :param text: 要合成的文本
        :param language: 语言代码
        :return: 音频文件URL或数据
        """
        pass