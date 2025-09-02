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
from config import Config

# 配置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class DashScopeService:
    """
    通义千问服务接口
    """
    def __init__(self):
        # 初始化DashScope API密钥
        dashscope.api_key = Config.DASHSCOPE_API_KEY
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_chat_response(self, user_input, conversation_history=None):
        """
        获取聊天响应
        :param user_input: 用户输入
        :param conversation_history: 对话历史
        :return: AI响应
        """
        try:
            # 构建提示词，设定场景为日语学习助手
            system_prompt = '''你是一个专业的日语学习助手，帮助用户练习日语对话。
请用日语回答用户的问题，回复要自然、友好。
同时，请提供以下额外信息帮助用户学习：
1. 平假名：提供日语回复的平假名形式
2. 中文翻译：提供刚才日语回复的中文翻译
3. 发音评分：对用户的表达进行评分(0-100分)
4. 下一句练习建议：提供下一句可以练习的日语句子以及平假名和中文意思

请严格按照以下JSON格式回复，不要添加其他内容：
{
    "japanese": "你的日语回复",
    "hiragana": "日语回复的平假名形式",
    "chinese": "日语回复的中文翻译",
    "pronunciation_score": 85,
    "next_suggestion": "建议练习的日语句子",
    "suggestion_hiragana": "建议句子的平假名",
    "suggestion_chinese": "建议句子的中文意思"
}'''

            messages = [
                {
                    'role': 'system',
                    'content': system_prompt
                }
            ]
            
            # 添加对话历史（如果有的话）
            if conversation_history:
                # 确保对话历史格式正确，只添加符合格式的对话条目
                for item in conversation_history:
                    if isinstance(item, dict) and 'role' in item and 'content' in item:
                        messages.append(item)
            
            # 添加当前用户输入（确保格式正确）
            if user_input:
                messages.append({
                    'role': 'user',
                    'content': str(user_input)
                })
            
            # 记录发送给模型的请求
            logger.info(f"Sending request to DashScope API with model qwen-plus")
            logger.info(f"Messages: {json.dumps(messages, ensure_ascii=False)}")
            
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
                logger.info(f"Received response from DashScope API: {ai_response}")
                
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
                error_msg = f"API调用失败: {response.message}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            logger.error(f"调用DashScope API时出错: {str(e)}")
            # 出现错误时返回错误信息
            return {
                'error': str(e)
            }
    
    def _parse_ai_response(self, response_text):
        """
        解析AI回复文本，提取日语、中文翻译、注音和评分
        :param response_text: AI回复的原始文本
        :return: 解析后的字典
        """
        # 此方法已不再使用，保留以避免破坏其他代码
        result = {}
        return result
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def correct_grammar(self, text):
        """
        语法纠错
        :param text: 需要纠错的文本
        :return: 纠错结果
        """
        try:
            # 构建语法纠错提示
            prompt = f"""
            请纠正以下日语文本中的语法错误：
            
            "{text}"
            
            请按以下格式回复：
            1. 原文：[用户输入的文本]
            2. 纠正后：[纠正后的文本]
            3. 错误说明：[指出具体错误及原因]
            4. 语法点：[相关的日语语法知识点]
            """
            
            messages = [
                {'role': 'system', 'content': '你是一个专业的日语语法纠正助手。'},
                {'role': 'user', 'content': prompt}
            ]
            
            # 记录发送给模型的请求
            logger.info(f"Sending grammar correction request to DashScope API with model qwen-plus")
            logger.info(f"Messages: {json.dumps(messages, ensure_ascii=False)}")
            
            # 调用通义千问API进行语法纠错
            response = Generation.call(
                model='qwen-plus',
                messages=messages,
                result_format='message'
            )
            
            if response.status_code == HTTPStatus.OK:
                correction_result = response.output.choices[0].message.content
                
                # 记录模型的响应
                logger.info(f"Received grammar correction response from DashScope API: {correction_result}")
                
                return {
                    'corrected_text': correction_result,
                    'errors': [],  # 在实际应用中可以解析错误详情
                    'suggestions': []
                }
            else:
                error_msg = f"语法纠错API调用失败: {response.message}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            logger.error(f"语法纠错时出错: {str(e)}")
            return {
                'error': str(e)
            }