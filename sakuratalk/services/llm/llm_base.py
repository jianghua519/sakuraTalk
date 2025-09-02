from abc import ABC, abstractmethod
import logging
from typing import List, Dict, Any

# 配置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class LLMBaseService(ABC):
    """
    LLM服务基类
    """
    
    def __init__(self):
        """
        初始化LLM服务
        """
        self.logger = logger
    
    @abstractmethod
    def get_chat_response(self, user_input: str, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        获取聊天响应
        
        :param user_input: 用户输入
        :param conversation_history: 对话历史
        :return: AI响应
        """
        pass
    
    @abstractmethod
    def correct_grammar(self, text: str) -> Dict[str, Any]:
        """
        语法纠错
        
        :param text: 需要纠错的文本
        :return: 纠错结果
        """
        pass
    
    def _log_request(self, messages: List[Dict[str, str]]) -> None:
        """
        记录发送给模型的请求
        
        :param messages: 发送给模型的消息
        """
        self.logger.info(f"Sending request to LLM API")
        self.logger.info(f"Messages: {messages}")
    
    def _log_response(self, response_text: str) -> None:
        """
        记录模型的响应
        
        :param response_text: 从模型接收的响应
        """
        self.logger.info(f"Received response from LLM API: {response_text}")