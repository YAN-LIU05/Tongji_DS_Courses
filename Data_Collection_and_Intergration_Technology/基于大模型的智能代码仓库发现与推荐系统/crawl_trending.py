import datetime
import pymysql
import requests
from bs4 import BeautifulSoup
import emoji
import re
import ssl
import urllib3

# =========================
# 基本配置
# =========================
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# =========================
# 工具函数
# =========================
def replaces(s):
    """去掉换行和空格"""
    return s.replace('\n', '').replace('\r', '').replace(' ', '')

# =========================
# GitHub Trending 抓取函数
# =========================
def getRepo(since=None, lang=None):
    url = 'https://github.com/trending'
    url_prefix = 'https://github.com'

    if lang:
        url += '/' + lang
    if since:
        url += '?since=' + since

    response = requests.get(url, verify=False).text
    soup = BeautifulSoup(response, 'html.parser')
    articles = soup.find_all('article', {'class': 'Box-row'})

    trendings = []
    ranking = 0

    for article in articles:
        ranking += 1
        dic = {'ranking': ranking}

        # -------- repo 和 url --------
        repo_tag = article.find('h2', {'class': 'lh-condensed'})
        if repo_tag and repo_tag.a:
            repo_text = replaces(repo_tag.a.get('href'))
            dic['repo'] = repo_text
            dic['url'] = url_prefix + repo_text
        else:
            continue  # 跳过无效条目

        # -------- description --------
        desc_tag = article.find('p', {'class': 'col-9'})
        if desc_tag:
            dic['description'] = re.sub(
                ':\S+?:', ' ',
                emoji.demojize(desc_tag.text.strip())
            )
        else:
            dic['description'] = ""

        # -------- language --------
        lang_tag = article.find('span', {'itemprop': 'programmingLanguage'})
        dic['lang'] = lang_tag.text.strip() if lang_tag else ""

        # -------- stars / forks --------
        links = article.find_all('a', {'class': 'Link Link--muted d-inline-block mr-3'})
        if len(links) >= 2:
            dic['stars'] = links[0].text.strip()
            dic['forks'] = links[1].text.strip()
        else:
            dic['stars'] = "0"
            dic['forks'] = "0"

        # -------- today stars --------
        added = article.find('span', {'class': 'float-sm-right'})
        dic['added_stars'] = added.text.strip() if added else "0"

        trendings.append(dic)

    return trendings

# =========================
# 数据库操作
# =========================
def db_connect():
    try:
        db = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='lzz20050511',  # 修改为你的 MySQL 密码
            database='gitTrend_db',
            charset='utf8mb4'
        )
        return db
    except Exception as e:
        print('db connect fail:', e)
        return None

def db_close(db):
    if db:
        db.close()

def save_to_db(db, data):
    try:
        with db.cursor() as cursor:
            sql = '''
                INSERT INTO github_trending_day
                (ranking, repo, url, description, lang, stars, forks, added_stars, time)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,NOW())
            '''
            cursor.execute(sql, (
                data['ranking'],
                data['repo'],
                data['url'],
                data['description'],
                data['lang'],
                data['stars'],
                data['forks'],
                data['added_stars']
            ))
        db.commit()
        print('insert success:', data['repo'])
    except Exception as e:
        print('insert fail:', e)

# =========================
# 主程序入口
# =========================
if __name__ == '__main__':
    db = db_connect()

    if not db:
        print('数据库连接失败，程序终止')
    else:
        for data in getRepo():
            save_to_db(db, data)
        db_close(db)
        print("爬取并保存完成！")
