from .config import Config
from .exceptions import ServiceInitializationError

# LLM服务
from .services.llm.dashscope_service import DashScopeService
from .services.llm.openai_service import OpenAIService
from .services.llm.gemini_service import GeminiService
from .services.llm.ollama_service import OllamaService

# STT服务
from .services.stt.aliyun_stt_service import AliyunSTTService
from .services.stt.local_stt_service import LocalSTTService

# TTS服务
from .services.tts.aliyun_tts_service import AliyunTTSService
from .services.tts.local_tts_service import LocalTTSService


class ServiceFactory:
    """
    服务工厂类，用于创建各种服务实例
    """
    
    @staticmethod
    def create_llm_service():
        """
        创建LLM服务实例
        """
        provider = Config.LLM_PROVIDER

        service_map = {
            'dashscope': DashScopeService,
            'openai': OpenAIService,
            'gemini': GeminiService,
            'ollama': OllamaService
        }

        service_class = service_map.get(provider, DashScopeService)
        return service_class()
    
    @staticmethod
    def create_stt_service():
        """
        创建STT服务实例
        """
        provider = Config.STT_PROVIDER

        service_map = {
            'dashscope': AliyunSTTService,
            'local': LocalSTTService
        }

        service_class = service_map.get(provider, AliyunSTTService)
        return service_class()
    
    @staticmethod
    def create_tts_service():
        """
        创建TTS服务实例
        """
        provider = Config.TTS_PROVIDER
        
        if provider == 'dashscope':
            return AliyunTTSService()
        elif provider == 'local':
            return LocalTTSService()
        else:
            # 默认使用阿里云
            return AliyunTTSService()