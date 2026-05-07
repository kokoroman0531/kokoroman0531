# アメブロ移行ツール 使い方ガイド

ひかるさんのアメブロ（https://ameblo.jp/zuttokimitoissyo/）の全記事を、
新HP（HIKARU SNS Marketing Studio）のブログとして取り込むスクリプトです。

---

## 🟢 ステップ 1：Pythonをインストールする（既に入っていればスキップ）

Macには標準でPythonが入っています。確認するには「ターミナル」を開いて：

```bash
python3 --version
```

`Python 3.x.x` と表示されればOKです。表示されない場合は [https://www.python.org/downloads/](https://www.python.org/downloads/) からインストールしてください。

---

## 🟢 ステップ 2：必要なライブラリをインストール

ターミナルで以下を1回だけ実行：

```bash
pip3 install requests beautifulsoup4
```

---

## 🟢 ステップ 3：スクリプトを実行

new_site フォルダに移動して、以下を実行します。

### お試し実行（最初の3記事だけ取得して動作確認）

```bash
cd "[new_siteフォルダのパス]/tools"
python3 migrate_ameblo.py --limit 3
```

ターミナルに以下のような表示が流れます：
```
📄 一覧ページ 1 を取得中: https://ameblo.jp/zuttokimitoissyo/entrylist.html
  → 10 件発見
📊 合計 10 件の記事URLを発見しました

[1/3] https://ameblo.jp/zuttokimitoissyo/entry-12345678.html
  ✓ 記事タイトルがここに表示されます (2024-05-01)
[2/3] ...
✅ blog.html を更新しました
```

完了したら、`new_site/blog.html` をブラウザで開いて、3記事が一覧に出ているか確認してください。問題なければ次のステップへ。

### 本番実行（全記事を取得）

```bash
python3 migrate_ameblo.py
```

記事数が多い場合は時間がかかります（1記事あたり約2秒、100記事で約3〜4分）。

---

## 🟢 ステップ 4：Netlifyに再アップロード

スクリプト実行後、`new_site` フォルダ全体を再度 [Netlify Drop](https://app.netlify.com/drop) にドラッグすれば公開サイトに反映されます。

---

## 🛠️ 実行後に生成されるもの

| ファイル/フォルダ | 説明 |
|----|----|
| `articles/article-XXXX.html` | 個別記事のHTMLページ |
| `articles_data.json` | 全記事のデータ（タイトル・日付・本文）。バックアップとして保管推奨 |
| `blog.html` | 記事一覧が自動更新されます |

---

## 🔁 もう一度実行したいとき

ブログに新しい記事が増えたとき・移行をやり直したいときは、もう一度 `python3 migrate_ameblo.py` を実行するだけでOKです。

JSONデータだけ残っていて、blog.htmlの一覧表示だけ作り直したい場合：
```bash
python3 migrate_ameblo.py --from-json
```

---

## ⚠️ 注意事項

- **アメブロのHTML構造が変わると動かなくなる可能性があります**。その場合は、お声がけいただければスクリプトを調整します。
- アメブロのサーバーに負荷をかけないよう、リクエスト間に1.5秒の待機を入れています。
- ご自身のブログ記事のみが取得対象です。
- 移行後、HPに掲載する内容に問題がないか目視で確認をお願いします（古い記事で個人情報・連絡先が含まれていないかなど）。

---

## 💡 トラブルシューティング

### 「pip3: command not found」と出る
Pythonが正しくインストールされていません。[https://www.python.org/downloads/](https://www.python.org/downloads/) から最新版を入れてください。

### 「ModuleNotFoundError: No module named 'requests'」と出る
ステップ2のライブラリインストールができていません。再度 `pip3 install requests beautifulsoup4` を実行。

### 1記事も取得できない
アメブロのHTML構造が変わった可能性があります。スクリプト内の `extract_article` 関数の調整が必要なので、お知らせください。

### 記事の画像が表示されない
画像はアメブロのサーバーから直接読み込まれます（HTML内の`<img src="https://stat.ameba.jp/...">`がそのまま残ります）。問題が出た場合は、画像を別途ダウンロードする処理を追加できます。
