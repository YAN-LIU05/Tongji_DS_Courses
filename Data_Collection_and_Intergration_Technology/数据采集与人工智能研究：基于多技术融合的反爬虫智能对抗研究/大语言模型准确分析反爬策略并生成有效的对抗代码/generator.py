"""
简化的爬虫代码生成器
"""

from openai import OpenAI


class SimpleGenerator:
    """简单的代码生成器"""
    
    def __init__(self, api_key):
        """初始化"""
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
    
    def generate_code(self, url, analysis, framework='requests'):
        """生成爬虫代码"""
        print(f"💻 生成 {framework} 代码...")
        
        prompt = self._build_prompt(url, analysis, framework)
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=4000
            )
            
            code = response.choices[0].message.content
            
            # 清理markdown标记
            code = code.replace('```python', '').replace('```', '').strip()
            
            return code
            
        except Exception as e:
            return f"# 生成失败: {str(e)}"
    
    def _build_prompt(self, url, analysis, framework):
        """构建提示词"""
        
        recommendations = analysis.get('recommendations', [])
        rec_text = '\n'.join([f"- {r.get('method')}: {r.get('reason')}" for r in recommendations])
        
        prompt = f"""生成一个完整的Python爬虫代码，用于抓取: {url}

## 检测到的风险
风险等级: {analysis.get('risk_level', 'unknown')}

## 应对建议
{rec_text}

## 要求
1. 使用 {framework} 框架
2. 包含所有必要的反爬虫对策
3. 代码完整可运行
4. 添加详细注释
5. 包含错误处理
6. 检测网页编码，默认为GBK

直接输出Python代码，不要解释。"""

        return prompt