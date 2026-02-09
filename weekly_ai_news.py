import feedparser
import requests
import google.generativeai as genai
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

# --- 設定 ---
GEMINI_API_KEY = "AIzaSyADwf8NOOMLxm1vQbilxPFipRObk4nzYzA"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1470304030621437986/faoZULE-5rwrAzuulffHaANHvZ9I_fhnyJvdtyYwTU91L0dMYfYgSMz-eSLpZZuT0VfS"

def fetch_news():
    feeds = [
        "https://www.maginative.com/rss/", # 海外AIクリエイティブ専門
        "https://www.itmedia.co.jp/aiplus/rss.xml", # ITmedia AI+
        "https://gamemakers.jp/feed/", # ゲーム制作・ツール関連
    ]
    all_news = []
    for url in feeds:
        feed = feedparser.parse(url)
        for entry in feed.entries[:8]:
            all_news.append(f"Title: {entry.title}\nLink: {entry.link}\nSummary: {entry.summary if 'summary' in entry else ''}\n")
    return "\n".join(all_news)

def summarize_with_gemini(news_text):
    genai.configure(api_key=GEMINI_API_KEY)
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target_model = "models/gemini-1.5-flash" if "models/gemini-1.5-flash" in available_models else available_models[0]
    model = genai.GenerativeModel(target_model)
    
    prompt = f"""
    あなたはクリエイティブ業界向けのニュースエディターです。
    提供されたリストから、Vidu Q3, Project Genie, Figma Vectorize, Roblox 4D等の「制作ワークフローに影響を与える最新情報」を厳選してください。

    【出力形式の指定】
    1. 冒頭は必ず「今週のクリエイティブAI関連ニュースをお届けします！（〜2026/02/09）」と記載する。
    2. セクション名は「🎥 動画・画像生成」「🚀 メジャーモデル・開発ツール」の2つに分ける。
    3. 各トピックのタイトルは「### ツール名：概要」とする。
    4. 内容は、機能の本質が伝わる3つの箇条書きにする。誇張表現（爆誕、とんでもない等）や過度な「！」は禁止。
    5. 各箇条書きの間には空行を入れ、ソースURLを最後に載せる。

    【コンテンツに関する補足】
    - 「Roblox」などの固有のサービス名については、どんなサービスなのかがわかる説明をしてください。例：動画生成AIプラットフォーム「RUNWAY」は
    - ビジネスニュース（ドメイン取得、資金調達など）は除外してください。

    ニュースリスト:
    {news_text}
    """
    
    response = model.generate_content(prompt)
    return response.text

def post_to_discord(content):
    # ニュースごとに分割して投稿
    sections = content.split("---")
    for section in sections:
        if section.strip():
            msg = section.strip()
            # 冒頭以外には区切り線を入れる
            if not msg.startswith("今週の"):
                msg = "---\n" + msg
            requests.post(DISCORD_WEBHOOK_URL, json={"content": msg})

if __name__ == "__main__":
    print("📰 ニュースを精査中...")
    raw_news = fetch_news()
    if raw_news:
        report = summarize_with_gemini(raw_news)
        print("📤 投稿中...")
        post_to_discord(report)
        print("✅ 完了しました。")