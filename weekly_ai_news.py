import feedparser
import requests
import google.generativeai as genai
import ssl
import os

# エラー回避
ssl._create_default_https_context = ssl._create_unverified_context

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def fetch_broad_news():
    feeds = ["https://www.maginative.com/rss/", "https://www.itmedia.co.jp/aiplus/rss.xml", "https://gamemakers.jp/feed/"]
    all_news = []
    for url in feeds:
        print(f"📡 取得開始: {url}")
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:
            all_news.append(f"Title: {entry.title}\nLink: {entry.link}\n")
    return "\n".join(all_news)

def summarize_with_gemini(news_text):
    print("🤖 Geminiで要約を開始します...")
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    prompt = f"以下のニュースからクリエイター向けにバズりそうな情報を5つ選び、Discord形式で要約して。ソースURLも付けて。\n\n{news_text}"
    response = model.generate_content(prompt)
    return response.text

if __name__ == "__main__":
    print("🚀 --- プログラム開始 ---")
    news = fetch_broad_news()
    if news:
        print(f"✅ ニュースを {len(news.splitlines())//2} 件取得しました")
        try:
            report = summarize_with_gemini(news)
            print("📤 Discordへ送信します...")
            requests.post(DISCORD_WEBHOOK_URL, json={"content": report})
            print("✨ すべて完了しました！")
        except Exception as e:
            print(f"❌ エラー発生: {e}")
    else:
        print("❌ ニュースが1件も取得できませんでした。")