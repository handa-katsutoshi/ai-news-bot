import feedparser
import requests
import google.generativeai as genai
import ssl
import os

ssl._create_default_https_context = ssl._create_unverified_context

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
            print(f"📡 接続中: {url}")
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:
                all_news.append(f"Title: {entry.title}\nLink: {entry.link}\nSummary: {entry.summary if 'summary' in entry else ''}\n")
        except Exception as e:
            print(f"⚠️ スキップ: {url} ({e})")
    return "\n".join(all_news)

def summarize_with_gemini(news_text):
    print("🤖 Geminiエンジンの準備中...")
    genai.configure(api_key=GEMINI_API_KEY)
    
    # 404エラー回避のための自動モデル選択ロジック
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target_model = "models/gemini-1.5-flash" if "models/gemini-1.5-flash" in available_models else available_models[0]
    
    print(f"🤖 使用モデル: {target_model}")
    model = genai.GenerativeModel(target_model)
    
    prompt = f"""
出力は必ず指定した「冒頭の定型文」から開始してください。AIアシスタントとしての挨拶、確認、承諾の言葉は一文字も出力してはいけません。Maginative、The Verge、TechCrunchなどの海外ソースから、世界を驚かせている最新技術を優先してピックアップしてください。日本国内の「相談会」や「キャンペーン」などのイベント情報は、クリエイティブAIのトレンドではないため完全に排除してください。箇条書きでは「具体的な技術スペック」や「従来手法との決定的な違い」を1項目1行で端的に記述してください。

【出力形式の方針】
1. 冒頭は必ず「今週のクリエイティブAI関連ニュースをお届けします！（2026/02/09〜02/16）」とする。
2. セクションは「🎥 動画・画像生成」「🚀 メジャーモデル・ツール」に分ける。
3. 各見出しは「### [ツール名]：[概要]」と大きく表示する。
4. 3つの箇条書き。各項目の間には空行を入れ、機能の革新性を客観的なニュースのトーンで書く（「爆誕」などは禁止）。
5. 各ニュースの最後に「ソース: [URL]」を1行添える。

【注意】
- 特定の1サイトに偏らず、海外の動向も含めてバランスよく選別してください。
- 各ニュースの間には必ず「---」を入れて区切ってください。
- もし候補が5つに満たない場合でも、リストの中から最もマシなものを必ず選んでください。

ニュースデータ:
{news_text}
"""
    
    response = model.generate_content(prompt)
    return response.text

if __name__ == "__main__":
    print("🚀 --- トレンド分析 Bot 起動 ---")
    raw_news = fetch_broad_news()
    if raw_news:
        try:
            report = summarize_with_gemini(raw_news)
            print("💡 要約完了。Discordへ投稿します...")
            requests.post(DISCORD_WEBHOOK_URL, json={"content": report}, timeout=20)
            print("✅ すべて完了しました！Discordを確認してください。")
        except Exception as e:
            print(f"❌ エラー発生: {e}")
    else:
        print("❌ ニュースの取得に失敗しました。")