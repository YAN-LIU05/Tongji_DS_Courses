from django.apps import AppConfig


class CommonConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.common'
    verbose_name = '公共工具'
    
    def ready(self):
        """应用就绪时执行"""
        # 导入信号处理器（如果有的话）
        # import apps.common.signals
        pass