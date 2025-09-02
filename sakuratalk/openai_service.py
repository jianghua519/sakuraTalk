import sys
import os
import json
import re
import openai
from http import HTTPStatus
from tenacity import retry, stop_after_attempt, wait_exponential
from config import Config

class OpenAIService:
    """
    OpenAI服务接口
    """
    def __init__(self):
        # 初始化OpenAI API密钥和基础URL
        self.client = openai.OpenAI(
            api_key=Config.OPENAI_API_KEY,
            base_url=Config.OPENAI_API_BASE
        )
    
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
            
            # 调用OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7
            )
            
            # 提取AI回复
            ai_response = response.choices[0].message.content
            
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
            print(f"调用OpenAI API时出错: {str(e)}")
            # 出现错误时返回错误信息
            return {
                'error': str(e)
            }
    
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
            
            # 调用OpenAI API进行语法纠错
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.3
            )
            
            correction_result = response.choices[0].message.content
            
            return {
                'corrected_text': correction_result,
                'errors': [],  # 在实际应用中可以解析错误详情
                'suggestions': []
            }
                
        except Exception as e:
            print(f"语法纠错时出错: {str(e)}")
            return {
                'error': str(e)
            }