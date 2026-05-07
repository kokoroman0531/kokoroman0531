# HIKARU - SNS Marketing Studio

SNS運用代行・ショート動画制作サービスを提供する「HIKARU」のコーポレートサイト。
旧「ひかる」個人サイトをビジネス／コーポレート寄りにリニューアルしたバージョンです。

## ファイル構成

```
new_site/
├── index.html           # トップページ
├── blog.html            # ブログ一覧ページ（新規）
├── tokushoho.html       # 特定商取引法に基づく表記
├── privacy.html         # プライバシーポリシー
├── css/
│   └── style.css        # 全ページ共通スタイル
├── js/
│   └── main.js          # 共通JavaScript
└── images/
    ├── profile.jpg      # 代表プロフィール写真
    ├── character.png    # （未使用：旧サイトから引き継ぎ）
    ├── cats.png         # （未使用：旧サイトから引き継ぎ）
    └── paw-icon.png     # （未使用：旧サイトから引き継ぎ）
```

## デザインコンセプト

- **ターゲット**：SNS運用・ショート動画制作を検討している企業担当者
- **トーン**：信頼感・専門性のあるビジネス／コーポレート
- **ブランド名**：HIKARU SNS Marketing Studio
- **キーカラー**：ネイビー (#0A2540) × オレンジ (#FF6B35)
- **フォント**：Inter（英数）／ Noto Sans JP（日本語）

## ページ構成（index.html）

1. ヒーロー（強いキャッチ + 実績数値 + ダッシュボード風ビジュアル）
2. 対応プラットフォームバナー
3. 課題提起（こんな課題はありませんか？）
4. サービス紹介（3プラン + 単発／育成）
5. HIKARUが選ばれる4つの理由
6. 制作実績（数値 + 動画埋め込み）
7. ご依頼の流れ（4ステップ）
8. 代表挨拶 / 会社情報
9. ブログ最新3記事
10. よくあるご質問（FAQ）
11. お問い合わせフォーム
12. フッター

## 主な変更点（旧サイトとの比較）

- 個人ブランディング → 屋号「HIKARU SNS Marketing Studio」のコーポレートブランディング
- 黄色基調の温かみあるデザイン → ネイビー×オレンジのビジネス系デザイン
- インフルエンサー要素を抑制し、「企業の発注者」目線に最適化
- ブログページを新設（カテゴリ・ページネーション付き）
- 課題提起・選ばれる理由・ご依頼の流れ・FAQ など BtoB 定番セクションを追加
- お問い合わせフォームに「会社名」フィールド追加

## 使用ライブラリ（CDN経由）

- Google Fonts: Inter / Noto Sans JP
- Font Awesome 6.4.0
- Instagram Embed Script

## 今後の改修候補

- 実際のブログ記事（マークダウン or CMS連携）
- 実績ロゴ・社名の差し替え（クライアント許諾後）
- お問い合わせフォームのバックエンド（Formspree代替）
- Google Analytics 4 / Search Console 連携
- 構造化データ（JSON-LD）の追加（Organization スキーマ）

---
© 2026 HIKARU SNS Marketing Studio. All rights reserved.
