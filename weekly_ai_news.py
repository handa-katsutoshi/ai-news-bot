import feedparser
import requests
import google.generativeai as genai
import ssl
import os

# サーバー上の通信エラー回避
ssl._create_default_https_context = ssl._create_unverified_context

# GitHub環境変数
GEMINI_API_KEY = os.getenv("AIzaSyADwf8NOOMLxm1vQbilxPFipRObk4nzYzA")
DISCORD_WEBHOOK_URL = os.getenv("https://discord.com/api/webhooks/1470304030621437986/faoZULE-5rwrAzuulffHaANHvZ9I_fhnyJvdtyYwTU91L0dMYfYgSMz-eSLpZZuT0VfS")

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
            feed = feedparser.parse(url)
            # 各サイトから上位件数を取得
            for entry in feed.entries[:10]:
                all_news.append(f"Title: {entry.title}\nLink: {entry.link}\nSummary: {entry.summary if 'summary' in entry else ''}\n")
        except:
            continue
    return "\n".join(all_news)

def summarize_with_gemini(news_text):
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    prompt = f"""
    あなたはSNSでのインプレッション最大化を狙うテックエディターです。
    提供されたリストから、今日この瞬間にクリエイター界隈で最も「バズる」可能性が高いニュースを【厳選して5つ】抽出してください。

    【トレンド選別の優先順位（最重要）】
    1. 「動画生成AI」の衝撃的なアップデート（Vidu Q3, Sora, Runway, Kling等）
    2. 誰もが知るメジャーツールのAI機能統合（Figma, Canva, Adobe等）
    3. 従来の制作ワークフローを「破壊」するレベルの技術革新
    ※ 企業間の訴訟、資金調達、抽象的な法律の議論は「インプレッションが伸びない」ため、徹底的に除外してください。

    【出力形式の指定】
    今週のクリエイティブAI関連ニュースをお届けします！（2026/02/02〜2026/02/09）

    ---
    🎥 動画・画像生成
    ### [ツール名]：[一瞬で内容が理解できるキャッチコピー]
    
    ・[革新的なポイント：何が今までと違うのかを具体的に]
    
    ・[利便性：制作時間がどれくらい短縮されるか、何が可能になるか]
    
    ・[将来性：これが今後の業界標準になる理由]
    
    ソース: [URL]

    ---
    🚀 メジャーモデル・開発ツール
    (同様の形式で出力)

    【トーン＆マナー】
    - 専門用語を避けつつも、プロのクリエイターが満足する解像度で書いてください。
    - 各ニュースの後に必ず「---」を入れて、Discord上での視認性を高めてください。
    """
    
    response = model.generate_content(prompt)
    return response.text

def post_to_discord(content):
    # エラー回避のため、セクション（---）ごとに分割して投稿
    sections = content.split("---")
    for section in sections:
        text = section.strip()
        if text:
            # 冒頭の挨拶以外には仕切り線を戻して投稿
            final_msg = text if "今週の" in text else "---\n" + text
            requests.post(DISCORD_WEBHOOK_URL, json={"content": final_msg}, timeout=15)

if __name__ == "__main__":
    print("📰 トレンドニュースを精査中...")
    raw_news = fetch_broad_news()
    if raw_news:
        try:
            report = summarize_with_gemini(raw_news)
            post_to_discord(report)
            print("✅ 配信成功")
        except Exception as e:
            print(f"❌ Gemini実行エラー: {e}")