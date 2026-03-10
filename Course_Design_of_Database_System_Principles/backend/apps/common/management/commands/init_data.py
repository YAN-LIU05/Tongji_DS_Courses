"""
初始化数据命令
python manage.py init_data
"""
from django.core.management.base import BaseCommand
from apps.common.models import Config


class Command(BaseCommand):
    help = '初始化系统配置数据'

    def handle(self, *args, **options):
        """执行命令"""
        self.stdout.write('开始初始化数据...')
        
        # 初始化系统配置
        self.init_configs()
        
        self.stdout.write(self.style.SUCCESS('数据初始化完成！'))

    def init_configs(self):
        """初始化系统配置"""
        configs = [
            {
                'key': 'system_name',
                'value': '文旅资源管理系统',
                'description': '系统名称',
                'category': 'system',
                'is_public': True
            },
            {
                'key': 'system_version',
                'value': '1.0.0',
                'description': '系统版本',
                'category': 'system',
                'is_public': True
            },
            {
                'key': 'default_page_size',
                'value': '20',
                'description': '默认分页大小',
                'category': 'system',
                'is_public': False
            },
            {
                'key': 'max_upload_size',
                'value': '10485760',
                'description': '最大上传文件大小（字节）',
                'category': 'system',
                'is_public': False
            },
        ]

        for config_data in configs:
            Config.objects.get_or_create(
                key=config_data['key'],
                defaults=config_data
            )
        
        self.stdout.write(f'  - 创建{len(configs)}个系统配置')