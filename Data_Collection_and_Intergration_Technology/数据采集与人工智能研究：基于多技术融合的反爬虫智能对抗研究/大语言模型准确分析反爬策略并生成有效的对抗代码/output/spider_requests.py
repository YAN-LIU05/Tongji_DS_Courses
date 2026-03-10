#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上海天气爬虫 (http://www.weather.com.cn/weather/101020100.shtml)
使用requests + 正则表达式/BeautifulSoup解析
注意：该网站使用JavaScript动态渲染，此代码可能无法获取完整数据
建议使用Selenium或Playwright获取动态内容
"""

import requests
import re
import time
import random
from bs4 import BeautifulSoup
import json
from typing import Dict, List, Optional
import logging
from urllib.parse import urlparse
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('weather_spider.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WeatherSpider:
    """天气爬虫类"""
    
    def __init__(self):
        """初始化爬虫配置"""
        self.base_url = "http://www.weather.com.cn/weather/101020100.shtml"
        
        # 用户代理列表，用于轮换
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        # 请求头
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
        # 会话对象，维持cookies
        self.session = requests.Session()
        
        # 请求间隔（秒）
        self.request_interval = random.uniform(3, 5)
        
        # 最大重试次数
        self.max_retries = 3
        
        # 超时时间（秒）
        self.timeout = 10
        
    def get_random_user_agent(self) -> str:
        """获取随机用户代理"""
        return random.choice(self.user_agents)
    
    def check_robots_txt(self) -> bool:
        """检查robots.txt文件"""
        try:
            parsed_url = urlparse(self.base_url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            
            response = self.session.get(
                robots_url,
                headers={'User-Agent': self.get_random_user_agent()},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                robots_content = response.text
                logger.info(f"robots.txt内容:\n{robots_content[:500]}...")
                
                # 检查是否允许爬取目标页面
                if f"Disallow: {parsed_url.path}" in robots_content:
                    logger.warning(f"robots.txt禁止爬取: {parsed_url.path}")
                    return False
                return True
            else:
                logger.info(f"未找到robots.txt文件 (状态码: {response.status_code})")
                return True
                
        except Exception as e:
            logger.warning(f"检查robots.txt时出错: {e}")
            return True
    
    def detect_encoding(self, response: requests.Response) -> str:
        """检测网页编码"""
        # 1. 从Content-Type头部获取
        content_type = response.headers.get('Content-Type', '').lower()
        if 'charset=' in content_type:
            charset = content_type.split('charset=')[-1].strip()
            return charset
        
        # 2. 从HTML meta标签获取
        try:
            # 使用正则表达式查找charset
            charset_patterns = [
                r'<meta[^>]*charset=["\']?([^"\'>]+)["\']?',
                r'<meta[^>]*content=["\'][^"\']*charset=([^"\'>]+)["\']?'
            ]
            
            for pattern in charset_patterns:
                match = re.search(pattern, response.text[:5000], re.IGNORECASE)
                if match:
                    charset = match.group(1).strip()
                    if charset:
                        return charset
        except:
            pass
        
        # 3. 默认使用GBK（中国天气网常用编码）
        return 'gbk'
    
    def fetch_page(self, url: str) -> Optional[str]:
        """获取网页内容"""
        for retry in range(self.max_retries):
            try:
                # 随机延迟，模拟人类行为
                time.sleep(self.request_interval)
                
                # 更新请求头
                self.headers['User-Agent'] = self.get_random_user_agent()
                
                logger.info(f"第{retry + 1}次尝试获取页面: {url}")
                
                response = self.session.get(
                    url,
                    headers=self.headers,
                    timeout=self.timeout,
                    allow_redirects=True
                )
                
                # 检查响应状态
                if response.status_code == 200:
                    # 检测编码
                    encoding = self.detect_encoding(response)
                    logger.info(f"检测到编码: {encoding}")
                    
                    # 使用检测到的编码解码内容
                    response.encoding = encoding
                    return response.text
                elif response.status_code == 403:
                    logger.error(f"访问被拒绝 (403)，可能需要使用无头浏览器")
                    return None
                elif response.status_code == 404:
                    logger.error(f"页面不存在 (404)")
                    return None
                elif response.status_code == 503:
                    logger.warning(f"服务暂时不可用 (503)，重试中...")
                    time.sleep(5)  # 等待更长时间
                else:
                    logger.warning(f"HTTP状态码 {response.status_code}，重试中...")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"请求超时，重试中... (尝试 {retry + 1}/{self.max_retries})")
            except requests.exceptions.ConnectionError:
                logger.warning(f"连接错误，重试中... (尝试 {retry + 1}/{self.max_retries})")
                time.sleep(2)
            except requests.exceptions.RequestException as e:
                logger.error(f"请求异常: {e}")
                break
            except Exception as e:
                logger.error(f"未知错误: {e}")
                break
        
        logger.error(f"获取页面失败，已达到最大重试次数: {self.max_retries}")
        return None
    
    def parse_weather_data(self, html: str) -> List[Dict]:
        """解析天气数据"""
        weather_data = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # 方法1: 尝试通过HTML解析获取数据
            # 查找天气信息容器（根据实际网站结构调整选择器）
            weather_items = soup.select('.t.clearfix li') or soup.select('.c7d ul li')
            
            if weather_items:
                logger.info(f"通过CSS选择器找到 {len(weather_items)} 个天气项目")
                
                for item in weather_items[:7]:  # 通常显示7天预报
                    try:
                        # 提取日期
                        date_elem = item.select_one('h1') or item.select_one('.date')
                        date = date_elem.get_text(strip=True) if date_elem else "未知日期"
                        
                        # 提取天气状况
                        wea_elem = item.select_one('.wea') or item.select_one('p.wea')
                        weather = wea_elem.get_text(strip=True) if wea_elem else "未知"
                        
                        # 提取温度
                        temp_elem = item.select_one('.tem') or item.select_one('p.tem')
                        temperature = temp_elem.get_text(strip=True) if temp_elem else "未知"
                        
                        # 提取风向风力
                        wind_elem = item.select_one('.win') or item.select_one('p.win')
                        wind = wind_elem.get_text(strip=True) if wind_elem else "未知"
                        
                        weather_data.append({
                            'date': date,
                            'weather': weather,
                            'temperature': temperature,
                            'wind': wind
                        })
                        
                    except Exception as e:
                        logger.warning(f"解析单个天气项目时出错: {e}")
                        continue
            
            # 方法2: 如果方法1失败，尝试通过正则表达式查找
            if not weather_data:
                logger.info("尝试使用正则表达式解析数据...")
                
                # 查找可能的天气数据模式
                patterns = [
                    r'<h1>([^<]+)</h1>.*?<p[^>]*class="wea"[^>]*>([^<]+)</p>.*?<p[^>]*class="tem"[^>]*>([^<]+)</p>',
                    r'"od":\s*\{[^}]+"od2":\s*"([^"]+)"[^}]+"od21":\s*"([^"]+)"[^}]+"od22":\s*"([^"]+)"',
                    r'<li[^>]*data-dn="7d"[^>]*>.*?<h1>([^<]+)</h1>.*?<p[^>]*class="wea"[^>]*>([^<]+)</p>'
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, html, re.DOTALL)
                    if matches:
                        logger.info(f"通过正则表达式找到 {len(matches)} 条数据")
                        for match in matches:
                            if len(match) >= 3:
                                weather_data.append({
                                    'date': match[0],
                                    'weather': match[1],
                                    'temperature': match[2],
                                    'wind': match[3] if len(match) > 3 else "未知"
                                })
                        break
            
            # 方法3: 查找JSON数据（如果网站使用JavaScript加载）
            if not weather_data:
                logger.info("尝试查找JSON格式的天气数据...")
                
                # 查找可能的JSON数据
                json_patterns = [
                    r'var\s+dataSK\s*=\s*(\{.*?\});',
                    r'var\s+weatherData\s*=\s*(\{.*?\});',
                    r'"7d":\s*(\[.*?\])'
                ]
                
                for pattern in json_patterns:
                    matches = re.search(pattern, html, re.DOTALL)
                    if matches:
                        try:
                            json_str = matches.group(1)
                            json_data = json.loads(json_str)
                            logger.info(f"找到JSON数据: {type(json_data)}")
                            
                            # 根据实际JSON结构提取数据
                            if isinstance(json_data, dict):
                                # 尝试提取城市信息
                                city = json_data.get('cityname', '上海')
                                logger.info(f"城市: {city}")
                                
                                # 尝试提取7天预报
                                forecast = json_data.get('7d', []) or json_data.get('f', [])
                                if forecast:
                                    for day in forecast[:7]:
                                        weather_data.append({
                                            'date': day.get('date', ''),
                                            'weather': day.get('weather', ''),
                                            'temperature': day.get('tem', ''),
                                            'wind': day.get('win', '')
                                        })
                                    
                        except json.JSONDecodeError as e:
                            logger.warning(f"JSON解析错误: {e}")
                        except Exception as e:
                            logger.warning(f"处理JSON数据时出错: {e}")
            
            return weather_data
            
        except Exception as e:
            logger.error(f"解析天气数据时出错: {e}")
            return weather_data
    
    def save_to_json(self, data: List[Dict], filename: str = 'weather_data.json'):
        """保存数据到JSON文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"数据已保存到 {filename}")
        except Exception as e:
            logger.error(f"保存数据时出错: {e}")
    
    def print_weather_data(self, data: List[Dict]):
        """打印天气数据"""
        if not data:
            print("未找到天气数据")
            return
        
        print("\n" + "="*60)
        print("上海天气预报")
        print("="*60)
        
        for item in data:
            print(f"日期: {item.get('date', '未知')}")
            print(f"天气: {item.get('weather', '未知')}")
            print(f"温度: {item.get('temperature', '未知')}")
            print(f"风力: {item.get('wind', '未知')}")
            print("-"*40)
    
    def run(self):
        """运行爬虫"""
        logger.info("开始爬取上海天气数据...")
        
        # 检查robots.txt
        if not self.check_robots_txt():
            logger.warning("robots.txt限制访问，程序退出")
            return
        
        # 获取页面内容
        html_content = self.fetch_page(self.base_url)
        
        if not html_content:
            logger.error("无法获取页面内容，程序退出")
            return
        
        # 保存原始HTML用于调试
        try:
            with open('weather_page.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info("原始HTML已保存到 weather_page.html")
        except:
            pass
        
        # 解析天气数据
        weather_data = self.parse_weather_data(html_content)
        
        if weather_data:
            logger.info(f"成功解析 {len(weather_data)} 条天气数据")
            
            # 打印数据
            self.print_weather_data(weather_data)
            
            # 保存数据
            self.save_to_json(weather_data)
            
            # 保存为文本文件
            try:
                with open('weather_report.txt', 'w', encoding='utf-8') as f:
                    f.write("上海天气预报\n")
                    f.write("="*40 + "\n")
                    for item in weather_data:
                        f.write(f"日期: {item.get('date', '未知')}\n")
                        f.write(f"天气: {item.get('weather', '未知')}\n")
                        f.write(f"温度: {item.get('temperature', '未知')}\n")
                        f.write(f"风力: {item.get('wind', '未知')}\n")
                        f.write("-"*40 + "\n")
                logger.info("文本报告已保存到 weather_report.txt")
            except Exception as e:
                logger.error(f"保存文本报告时出错: {e}")
        else:
            logger.warning("未找到天气数据，可能原因:")
            logger.warning("1. 网站结构已更改")
            logger.warning("2. 数据通过JavaScript动态加载")
            logger.warning("3. 需要处理反爬虫机制")
            logger.warning("建议使用Selenium或Playwright等无头浏览器工具")
            
            # 尝试查找API接口
            logger.info("尝试查找API接口...")
            api_patterns = [
                r'http[^"\']+101020100[^"\']*\.json',
                r'http[^"\']+weather[^"\']*101020100[^"\']*',
                r'var\s+cityDZ\s*=\s*"([^"]+)"'
            ]
            
            for pattern in api_patterns:
                matches = re.findall(pattern, html_content)
                if matches:
                    logger.info(f"找到可能的API接口: {matches[:3]}")
        
        logger.info("爬虫执行完成")


def main():
    """主函数"""
    try:
        spider = WeatherSpider()
        spider.run()
    except KeyboardInterrupt:
        logger.info("用户中断程序")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序执行出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()