import sys
import os
import json
import re
import logging
import google.generativeai as genai
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

class GeminiService(LLMBaseService):
    """
    Gemini服务接口
    """
    def __init__(self):
        """
        初始化Gemini服务
        """
        super().__init__()
        # 初始化Gemini API密钥
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
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

            # 构建消息列表
            messages = []
            
            # 添加系统提示
            messages.append({
                'role': 'system',
                'content': system_prompt
            })
            
            # 添加对话历史提示
            if conversation_history and len(conversation_history) > 1:  # 确保有历史记录（除了系统提示）
                messages.append({
                    'role': 'system',
                    'content': '以下是你与用户的历史对话记录，按时间顺序排列（较早的记录在前）：'
                })
                # 添加实际的历史记录（跳过初始的系统提示）
                messages.extend(conversation_history[1:])
            
            # 构建完整的提示
            full_prompt = system_prompt
            
            # 添加历史记录说明和内容
            if len(messages) > 1:
                full_prompt += "\n\n以下是你与用户的历史对话记录，按时间顺序排列（较早的记录在前）："
                for msg in messages[2:]:  # 跳过系统提示和历史记录说明
                    if msg['role'] == 'user':
                        full_prompt += f"\n用户: {msg['content']}"
                    elif msg['role'] == 'assistant':
                        full_prompt += f"\n助手: {msg['content']}"
            
            full_prompt += f"\n\n当前用户输入: {user_input}\n请根据以上对话历史进行回复。"
            
            # 记录发送给模型的请求
            self._log_request([{'role': 'user', 'content': full_prompt}])
            
            # 调用Gemini API
            response = self.model.generate_content(full_prompt)
            
            # 提取AI回复
            ai_response = response.text
            
            # 记录模型的响应
            self._log_response(ai_response)
            
            # 尝试解析JSON格式的回复
            try:
                # 如果AI在JSON前后添加了其他内容，尝试提取JSON部分
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    json_text = json_match.group(0)
                    parsed_response = json.loads(json_text)
                else:
                    # 直接尝试解析整个回复
                    parsed_response = json.loads(ai_response)
            except json.JSONDecodeError:
                # 如果JSON解析失败，使用原始响应作为message字段
                parsed_response = {
                    'japanese': ai_response,
                    'hiragana': '暂无平假名',
                    'chinese': '暂无翻译',
                    'pronunciation_score': 85,
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
                'next_suggestion': parsed_response.get('next_suggestion', 'お元気ですか？'),
                'suggestion_hiragana': parsed_response.get('suggestion_hiragana', 'おげんきですか？'),
                'suggestion_translation': parsed_response.get('suggestion_chinese', '你好吗？')
            }
                
        except Exception as e:
            self.logger.error(f"调用Gemini API时出错: {str(e)}")
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
            
            full_prompt = "你是一个专业的日语语法纠正助手。" + prompt
            
            # 记录发送给模型的请求
            self._log_request([{'role': 'user', 'content': full_prompt}])
            
            # 调用Gemini API进行语法纠错
            response = self.model.generate_content(full_prompt)
            
            correction_result = response.text
            
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