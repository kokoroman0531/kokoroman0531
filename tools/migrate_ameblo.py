#!/usr/bin/env python3
"""
アメブロ → 新HPブログ 移行スクリプト
=====================================
ひかるさんのアメブロ（https://ameblo.jp/zuttokimitoissyo/）の全記事を取得し、
新HPの blog.html / articles/ フォルダ用のHTMLファイルに変換します。

【使い方】
1. ターミナル（Macなら「ターミナル.app」）を開く
2. 以下のコマンドを順に実行:

   cd "/path/to/new_site/tools"
   pip3 install requests beautifulsoup4
   python3 migrate_ameblo.py

3. 完了すると以下が生成されます:
   - new_site/articles/article-XXXX.html  （個別記事ページ）
   - new_site/articles_data.json          （記事データのJSON）
   - new_site/blog.html                   （記事一覧が更新される）

【お試し実行（最初の3記事だけ取得）】
   python3 migrate_ameblo.py --limit 3
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from urllib.parse import urljoin

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("エラー: requests と beautifulsoup4 が必要です。")
    print("以下のコマンドでインストールしてください:")
    print("  pip3 install requests beautifulsoup4")
    sys.exit(1)


# ===== 設定 =====
BLOG_URL = "https://ameblo.jp/zuttokimitoissyo/"
ENTRY_LIST_URL = BLOG_URL + "entrylist.html"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ja,en;q=0.9",
}
DELAY_SEC = 1.5  # サーバー負荷軽減のためリクエスト間に待機

# 出力先（このスクリプトの1つ上のフォルダ＝new_site）
SITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLES_DIR = os.path.join(SITE_DIR, "articles")
JSON_FILE = os.path.join(SITE_DIR, "articles_data.json")
BLOG_HTML = os.path.join(SITE_DIR, "blog.html")


# ===== 共通ユーティリティ =====
def fetch(url):
    """URLを取得（HTML文字列を返す）"""
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.encoding = r.apparent_encoding or "utf-8"
        if r.status_code != 200:
            print(f"  ⚠️  HTTP {r.status_code}: {url}")
            return None
        return r.text
    except Exception as e:
        print(f"  ⚠️  取得失敗: {e}")
        return None


# ===== 記事URL一覧を取得 =====
def get_all_entry_urls():
    """entrylist のページネーションを辿って全記事URLを取得"""
    urls = []
    page = 1
    while True:
        list_url = (
            f"{BLOG_URL}entrylist-{page}.html" if page > 1 else ENTRY_LIST_URL
        )
        print(f"📄 一覧ページ {page} を取得中: {list_url}")
        html = fetch(list_url)
        if not html:
            break
        soup = BeautifulSoup(html, "html.parser")

        # 記事リンクを抽出（entry-で始まるhref）
        page_urls = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            m = re.search(r"/(entry-\d+\.html)", href)
            if m:
                full_url = urljoin(BLOG_URL, m.group(0))
                if full_url not in urls and full_url not in page_urls:
                    page_urls.append(full_url)

        if not page_urls:
            print("  → これ以上記事が見つかりませんでした")
            break
        print(f"  → {len(page_urls)} 件発見")
        urls.extend(page_urls)

        # 「次のページ」リンクの存在確認
        next_link = soup.find("a", string=re.compile(r"次の|Next|»"))
        next_link2 = soup.find("a", class_=re.compile(r"(pagingNext|next)"))
        if not (next_link or next_link2):
            # ページネーションが見つからない場合、ページ番号を増やして試す
            test_url = f"{BLOG_URL}entrylist-{page+1}.html"
            test_html = fetch(test_url)
            if not test_html:
                break
            time.sleep(DELAY_SEC)

        page += 1
        if page > 200:  # 安全装置
            print("  ⚠️  200ページに達したため停止")
            break
        time.sleep(DELAY_SEC)
    return urls


# ===== 記事ページから本文を抽出 =====
def extract_article(url):
    """個別記事ページから情報を抽出"""
    html = fetch(url)
    if not html:
        return None
    soup = BeautifulSoup(html, "html.parser")

    # 記事ID
    m = re.search(r"entry-(\d+)\.html", url)
    article_id = m.group(1) if m else "unknown"

    # タイトル: og:title or h1
    title = ""
    og_title = soup.find("meta", {"property": "og:title"})
    if og_title:
        title = og_title.get("content", "").split("｜")[0].split("|")[0].strip()
    if not title:
        h1 = soup.find("h1")
        if h1:
            title = h1.get_text(strip=True)

    # 公開日: article:published_time / time タグ
    date_str = ""
    meta_date = soup.find("meta", {"property": "article:published_time"})
    if meta_date:
        date_str = meta_date.get("content", "")[:10]
    if not date_str:
        time_el = soup.find("time")
        if time_el and time_el.get("datetime"):
            date_str = time_el["datetime"][:10]
    if not date_str:
        # 本文内に「YYYY-MM-DD」っぽいパターンを探す
        m = re.search(r"(\d{4})[-/](\d{2})[-/](\d{2})", html)
        if m:
            date_str = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"

    # 本文: アメブロは「skinArticleBody」「articleText」「entry-content」など
    content = ""
    for cls in ["skinArticleBody", "articleText", "entry-content", "article-text"]:
        body = soup.find("div", class_=re.compile(cls))
        if body:
            # 不要な広告・推奨記事リンクを除去
            for unwanted in body.find_all(
                ["script", "style", "iframe"]
            ):
                unwanted.decompose()
            for unwanted in body.find_all(class_=re.compile(r"(ad|recommend|share)", re.I)):
                unwanted.decompose()
            content = str(body)
            break

    return {
        "id": article_id,
        "url": url,
        "title": title or f"記事 {article_id}",
        "date": date_str or "",
        "content_html": content,
    }


# ===== 個別記事HTMLを生成 =====
ARTICLE_TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{description}">
    <title>{title}｜HIKARU SNS Marketing Studio</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.4.0/css/all.min.css">
    <link rel="stylesheet" href="../css/style.css">
    <style>
      .article-container {{ max-width: 800px; margin: 0 auto; padding: 0 24px; }}
      .article-meta {{ text-align: center; color: var(--c-text-3); margin-bottom: 32px; font-size: 14px; }}
      .article-body {{ background: #fff; padding: 48px; border-radius: var(--r-lg); box-shadow: var(--shadow-sm); line-height: 1.95; font-size: 16px; }}
      .article-body img {{ max-width: 100%; height: auto; border-radius: 8px; margin: 16px 0; }}
      .article-body p {{ margin-bottom: 16px; }}
      .article-body a {{ color: var(--c-yellow-deep); text-decoration: underline; }}
      .article-back {{ display: inline-flex; align-items: center; gap: 8px; color: var(--c-yellow-deep); font-weight: 600; margin-bottom: 24px; }}
      @media (max-width: 768px) {{ .article-body {{ padding: 28px 22px; }} }}
    </style>
</head>
<body>
    <header class="site-header" id="siteHeader">
        <div class="header-inner">
            <a href="../index.html" class="brand">
                <span class="brand-mark">H</span>
                <span class="brand-text">
                    <span class="brand-name">HIKARU</span>
                    <span class="brand-tag">SNS Marketing Studio</span>
                </span>
            </a>
            <nav class="global-nav" id="globalNav">
                <ul class="nav-list">
                    <li><a href="../index.html#service">サービス</a></li>
                    <li><a href="../index.html#tts">TTS</a></li>
                    <li><a href="../index.html#ai">AI</a></li>
                    <li><a href="../index.html#works">実績</a></li>
                    <li><a href="../blog.html">ブログ</a></li>
                </ul>
                <a href="../index.html#contact" class="nav-cta">お問い合わせ <i class="fas fa-arrow-right"></i></a>
            </nav>
            <button class="hamburger" id="hamburger"><span></span><span></span><span></span></button>
        </div>
    </header>

    <main class="legal-page">
        <div class="article-container">
            <a href="../blog.html" class="article-back"><i class="fas fa-arrow-left"></i> ブログ一覧に戻る</a>
            <h1 class="page-title">{title}</h1>
            <p class="article-meta">{date}</p>
            <div class="article-body">
                {content_html}
            </div>
            <div style="text-align: center; margin-top: 40px;">
                <a href="../blog.html" class="btn btn-ghost">ブログ一覧へ <i class="fas fa-arrow-right"></i></a>
            </div>
        </div>
    </main>

    <footer class="site-footer">
        <div class="container">
            <div class="footer-bottom">
                <p>&copy; 2026 HIKARU SNS Marketing Studio. All rights reserved.</p>
            </div>
        </div>
    </footer>
    <script src="../js/main.js"></script>
</body>
</html>
"""


