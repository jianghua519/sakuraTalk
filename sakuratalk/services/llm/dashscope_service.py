import sys
import os
import json
import re
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import dashscope
from dashscope import Generation
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

class DashScopeService(LLMBaseService):
    """
    通义千问服务接口（日语学习助手）
    """
    def __init__(self):
        """
        初始化DashScope服务
        """
        super().__init__()
        # 初始化DashScope API密钥
        dashscope.api_key = Config.DASHSCOPE_API_KEY
    
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
            system_prompt = PromptManager.JAPANESE_LEARNING_ASSISTANT_JA

            messages = [
                {
                    'role': 'system',
                    'content': system_prompt
                }
            ]
            
            # 添加对话历史（如果有的话）
            if conversation_history:
                messages.extend(conversation_history)
            
            # 添加当前用户输入
            messages.append({
                'role': 'user',
                'content': user_input
            })
            
            # 记录发送给模型的请求
            self._log_request(messages)
            
            # 调用通义千问API
            response = Generation.call(
                model='qwen-plus',
                messages=messages,
                result_format='message'  # 设置结果格式为message
            )
            
            if response.status_code == HTTPStatus.OK:
                # 提取AI回复
                ai_response = response.output.choices[0].message.content
                
                # 记录模型的响应
                self._log_response(ai_response)
                
                # 尝试解析JSON格式的回复
                try:
                    json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                    if json_match:
                        json_text = json_match.group(0)
                        parsed_response = json.loads(json_text)
                    else:
                        parsed_response = json.loads(ai_response)
                except json.JSONDecodeError:
                    parsed_response = {
                        'japanese': ai_response,
                        'hiragana': '暂无平假名',
                        'chinese': '暂无翻译',
                        'pronunciation_score': 85,
                        'improvement_tips': '暂无改进建议',
                        'next_suggestion': 'お元気ですか？',
                        'suggestion_hiragana': 'おげんきですか？',
                        'suggestion_chinese': '你好吗？'
                    }
                
                # 确保所有字段都有默认值
                return {
                    'message': parsed_response.get('japanese'),
                    'translation': parsed_response.get('chinese', '暂无翻译'),
                    'hiragana': parsed_response.get('hiragana', '暂无平假名'),
                    'pronunciation_score': parsed_response.get('pronunciation_score', 85),
                    'user_pronunciation_score': 80,  # 默认用户发音评分
                    'improvement_tips': parsed_response.get('improvement_tips', '暂无改进建议'),
                    'next_suggestion': parsed_response.get('next_suggestion', 'お元気ですか？'),
                    'suggestion_hiragana': parsed_response.get('suggestion_hiragana', 'おげんきですか？'),
                    'suggestion_translation': parsed_response.get('suggestion_chinese', '你好吗？')
                }
            else:
                error_msg = f"API调用失败: {response.message}"
                self.logger.error(error_msg)
                raise ServiceCallError(error_msg)
                
        except Exception as e:
            self.logger.error(f"调用DashScope API时出错: {str(e)}")
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
            prompt = PromptManager.JAPANESE_GRAMMAR_CORRECTION_JA.format(text=text)
            
            messages = [
                {'role': 'system', 'content': 'あなたはプロの日本語文法訂正アシスタントです。'},
                {'role': 'user', 'content': prompt}
            ]
            
            self._log_request(messages)
            
            response = Generation.call(
                model='qwen-plus',
                messages=messages,
                result_format='message'
            )
            
            if response.status_code == HTTPStatus.OK:
                correction_result = response.output.choices[0].message.content
                self._log_response(correction_result)
                
                return {
                    'corrected_text': correction_result,
                    'errors': [],
                    'suggestions': []
                }
            else:
                error_msg = f"语法纠错API调用失败: {response.message}"
                self.logger.error(error_msg)
                raise ServiceCallError(error_msg)
                
        except Exception as e:
            self.logger.error(f"语法纠错时出错: {str(e)}")
            return {
                'error': str(e)
            }