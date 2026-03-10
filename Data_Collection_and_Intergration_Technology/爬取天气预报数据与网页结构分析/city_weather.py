import requests
from bs4 import BeautifulSoup
from pyecharts import options as opts
from pyecharts.charts import Bar
from pyecharts.globals import ThemeType

def scrape_and_generate_chart():
    """
    爬取全国省会城市天气数据并生成柱状图（修正版）。
    """
    # 基础URL
    base_url = "https://www.weather.com.cn"
    # 包含全国所有区域的页面路径
    regions = [
        '/textFC/hb.shtml',   # 华北
        '/textFC/db.shtml',   # 东北
        '/textFC/hd.shtml',   # 华东
        '/textFC/hz.shtml',   # 华中
        '/textFC/hn.shtml',   # 华南
        '/textFC/xb.shtml',   # 西北
        '/textFC/xn.shtml',   # 西南
        '/textFC/gat.shtml'   # 港澳台
    ]

    # 用于存储所有省会城市数据的列表
    cities = []
    high_temps = []
    low_temps = []

    print("正在开始从中国天气网爬取数据...")

    # 遍历所有区域页面
    for region_path in regions:
        url = base_url + region_path
        print(f"正在处理: {url}")
        
        try:
            # 发送HTTP请求，并设置headers模拟浏览器访问
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            response.encoding = 'utf-8' # 确保正确解码中文

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 找到包含天气数据的div (只找第一个，即当天的数据)
                conMidtab = soup.find('div', class_='conMidtab')
                if not conMidtab:
                    continue

                # 找到所有省份的表格
                tables = conMidtab.find_all('table')
                
                for table in tables:
                    # 寻找包含省份信息的行
                    rows = table.find_all('tr')
                    
                    # 从第二行开始遍历（跳过表头）
                    for i in range(2, len(rows)):
                        cells = rows[i].find_all('td')
                        
                        # 确保行中有足够的数据
                        if len(cells) < 8:
                            continue

                        # 省会城市通常是每个省份表格的第一行数据
                        # 我们可以通过检查第一个td是否有class='rowsPan'来判断是否是新省份的开始
                        # 或者更简单的方法是，我们只取每个表格的第一条城市数据
                        is_capital = "rowsPan" in str(cells[0])
                        
                        # 如果是港澳台页面，每个城市都是一个"省份"，所以也适用此逻辑
                        if is_capital:
                            city = cells[1].text.strip()
                            
                            # --- 这是关键的修改 ---
                            # 如果城市尚未被记录，则添加数据
                            if city not in cities:
                                high_temp = int(cells[4].text.strip())
                                low_temp = int(cells[7].text.strip())
                                
                                cities.append(city)
                                high_temps.append(high_temp)
                                low_temps.append(low_temp)

                                print(f"  成功获取: {city}, 最高温: {high_temp}°C, 最低温: {low_temp}°C")
                            # 如果已经记录过，就直接跳过，不再抓取后面几天的数据
                            else:
                                continue
            else:
                print(f"请求失败，状态码: {response.status_code}")

        except requests.RequestException as e:
            print(f"请求发生错误: {e}")

    print("\n数据爬取完毕！正在生成图表...")

    # 使用 Pyecharts 绘制柱状图
    bar = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT, width="1600px", height="800px"))
        .add_xaxis(cities)
        .add_yaxis("最高气温", high_temps)
        .add_yaxis("最低气温", low_temps)
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="全国省会城市今日天气情况",
                subtitle=f"数据来源: 中国天气网"
            ),
            tooltip_opts=opts.TooltipOpts(
                is_show=True,
                trigger="axis",
                axis_pointer_type="cross"
            ),
            xaxis_opts=opts.AxisOpts(
                name="城市",
                axislabel_opts=opts.LabelOpts(rotate=-30) # X轴标签旋转，防止重叠
            ),
            yaxis_opts=opts.AxisOpts(
                name="温度 (°C)",
            ),
            datazoom_opts=[ # 添加滑动条用于区域缩放
                opts.DataZoomOpts(
                    is_show=True,
                    type_="slider",
                    range_start=0,
                    range_end=40, # 默认显示约前40%的数据
                ),
            ],
        )
    )

    # 生成HTML文件
    output_file = "全国省会城市天气柱状图.html"
    bar.render(output_file)
    print(f"图表已成功生成！请在浏览器中打开文件: {output_file}")


if __name__ == '__main__':
    scrape_and_generate_chart()