"""
简化的反爬策略分析器 - 使用 DeepSeek API
"""

import requests
from bs4 import BeautifulSoup
import json
from openai import OpenAI


class SimpleAnalyzer:
    """简单的网站分析器"""
    
    def __init__(self, api_key):
        """初始化"""
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        print("✅ DeepSeek API 已连接")
    
    def analyze(self, url):
        """分析网站"""
        print(f"🔍 分析网站: {url}")
        
        # 1. 获取网站信息
        site_info = self._get_site_info(url)
        
        # 2. LLM 分析
        analysis = self._llm_analyze(url, site_info)
        
        return analysis
    
    def _get_site_info(self, url):
        """获取网站基本信息"""
        info = {
            'headers': {},
            'has_cloudflare': False,
            'has_js': False,
            'status_code': None
        }
        
        try:
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            info['status_code'] = response.status_code
            info['headers'] = dict(response.headers)
            
            # 检测 Cloudflare
            if 'CF-Ray' in response.headers or 'cloudflare' in str(response.headers).lower():
                info['has_cloudflare'] = True
            
            # 检测 JavaScript
            soup = BeautifulSoup(response.text, 'html.parser')
            scripts = soup.find_all('script')
            info['has_js'] = len(scripts) > 0
            info['script_count'] = len(scripts)
            
        except Exception as e:
            info['error'] = str(e)
        
        return info
    
    def _llm_analyze(self, url, site_info):
        """使用 LLM 分析"""
        prompt = f"""你是网络爬虫专家。请分析这个网站的反爬虫策略并给出应对建议。

网站: {url}
状态码: {site_info.get('status_code')}
有Cloudflare: {site_info.get('has_cloudflare')}
有JavaScript: {site_info.get('has_js')}
脚本数量: {site_info.get('script_count', 0)}

请用JSON格式返回，包含：
1. risk_level: 风险等级 (low/medium/high)
2. strategies: 检测到的反爬策略列表
3. recommendations: 应对建议列表（每条包含 method 和 reason）

只返回JSON，不要其他内容。"""

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            result_text = response.choices[0].message.content
            
            # 清理可能的markdown标记
            result_text = result_text.replace('```json', '').replace('```', '').strip()
            
            return json.loads(result_text)
            
        except Exception as e:
            return {
                'risk_level': 'unknown',
                'strategies': [],
                'recommendations': [{'method': 'manual', 'reason': f'分析失败: {str(e)}'}],
                'error': str(e)
            }