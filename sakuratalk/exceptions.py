class SakuraTalkException(Exception):
    """SakuraTalk基础异常类"""
    pass

class ServiceInitializationError(SakuraTalkException):
    """服务初始化异常"""
    pass

class ServiceCallError(SakuraTalkException):
    """服务调用异常"""
    pass

class ConfigurationError(SakuraTalkException):
    """配置异常"""
    pass

class AudioProcessingError(SakuraTalkException):
    """音频处理异常"""
    pass