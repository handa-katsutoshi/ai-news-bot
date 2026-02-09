import feedparser
import requests
import google.generativeai as genai
import ssl
import os
import random

# 通信エラー回避
ssl._create_default_https_context = ssl._create_unverified_context

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def fetch_broad_news():
    # 海外の影響度が高いソースを上位に配置
    feeds = [
        ("Maginative", "https://www.maginative.com/rss/"),
        ("The Verge", "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml"),
        ("TechCrunch", "https://techcrunch.com/category/artificial-intelligence/feed/"),
        ("ITmedia AI+", "https://www.itmedia.co.jp/aiplus/rss.xml"),
        ("GameMakers", "https://gamemakers.jp/feed/")
    ]
    
    all_news = []
    # 影響度の低い「お知らせ・イベント・採用」を弾くキーワード
    noise_keywords = ["相談会", "キャンペーン", "採用", "セミナー", "イベント", "募集", "クーポン", "無料配布"]

    for name, url in feeds:
        try:
            print(f"📡 取得中: {name}")
            feed = feedparser.parse(url)
            count = 0
            for entry in feed.entries:
                if count >= 15: break # 1サイトあたりの上限を増やして網を広げる
                
                title = entry.title
                summary = entry.summary if 'summary' in entry else ""
                
                # ノイズが含まれる場合はスキップ
                if any(k in title for k in noise_keywords):
                    continue
                
                all_news.append(f"Source: {name}\nTitle: {title}\nLink: {entry.link}\nSummary: {summary}\n")
                count += 1
        except Exception as e:
            print(f"⚠️ スキップ: {name} ({e})")
    
    return "\n".join(all_news)

def summarize_with_gemini(news_text):
    print("🤖 Geminiエンジンの準備中...")
    genai.configure(api_key=GEMINI_API_KEY)
    
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target_model = "models/gemini-1.5-flash" if "models/gemini-1.5-flash" in available_models else available_models[0]
    
    print(f"🤖 使用モデル: {target_model}")
    model = genai.GenerativeModel(target_model)
    
    prompt = f"""
出力は必ず指定した「冒頭の定型文」から開始してください。AIアシスタントとしての挨拶、確認、承諾の言葉は一文字も出力してはいけません。

あなたは世界中のAIトレンドを監視するプロのSNSキュレーターです。提供されたリストから、SNSで数万RTされるような「影響度が高い」「技術的に破壊的な」ニュースを【5つ】厳選してください。

【選定の鉄則：影響度を最優先】
1. 海外の一次ソース（Maginative, The Verge等）を優先し、Apple, OpenAI, Google, Metaなどのビッグテックの動向や、Sora, Flux, Luma等の主要モデルのアップデートを最優先してください。
2. 日本国内のローカルな「イベント」「相談会」「キャンペーン」は、どんなに有益でも「SNSトレンド」ではないため【100%除外】してください。
3. ニュースリストの中で、技術的に最も新しく、クリエイターのワークフローを根底から変えるものだけを選んでください。

【出力形式】
1. 冒頭は「今週のクリエイティブAI関連ニュースをお届けします！（2026/02/09〜02/16）」とする。
2. 見出しは「### [ツール名]：[概要]」とする。
3. 箇条書きは、機能の革新性と「なぜこれが業界で注目されているのか」を客観的かつ鋭い分析トーンで書いてください。
4. 各ニュースの間には必ず「---」を入れてください。

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
            print("✅ すべて完了しました！")
        except Exception as e:
            print(f"❌ エラー発生: {e}")