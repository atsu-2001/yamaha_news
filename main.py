from selenium import webdriver
from bs4 import BeautifulSoup
import time
import pandas as pd
from datetime import datetime
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os

load_dotenv()

browser = webdriver.Chrome()

url = 'https://news.yahoo.co.jp/search?p=ヤマハ発動機'
browser.get(url)
time.sleep(5)

soup = BeautifulSoup(browser.page_source, 'html.parser')
browser.quit()

newsfeed = soup.find('ol')
links = newsfeed.find_all('a')

today = datetime.today()
today_md = today.strftime('%-m/%-d')

today_news_links = []
for link in links:
    news_date = link.get_text()
    if today_md in news_date:
        today_news_links.append(link)

titles = []
hrefs = []
for today_news_link in today_news_links:
    href = today_news_link.get('href', '')
    if 'articles' in href:
        title = today_news_link.get_text().strip()
        if title and title not in titles:
            titles.append(title)
            hrefs.append(href)

df = pd.DataFrame({
    'タイトル':titles,
    'リンク':hrefs
})
df.to_csv('yamaha.csv',index=False)


GMAIL_ADDRESS = os.getenv('GMAIL_ADDRESS')
APP_PASSWORD = os.getenv('APP_PASSWORD')
TO_ADDRESS = os.getenv('TO_ADDRESS')

body = "【本日のヤマハ発動機ニュース】\n\n"
if len(df) == 0:
    body += "本日見つかった記事はありませんでした。"
else:
    for i in range(len(df)):
        body += f"{i + 1}. {df.iloc[i]['タイトル']}\n"
        body += f"{df.iloc[i]['リンク']}\n\n"

# --- メール本文を作成 ---
msg = EmailMessage()
msg['Subject'] = '【ヤマハ発動機】今日のニュース通知'
msg['From'] = GMAIL_ADDRESS
msg['To'] = TO_ADDRESS
msg.set_content(body)

# --- Gmailサーバーに接続して送信 ---
with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
    smtp.starttls()
    smtp.login(GMAIL_ADDRESS, APP_PASSWORD)
    smtp.send_message(msg)

print("✅ メール送信完了！")
