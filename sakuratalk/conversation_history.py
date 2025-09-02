import json
from collections import deque
from typing import List, Dict, Any


class ConversationHistory:
    """
    对话历史管理类，用于存储和管理用户与AI助手的对话记录
    """
    def __init__(self, max_history: int = 10):
        """
        初始化对话历史管理器
        
        :param max_history: 最大历史记录数，默认为10
        """
        self.max_history = max_history
        self.history = deque(maxlen=max_history)
    
    def add_interaction(self, user_input: str, ai_response: str) -> None:
        """
        添加一次用户与AI的交互记录
        
        :param user_input: 用户输入
        :param ai_response: AI回复（仅包含日语回复）
        """
        interaction = {
            'user': user_input,
            'ai': ai_response
        }
        self.history.append(interaction)
    
    def get_history(self) -> List[Dict[str, str]]:
        """
        获取对话历史记录
        
        :return: 对话历史列表
        """
        return list(self.history)
    
    def get_history_for_llm(self) -> List[Dict[str, str]]:
        """
        获取用于LLM对话的格式化历史记录
        
        :return: 格式化的对话历史列表，适用于LLM API
        """
        formatted_history = []
        for interaction in self.history:
            # 添加用户消息
            formatted_history.append({
                'role': 'user',
                'content': interaction['user']
            })
            # 添加AI助手消息
            formatted_history.append({
                'role': 'assistant',
                'content': interaction['ai']
            })
        return formatted_history
    
    def clear_history(self) -> None:
        """
        清空对话历史
        """
        self.history.clear()
    
    def __len__(self) -> int:
        """
        返回当前历史记录数量
        """
        return len(self.history)
    
    def __str__(self) -> str:
        """
        字符串表示
        """
        return json.dumps(list(self.history), ensure_ascii=False, indent=2)