def save_article_html(article):
    """個別記事HTMLを保存"""
    os.makedirs(ARTICLES_DIR, exist_ok=True)
    description = re.sub(r"<[^>]+>", "", article["content_html"])[:120]
    description = re.sub(r"\s+", " ", description).strip()

    out_html = ARTICLE_TEMPLATE.format(
        title=article["title"],
        date=article["date"] or "—",
        content_html=article["content_html"],
        description=description.replace('"', "'"),
    )
    path = os.path.join(ARTICLES_DIR, f"article-{article['id']}.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(out_html)


# ===== blog.html を更新 =====
def update_blog_index(articles):
    """blog.html の <div class="blog-list-grid"> 部分を生成記事で置換"""
    if not os.path.exists(BLOG_HTML):
        print(f"  ⚠️  {BLOG_HTML} が見つかりません。スキップします。")
        return

    # 日付で降順ソート
    articles_sorted = sorted(
        articles,
        key=lambda x: x.get("date", ""),
        reverse=True,
    )

    thumb_classes = ["thumb-1", "thumb-2", "thumb-3"]
    cards = []
    for i, a in enumerate(articles_sorted):
        thumb = thumb_classes[i % 3]
        # 抜粋: HTMLタグを除いた最初の80文字
        excerpt = re.sub(r"<[^>]+>", "", a["content_html"])
        excerpt = re.sub(r"\s+", " ", excerpt).strip()[:80]
        date_display = a["date"].replace("-", ".") if a["date"] else ""
        cards.append(f"""                <a href="articles/article-{a['id']}.html" class="blog-card">
                    <div class="blog-thumb {thumb}"><span class="blog-cat">記事</span></div>
                    <div class="blog-body">
                        <p class="blog-date">{date_display}</p>
                        <h3>{a['title']}</h3>
                        <p class="blog-excerpt">{excerpt}…</p>
                    </div>
                </a>""")

    cards_html = "\n".join(cards)

    with open(BLOG_HTML, "r", encoding="utf-8") as f:
        html = f.read()

    new_html = re.sub(
        r'(<div class="blog-list-grid">)[\s\S]*?(</div>\s*<div class="blog-pagination">)',
        f'\\1\n{cards_html}\n            \\2',
        html,
        count=1,
    )

    with open(BLOG_HTML, "w", encoding="utf-8") as f:
        f.write(new_html)


# ===== メイン =====
def main():
    parser = argparse.ArgumentParser(description="アメブロ → 新HP移行スクリプト")
    parser.add_argument("--limit", type=int, default=0, help="取得する記事数の上限（テスト用、0で無制限）")
    parser.add_argument("--from-json", action="store_true", help="既存のarticles_data.jsonからblog.htmlだけ再生成")
    args = parser.parse_args()

    if args.from_json:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            articles = json.load(f)
        print(f"📂 {len(articles)} 件の記事データを読み込みました")
        update_blog_index(articles)
        print(f"✅ blog.html を更新しました")
        return

    print("=" * 60)
    print("  アメブロ → 新HP 移行スクリプト")
    print(f"  対象: {BLOG_URL}")
    print("=" * 60)

    # ① 全記事URL取得
    urls = get_all_entry_urls()
    print(f"\n📊 合計 {len(urls)} 件の記事URLを発見しました\n")

    if args.limit > 0:
        urls = urls[: args.limit]
        print(f"⚙️  --limit {args.limit} のため、最初の {len(urls)} 件のみ処理します\n")

    # ② 各記事の本文取得 + HTML保存
    articles = []
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] {url}")
        article = extract_article(url)
        if article and article.get("title"):
            articles.append(article)
            save_article_html(article)
            print(f"  ✓ {article['title'][:40]} ({article['date']})")
        else:
            print(f"  × スキップ")
        time.sleep(DELAY_SEC)

    # ③ JSON保存
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    print(f"\n💾 articles_data.json を保存しました ({len(articles)} 件)")

    # ④ blog.html 更新
    update_blog_index(articles)
    print(f"✅ blog.html を更新しました")

    print("\n" + "=" * 60)
    print(f"  完了: {len(articles)} 件の記事を移行しました")
    print(f"  個別ページ: {ARTICLES_DIR}/")
    print(f"  一覧ページ: {BLOG_HTML}")
    print("=" * 60)


if __name__ == "__main__":
    main()
