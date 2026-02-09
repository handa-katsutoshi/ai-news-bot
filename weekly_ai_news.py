import feedparser
import requests
import google.generativeai as genai
import ssl
import os

# サーバー上の通信エラー回避
ssl._create_default_https_context = ssl._create_unverified_context

# GitHub環境変数
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def fetch_broad_news():
    feeds = [
        "https://www.maginative.com/rss/",
        "https://www.itmedia.co.jp/aiplus/rss.xml",
        "https://techcrunch.com/category/artificial-intelligence/feed/",
        "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml",
        "https://gamemakers.jp/feed/"
    ]
    all_news = []
    for url in feeds:
        try:
            print(f"📡 {url} から情報を取得中...")
            feed = feedparser.parse(url)
            for entry in feed.entries[:15]: # 取得数をさらに増やして網を広げる
                all_news.append(f"Title: {entry.title}\nLink: {entry.link}\nSummary: {entry.summary if 'summary' in entry else ''}\n")
        except Exception as e:
            print(f"⚠️ スキップ: {url} ({e})")
    return "\n".join(all_news)

def summarize_with_gemini(news_text):
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    prompt = f"""
    あなたは世界中のAIトレンドを監視するプロのキュレーターです。
    提供されたリストから、SNSで今最も注目を浴びている、あるいはクリエイターが「今すぐ知るべき」AIニュースを【5つ】選んでください。

    【選定基準：トレンド感度MAX】
    - 世界的なトレンド（Vidu Q3, Sora, Runway Gen-3, Kling, Luma, Flux等）を最優先。
    - デザイン業界を激震させるメジャーツール（Figma, Adobe, Canva等）のAI新機能。
    - インプレッションが見込めない「法律」「会議」「地味な提携」のニュースは1つも入れないでください。

    【出力形式：Discord最適化】
    今週のクリエイティブAI関連ニュースをお届けします！（2026/02/02〜2026/02/09）

    ---
    🎥 動画・画像生成
    ### [ツール名]：[強烈なキャッチコピー]
    
    ・[なぜこれが「今」話題なのか？]
    
    ・[既存ツールと比べて何が圧倒的なのか？]
    
    ・[クリエイターがどう活用できるか？]
    
    ソース: [URL]

    ---
    🚀 メジャーモデル・開発ツール
    (同様の形式)

    ※各ニュースの間には必ず「---」を入れてください。
    ※もし候補が5つに満たない場合でも、リストの中から最もマシなものを必ず選んでください。
    """
    
    response = model.generate_content(prompt)
    return response.text

def post_to_discord(content):
    if not content or len(content) < 50:
        print("⚠️ 内容が短すぎるため送信を中止しました。")
        return

    sections = content.split("---")
    for section in sections:
        text = section.strip()
        if text:
            # 冒頭の挨拶以外には仕切り線を戻して投稿
            final_msg = text if "今週の" in text else "---\n" + text
            res = requests.post(DISCORD_WEBHOOK_URL, json={"content": final_msg}, timeout=20)
            if res.status_code == 204 or res.status_code == 200:
                print("📤 セクションの送信成功")
            else:
                print(f"❌ Discord送信失敗: {res.status_code}")

if __name__ == "__main__":
    print("📰 トレンド分析を開始します...")
    raw_news = fetch_broad_news()
    if raw_news:
        try:
            report = summarize_with_gemini(raw_news)
            print("💡 要約完了。Discordへ投稿します。")
            post_to_discord(report)
            print("✅ すべての処理が完了しました。")
        except Exception as e:
            print(f"❌ Gemini処理中にエラー: {e}")
    else:
        print("❌ ニュースの取得自体に失敗しました。")