import os
import newspaper
import openai

# GitHub SecretsからAPIキーを読み込む
openai.api_key = os.getenv('OPENAI_API_KEY')

# リポジトリ内のテキストファイルからニュースサイトのURLを読み込む
with open('news_sites.txt', 'r') as f:
    urls = [line.strip() for line in f]

# 各URLについて
for url in urls:
    # このウェブサイトから記事を取得
    website = newspaper.build(url)

    # 最初の5記事を取得
    articles = website.articles[:5]

    # 各記事について
    for a in articles:
        # 記事をダウンロード
        a.download()
        a.parse()

        # 記事の本文を取得
        text = a.text

        # GPT-3.5-turboを使って記事を要約
        response = openai.ChatCompletion.create(
          model="gpt-3.5-turbo",
          messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes news articles."},
                {"role": "user", "content": f"Here's a news article: {text}. Can you summarize it for me in japanese?"},
            ]
        )

        # 要約を取得
        summary = response['choices'][0]['message']['content']

        # 要約を表示
        print('Title:', a.title)
        print('Summary:', summary)
        print()
