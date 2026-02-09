import feedparser
import requests
import google.generativeai as genai
import ssl
import os

# Macの通信ブロックを回避
ssl._create_default_https_context = ssl._create_unverified_context

# --- 設定（GitHub環境変数） ---
GEMINI_API_KEY = os.getenv("AIzaSyADwf8NOOMLxm1vQbilxPFipRObk4nzYzA")
DISCORD_WEBHOOK_URL = os.getenv("https://discord.com/api/webhooks/1470304030621437986/faoZULE-5rwrAzuulffHaANHvZ9I_fhnyJvdtyYwTU91L0dMYfYgSMz-eSLpZZuT0VfS")

def fetch_broad_news():
    # ソースをさらに広げ、海外の速報サイトを上位に配置
    feeds = [
        "https://www.maginative.com/rss/", # 世界のAIトレンド最速
        "https://techcrunch.com/category/artificial-intelligence/feed/", # テック全般
        "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml", # デザイントレンド
        "https://www.itmedia.co.jp/aiplus/rss.xml", # 日本のAI速報
        "https://gamemakers.jp/feed/" # ゲーム・3D関連
    ]
    all_news = []
    for url in feeds:
        print(f"📡 {url} から取得中...")
        feed = feedparser.parse(url)
        for entry in feed.entries[:10]: # 取得件数を増やしてGeminiに選別させる
            all_news.append(f"Title: {entry.title}\nLink: {entry.link}\nSummary: {entry.summary if 'summary' in entry else ''}\n")
    return "\n".join(all_news)

def summarize_with_gemini(news_text):
    genai.configure(api_key=GEMINI_API_KEY)
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target_model = "models/gemini-1.5-flash" if "models/gemini-1.5-flash" in available_models else available_models[0]
    model = genai.GenerativeModel(target_model)
    
    prompt = f"""
    あなたはクリエイティブ専門のトレンドアナリストです。
    提供されたリストから、世界中で話題になっている、あるいは急上昇しているAIツール（特に動画生成、画像生成、3D、デザイン）に関するニュースを【5つ】厳選してください。

    【特に注目すべきキーワード】
    Vidu Q3, OpenAI Sora, Runway Gen-3, Kling, Luma Dream Machine, Flux.1, Midjourney, Figma AI, Adobe Firefly, Project Genie

    【出力形式の指定】
    1. 冒頭は必ず「今週のクリエイティブAI関連ニュースをお届けします！（2026/02/02〜2026/02/09）」とする。
    2. セクションは「🎥 動画・画像生成」「🚀 メジャーモデル・開発ツール」に分ける。
    3. 各見出しは「### [ツール名]：[概要]」と大きく表示する。
    4. 3つの箇条書き。各項目の間には空行を入れ、機能の革新性を客観的なニュースのトーンで書く（「爆誕」などは禁止）。
    5. 各ニュースの最後に「ソース: [URL]」を1行添える。余計なサイト解説は不要。

    【注意】
    - 特定の1サイト（例：gamemakers）に偏らず、海外の動向も含めてバランスよく選別してください。
    - 資金調達やビジネスの話は除外し、ツール自体の進化にフォーカスしてください。

    ニュースリスト:
    {news_text}
    """
    
    response = model.generate_content(prompt)
    return response.text

def post_to_discord(content):
    sections = content.split("---")
    for section in sections:
        if section.strip():
            msg = section.strip()
            if not msg.startswith("今週の"):
                msg = "---\n" + msg
            requests.post(DISCORD_WEBHOOK_URL, json={"content": msg})

if __name__ == "__main__":
    raw_news = fetch_broad_news()
    if raw_news:
        report = summarize_with_gemini(raw_news)
        post_to_discord(report)
        print("✅ アップデート完了！")