"""
主程序 - 简化版
"""

import argparse
import json
import os
from analyzer import SimpleAnalyzer
from generator import SimpleGenerator


def main():
    
    parser = argparse.ArgumentParser(description='简化的反爬虫分析系统')
    parser.add_argument('url', type=str, help='目标网站URL')
    parser.add_argument('--api-key', type=str, help='DeepSeek API密钥')
    parser.add_argument('--framework', type=str, default='requests',
                        choices=['requests', 'selenium'],
                        help='爬虫框架')
    parser.add_argument('--output', type=str, default='output',
                        help='输出目录')
    
    args = parser.parse_args()
    
    # 获取API密钥
    api_key = args.api_key or os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("❌ 错误: 需要提供 DeepSeek API 密钥")
        print("   方法1: --api-key YOUR_KEY")
        print("   方法2: export DEEPSEEK_API_KEY=YOUR_KEY")
        return
    
    # 创建输出目录
    os.makedirs(args.output, exist_ok=True)
    
    print("="*60)
    print("🤖 简化的反爬虫分析系统")
    print("="*60)
    
    # 步骤1: 分析
    analyzer = SimpleAnalyzer(api_key)
    analysis = analyzer.analyze(args.url)
    
    # 保存分析结果
    analysis_file = os.path.join(args.output, 'analysis.json')
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 分析完成")
    print(f"   风险等级: {analysis.get('risk_level', 'unknown').upper()}")
    print(f"   检测到策略: {len(analysis.get('strategies', []))} 个")
    print(f"   应对建议: {len(analysis.get('recommendations', []))} 条")
    
    # 打印建议
    print(f"\n📋 应对建议:")
    for rec in analysis.get('recommendations', []):
        print(f"   • {rec.get('method')}: {rec.get('reason')}")
    
    # 步骤2: 生成代码
    print(f"\n{'='*60}")
    generator = SimpleGenerator(api_key)
    code = generator.generate_code(args.url, analysis, args.framework)
    
    # 保存代码
    code_file = os.path.join(args.output, f'spider_{args.framework}.py')
    with open(code_file, 'w', encoding='utf-8') as f:
        f.write(code)
    
    print(f"✅ 代码已生成: {code_file}")
    
    print(f"\n{'='*60}")
    print("🎉 完成!")
    print(f"{'='*60}")
    print(f"\n生成的文件:")
    print(f"  1. 分析报告: {analysis_file}")
    print(f"  2. 爬虫代码: {code_file}")


if __name__ == '__main__':
    main()