# Backlog Backup

Backlogプロジェクトデータをバックアップするためのコマンドラインツールです。

[English README](README.md)

## 特徴

- コマンドラインからBacklogプロジェクトデータをバックアップ
- 複数の種類のプロジェクトデータをバックアップ可能：
  - 課題（一覧と詳細）
  - Wikiページ
  - ファイル
  - Gitリポジトリ
  - Subversionリポジトリ
- 可能な限りBacklog APIを使用
- 必要に応じてWebスクレイピングにフォールバック（適切なレート制限付き）

## インストール

### 要件

- Python 3.8以上
- Git（Gitリポジトリバックアップ用）
- Subversion（SVNリポジトリバックアップ用）

### ソースからインストール

```bash
# リポジトリをクローン
git clone https://github.com/tmyymmt/backlog-backup.git
cd backlog-backup

# パッケージをインストール
pip install -e .

# Webスクレイピングサポート（オプション）
pip install -e ".[scraping]"
```

### Dockerを使用

```bash
# リポジトリをクローン
git clone https://github.com/tmyymmt/backlog-backup.git
cd backlog-backup

# Dockerイメージをビルド
docker build -t backlog-backup .

# コンテナを実行
docker run -v $(pwd)/backup:/app/backup backlog-backup --help
```

## 使い方

### 基本的な使用方法

```bash
# プロジェクトの課題をバックアップ
backlog-backup --domain example.backlog.com --api-key YOUR_API_KEY --project PROJECT_KEY --issues --output ./backup

# プロジェクトのすべてをバックアップ
backlog-backup --domain example.backlog.com --api-key YOUR_API_KEY --project PROJECT_KEY --all --output ./backup
```

### コマンドラインオプション

```
--version             バージョン情報を表示
-v, --verbose         詳細出力を有効化
--domain DOMAIN       Backlogドメイン（例：'example.backlog.com'）
--api-key API_KEY     Backlog APIキー
--project PROJECT     バックアップするBacklogプロジェクトキー
--output OUTPUT, -o OUTPUT
                      バックアップの出力ディレクトリ（デフォルト：'./backup'）
--issues              プロジェクトの課題をバックアップ
--wiki                プロジェクトのWikiをバックアップ
--files               プロジェクトのファイルをバックアップ
--git                 Gitリポジトリをバックアップ
--svn                 Subversionリポジトリをバックアップ
--all                 すべてをバックアップ
```

### Docker Composeの使用

1. `docker-compose.yml`ファイルを編集してパラメータを含める
2. バックアップを実行：

```bash
docker-compose up
```

## ディレクトリ構造

バックアップツールは以下のディレクトリ構造を作成します：

```
output_directory/
└── project_key/
    ├── issues/
    │   ├── issue_list.csv
    │   ├── ISSUE-1.json
    │   ├── ISSUE-2.json
    │   └── attachments/
    │       └── ISSUE-1/
    │           └── attachment1.png
    ├── wiki/
    │   ├── wiki_index.json
    │   ├── Page1.json
    │   ├── Page1.md
    │   └── attachments/
    │       └── Page1/
    │           └── attachment1.png
    ├── files/
    │   └── directory_structure_mirroring_backlog
    ├── git/
    │   └── repository1/
    └── svn/
        └── repository1/
```

## ライセンス

MIT

## 参考情報

- [Backlog](https://backlog.com/ja/)
- [Backlog API](https://developer.nulab.com/ja/docs/backlog/)