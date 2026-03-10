"""
Celery 异步任务配置
用于定时任务和异步处理
"""

import os
from celery import Celery
from celery.schedules import crontab

# 设置Django settings模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('tourism')

# 从Django settings加载配置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现各个app中的tasks
app.autodiscover_tasks()

# ========================================
# 定时任务配置
# ========================================
app.conf.beat_schedule = {
    # 每30分钟更新天气数据
    'update-weather-data': {
        'task': 'apps.weather.tasks.update_weather_data',
        'schedule': crontab(minute='*/30'),
    },
    
    # 每15分钟更新客流数据
    'update-traffic-data': {
        'task': 'apps.monitoring.tasks.update_traffic_data',
        'schedule': crontab(minute='*/15'),
    },
    
    # 每小时检查预警状态
    'check-alert-status': {
        'task': 'apps.alerts.tasks.check_alert_expiry',
        'schedule': crontab(minute=0),
    },
    
    # 每天凌晨1点生成统计报表
    'generate-daily-report': {
        'task': 'apps.statistics.tasks.generate_daily_report',
        'schedule': crontab(hour=1, minute=0),
    },
}

# Celery配置
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 任务超时时间30分钟
)

@app.task(bind=True)
def debug_task(self):
    """测试任务"""
    print(f'Request: {self.request!r}')