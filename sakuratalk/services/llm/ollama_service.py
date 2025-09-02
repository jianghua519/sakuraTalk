import sys
import os
import json
import re
import logging
import requests
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

class OllamaService(LLMBaseService):
    """
    Ollama服务接口
    """
    def __init__(self):
        """
        初始化Ollama服务
        """
        super().__init__()
        # 初始化Ollama API基础URL
        self.api_base = Config.OLLAMA_API_BASE
        self.model = "gemma3:12b"
    
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

            # 构建消息列表
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
            request_data = {
                "model": self.model,
                "messages": messages,
                "stream": False
            }
            self._log_request(messages)
            
            # 调用Ollama API
            response = requests.post(
                f"{self.api_base}/chat",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['message']['content']
                
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
            else:
                error_msg = f"Ollama API调用失败: {response.text}"
                self.logger.error(error_msg)
                raise ServiceCallError(error_msg)
                
        except Exception as e:
            self.logger.error(f"调用Ollama API时出错: {str(e)}")
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
            
            # 记录发送给模型的请求
            request_data = {
                "model": self.model,
                "prompt": "你是一个专业的日语语法纠正助手。" + prompt,
                "stream": False
            }
            self._log_request([{'role': 'user', 'content': request_data['prompt']}])
            
            # 调用Ollama API进行语法纠错
            response = requests.post(
                f"{self.api_base}/generate",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                correction_result = result['response']
                
                # 记录模型的响应
                self._log_response(correction_result)
                
                return {
                    'corrected_text': correction_result,
                    'errors': [],  # 在实际应用中可以解析错误详情
                    'suggestions': []
                }
            else:
                error_msg = f"Ollama语法纠错API调用失败: {response.text}"
                self.logger.error(error_msg)
                raise ServiceCallError(error_msg)
                
        except Exception as e:
            self.logger.error(f"语法纠错时出错: {str(e)}")
            return {
                'error': str(e)
            }