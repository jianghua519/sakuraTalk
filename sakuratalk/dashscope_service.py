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
    通义千问服务接口（日语学习助手）
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
            # 改进版系统提示词
            system_prompt = '''あなたはプロの日本語学習アシスタントです。  
ユーザーと自然で友好的な日本語会話をしながら、学習をサポートしてください。  

必ず以下の情報をJSON形式で返してください。他の文章は不要です。  

{
    "japanese": "AIの日本語回答（自然で友好的な会話文）",
    "hiragana": "日本語回答のひらがな表記",
    "chinese": "上記日本語の中国語翻訳",
    "pronunciation_score": 85,
    "improvement_tips": "ユーザーの発話に対する簡単な改善ポイント",
    "next_suggestion": "次に練習できる日本語の文",
    "suggestion_hiragana": "上記文のひらがな表記",
    "suggestion_chinese": "上記文の中国語訳"
}

追加ルール:  
1. 回答は自然な日本語会話にしてください。  
2. improvement_tips には簡潔に改善点を一つ示してください（例: 助詞の使い方、より自然な表現など）。  
3. next_suggestion はユーザーのレベルに応じて難易度を調整してください。  
4. すべての回答は上記JSON形式のみで返してください。
'''

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
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            logger.error(f"调用DashScope API时出错: {str(e)}")
            return {
                'error': str(e)
            }
    
    def _parse_ai_response(self, response_text):
        """
        解析AI回复文本，提取日语、中文翻译、注音和评分
        :param response_text: AI回复的原始文本
        :return: 解析后的字典
        """
        return {}
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def correct_grammar(self, text):
        """
        语法纠错
        :param text: 需要纠错的文本
        :return: 纠错结果
        """
        try:
            prompt = f"""
            以下の日文に文法の誤りがあれば修正してください：

            "{text}"

            回答フォーマット：
            1. 原文：[ユーザーの入力]
            2. 修正版：[修正後の文]
            3. エラー説明：[具体的な誤りと理由]
            4. 文法ポイント：[関連する文法知識]
            """
            
            messages = [
                {'role': 'system', 'content': 'あなたはプロの日本語文法訂正アシスタントです。'},
                {'role': 'user', 'content': prompt}
            ]
            
            logger.info(f"Sending grammar correction request to DashScope API with model qwen-plus")
            logger.info(f"Messages: {json.dumps(messages, ensure_ascii=False)}")
            
            response = Generation.call(
                model='qwen-plus',
                messages=messages,
                result_format='message'
            )
            
            if response.status_code == HTTPStatus.OK:
                correction_result = response.output.choices[0].message.content
                logger.info(f"Received grammar correction response from DashScope API: {correction_result}")
                
                return {
                    'corrected_text': correction_result,
                    'errors': [],
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
