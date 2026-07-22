#!/usr/bin/env python
"""
后端测试脚本
快速验证Django项目是否能正常运行
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command
from django.db import connection
from django.core.cache import cache


def print_section(title):
    """打印分节标题"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def test_database():
    """测试数据库连接"""
    print_section("🗄️  测试数据库连接")
    try:
        connection.ensure_connection()
        print("✅ 数据库连接成功")
        print(f"   引擎: {connection.settings_dict['ENGINE']}")
        print(f"   数据库: {connection.settings_dict['NAME']}")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False


def test_cache():
    """测试缓存"""
    print_section("💾 测试缓存系统")
    try:
        cache.set('test_key', 'test_value', 30)
        value = cache.get('test_key')
        if value == 'test_value':
            print("✅ 缓存系统正常")
            return True
        else:
            print("❌ 缓存读取失败")
            return False
    except Exception as e:
        print(f"❌ 缓存系统错误: {e}")
        return False


def test_migrations():
    """测试数据库迁移"""
    print_section("🔄 创建数据库迁移")
    try:
        # 创建迁移
        call_command('makemigrations', '--noinput', verbosity=0)
        print("✅ 迁移文件创建成功")
        
        # 执行迁移
        print("\n执行数据库迁移...")
        call_command('migrate', '--noinput', verbosity=1)
        print("✅ 数据库迁移成功")
        return True
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        return False


def test_models():
    """测试模型创建"""
    print_section("📦 测试模型操作")
    try:
        from apps.common.models import Config
        
        # 创建配置
        config = Config.objects.create(
            key='test_config',
            value='test_value',
            description='测试配置',
            category='test',
            is_public=True
        )
        print(f"✅ 创建配置成功: {config}")
        
        # 查询配置
        found = Config.objects.get(key='test_config')
        print(f"✅ 查询配置成功: {found.value}")
        
        # 更新配置
        found.value = 'updated_value'
        found.save()
        print(f"✅ 更新配置成功: {found.value}")
        
        # 软删除
        found.delete()
        print(f"✅ 软删除成功: is_deleted={found.is_deleted}")
        
        # 清理
        found.hard_delete()
        print("✅ 清理测试数据完成")
        
        return True
    except Exception as e:
        print(f"❌ 模型测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_admin():
    """测试管理员创建"""
    print_section("👤 创建测试超级用户")
    try:
        from django.contrib.auth.models import User
        
        # 检查是否已存在
        if User.objects.filter(username='admin').exists():
            print("ℹ️  超级用户 'admin' 已存在")
            user = User.objects.get(username='admin')
        else:
            # 创建超级用户
            user = User.objects.create_superuser(
                username='admin',
                email='admin@tourism.com',
                password='admin123456'
            )
            print("✅ 超级用户创建成功")
        
        print(f"   用户名: {user.username}")
        print(f"   邮箱: {user.email}")
        print(f"   密码: admin123456")
        return True
    except Exception as e:
        print(f"❌ 创建超级用户失败: {e}")
        return False


def test_urls():
    """测试URL配置"""
    print_section("🌐 测试URL配置")
    try:
        from django.urls import get_resolver
        
        resolver = get_resolver()
        url_patterns = resolver.url_patterns
        
        print(f"✅ URL配置加载成功")
        print(f"   已注册路由数量: {len(url_patterns)}")
        
        # 打印部分路由
        print("\n   部分路由列表:")
        for pattern in url_patterns[:5]:
            print(f"   - {pattern}")
        
        return True
    except Exception as e:
        print(f"❌ URL配置测试失败: {e}")
        return False


def test_import_apps():
    """测试应用导入"""
    print_section("📱 测试应用模块导入")
    
    modules = [
        'apps.common.models',
        'apps.common.serializers',
        'apps.common.views',
        'apps.common.permissions',
        'apps.common.utils',
    ]
    
    success_count = 0
    for module_name in modules:
        try:
            __import__(module_name)
            print(f"✅ {module_name}")
            success_count += 1
        except Exception as e:
            print(f"❌ {module_name}: {e}")
    
    print(f"\n导入成功: {success_count}/{len(modules)}")
    return success_count == len(modules)


def run_all_tests():
    """运行所有测试"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "后端系统测试开始" + " "*27 + "║")
    print("╚" + "="*58 + "╝")
    
    tests = [
        ("导入测试", test_import_apps),
        ("数据库连接", test_database),
        ("缓存系统", test_cache),
        ("数据库迁移", test_migrations),
        ("模型操作", test_models),
        ("URL配置", test_urls),
        ("超级用户", test_admin),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ {name}测试异常: {e}")
            results[name] = False
    
    # 打印总结
    print_section("📊 测试结果汇总")
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n" + "🎉 " * 20)
        print("🎉 所有测试通过！后端系统运行正常！")
        print("🎉 " * 20)
        print("\n✨ 下一步:")
        print("   1. 运行开发服务器: python manage.py runserver")
        print("   2. 访问管理后台: http://127.0.0.1:8000/admin/")
        print("   3. 使用账号登录: admin / admin123456")
        print("   4. 访问API文档: http://127.0.0.1:8000/swagger/")
    else:
        print("\n⚠️  部分测试失败，请检查上述错误信息")
        sys.exit(1)


if __name__ == '__main__':
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ 测试过程发生异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)