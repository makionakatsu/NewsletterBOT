import os
import datetime
import newspaper
from openai import OpenAI
import requests

# 現在の日付を取得
today = datetime.date.today()

# GitHub SecretsからAPIキーを読み込む
openai_api_key = os.getenv('OPENAI_API_KEY')

# OpenAI API キーの設定
client = OpenAI()

# ウェブフックURLを読み込み、カンマで区切られたリストに変換する
WEBHOOK_URLS = os.getenv('DISCORD_WEBHOOK_URL').split(',')

# リポジトリ内のテキストファイルからニュースサイトのURLを読み込む
with open('news_sites.txt', 'r') as f:
    urls = [line.strip() for line in f]

# 各URLについて
for url in urls:
    # このウェブサイトから記事を取得
    website = newspaper.build(url)

    # 最初の3記事を取得
    articles = website.articles[:3]

    # 各記事について
    for a in articles:
        # 記事をダウンロードして解析
        a.download()
        a.parse()

        # 記事の掲載日を取得
        publish_date = a.publish_date

        # 掲載日が今日の場合のみ処理を続ける
        if publish_date and publish_date.date() == today:
            # 記事の本文を取得
            text = a.text

            # GPT-3.5-turboを使って記事を要約
            response_summary = client.chat.completions.create(
                model="gpt-3.5-turbo-16k",
                messages=[
                    {"role": "system", "content": "You are an assistant who summarizes news articles in Japanese into about 200 characters. You can generate interesting sentences."},
                    {"role": "user", "content": f"Here's a news article: {text}. Can you summarize it for me in japanese?"},
                ],
                max_tokens=300
            )

            # 要約を取得
            summary = response_summary.choices[0].message.content

            # ディスコードに送信するメッセージをフォーマット
            message = f"🗞{website.brand}\n📝{a.title}\n{summary}\n🔗{a.url}\n⌐◨-◨ ⌐◨-◨ ⌐◨-◨ ⌐◨-◨ ⌐◨-◨ ⌐◨-◨\n\n"
            print(message)
            
            # 各ウェブフックURLに対してディスコードに送信
            for webhook_url in WEBHOOK_URLS:
                data = {
                    "content": message
                }
                response = requests.post(webhook_url.strip(), data=data)
