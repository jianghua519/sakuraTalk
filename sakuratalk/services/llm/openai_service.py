import sys
import os
import json
import re
import logging
import openai
from http import HTTPStatus
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import List, Dict, Any

from ...config import Config
from ...exceptions import ServiceCallError
from ...prompts import PromptManager
from .llm_base import LLMBaseService

# 配置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class OpenAIService(LLMBaseService):
    """
    OpenAI服务接口
    """
    def __init__(self):
        """
        初始化OpenAI API密钥和基础URL
        """
        super().__init__()
        self.client = openai.OpenAI(
            api_key=Config.OPENAI_API_KEY,
            base_url=Config.OPENAI_API_BASE
        )
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_chat_response(self, user_input: str, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        获取聊天响应
        :param user_input: 用户输入
        :param conversation_history: 对话历史
        :return: AI响应
        """
        try:
            # 使用集中管理的系统提示词
            system_prompt = PromptManager.JAPANESE_LEARNING_ASSISTANT
            
            messages = [
                {
                    'role': 'system',
                    'content': system_prompt
                }
            ]
            
            # 添加对话历史（如果有的话）
            if conversation_history:
                # 转换对话历史格式以匹配OpenAI API
                for msg in conversation_history:
                    messages.append({
                        'role': msg['role'],
                        'content': msg['content']
                    })
            
            # 添加当前用户输入
            messages.append({
                'role': 'user',
                'content': user_input
            })
            
            # 记录发送给模型的请求
            self._log_request(messages)
            
            # 调用OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7
            )
            
            # 提取AI回复
            ai_response = response.choices[0].message.content
            
            # 记录模型的响应
            self._log_response(ai_response)
            
            # 解析JSON响应
            try:
                # 尝试直接解析
                parsed_response = json.loads(ai_response)
            except json.JSONDecodeError:
                # 如果解析失败，尝试提取JSON内容
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    try:
                        parsed_response = json.loads(json_match.group(0))
                    except json.JSONDecodeError:
                        raise ValueError("无法解析模型返回的JSON内容")
                else:
                    raise ValueError("模型返回内容中未找到有效的JSON格式数据")
            
            # 返回标准化的响应格式
            return {
                'message': parsed_response.get('japanese', ''),
                'translation': parsed_response.get('chinese', '暂无翻译'),
                'hiragana': parsed_response.get('hiragana', '暂无平假名'),
                'pronunciation_score': parsed_response.get('pronunciation_score', 0),
                'user_pronunciation_score': parsed_response.get('user_pronunciation_score', 80),
                'next_suggestion': parsed_response.get('next_suggestion', ''),
                'suggestion_hiragana': parsed_response.get('suggestion_hiragana', ''),
                'suggestion_translation': parsed_response.get('suggestion_chinese', '')
            }
                
        except Exception as e:
            self.logger.error(f"调用OpenAI API时出错: {str(e)}")
            # 出现错误时返回错误信息
            return {
                'error': str(e)
            }
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def correct_grammar(self, text: str) -> Dict[str, Any]:
        """
        语法纠错
        :param text: 需要纠错的文本
        :return: 纠错结果
        """
        try:
            # 使用集中管理的语法纠错提示词
            prompt = PromptManager.JAPANESE_GRAMMAR_CORRECTION.format(text=text)
            
            messages = [
                {'role': 'system', 'content': '你是一个专业的日语语法纠正助手。'},
                {'role': 'user', 'content': prompt}
            ]
            
            # 记录发送给模型的请求
            self._log_request(messages)
            
            # 调用OpenAI API进行语法纠错
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.3
            )
            
            correction_result = response.choices[0].message.content
            
            # 记录模型的响应
            self._log_response(correction_result)
            
            return {
                'corrected_text': correction_result,
                'errors': [],  # 在实际应用中可以解析错误详情
                'suggestions': []
            }
                
        except Exception as e:
            self.logger.error(f"语法纠错时出错: {str(e)}")
            return {
                'error': str(e)
            }