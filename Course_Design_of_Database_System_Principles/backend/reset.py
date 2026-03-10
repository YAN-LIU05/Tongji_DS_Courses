"""
重置数据库脚本
"""
import os
import sys
import django
from pathlib import Path

# 设置 Django 环境
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command
from django.conf import settings
import pymysql

def reset_database():
    """重置数据库"""
    
    # 获取数据库配置
    db_config = settings.DATABASES['default']
    db_name = db_config['NAME']
    db_user = db_config['USER']
    db_password = db_config['PASSWORD']
    db_host = db_config['HOST']
    db_port = int(db_config['PORT'])
    
    print(f"🔧 正在重置数据库: {db_name}")
    
    try:
        # 连接 MySQL（不指定数据库）
        connection = pymysql.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        # 删除数据库
        print(f"🗑️  删除数据库: {db_name}")
        cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
        
        # 创建数据库
        print(f"📦 创建数据库: {db_name}")
        cursor.execute(
            f"CREATE DATABASE {db_name} "
            f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        
        cursor.close()
        connection.close()
        
        print("✅ 数据库重置成功")
        
        # 删除迁移文件
        print("🧹 清理迁移文件...")
        apps_dir = Path('apps')
        for migration_file in apps_dir.rglob('0*.py'):
            migration_file.unlink()
            print(f"  删除: {migration_file}")
        
        print("✅ 迁移文件清理完成")
        
        # 重新生成迁移
        print("📝 生成迁移文件...")
        call_command('makemigrations')
        
        # 执行迁移
        print("🚀 执行迁移...")
        call_command('migrate')
        
        print("\n🎉 数据库重置完成！")
        print("\n下一步：创建超级用户")
        print("  python manage.py createsuperuser")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False
    
    return True

if __name__ == '__main__':
    reset_database()