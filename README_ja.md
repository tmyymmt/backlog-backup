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

### スタンドアロン実行ファイルの使用

Windows、macOS、Linuxプラットフォーム向けのスタンドアロン実行ファイルが利用できます。これらの実行ファイルは別途Pythonのインストールが不要です。

#### ダウンロード

[リリースページ](https://github.com/tmyymmt/backlog-backup/releases)からご使用のプラットフォームに適した実行ファイルをダウンロードしてください。

#### 使用方法

Windows:
```
backlog-backup-win.exe --domain example.backlog.com --api-key YOUR_API_KEY --project PROJECT_KEY --all
```

macOS/Linux:
```
chmod +x backlog-backup-macos  # 実行可能にする（初回のみ）
./backlog-backup-macos --domain example.backlog.com --api-key YOUR_API_KEY --project PROJECT_KEY --all
```

### 独自の実行ファイルをビルド

スタンドアロン実行ファイルをビルドするには：

```bash
# リポジトリをクローン
git clone https://github.com/tmyymmt/backlog-backup.git
cd backlog-backup

# 必要な依存関係をインストール
pip install -e ".[build]"

# 実行ファイルをビルド
python build_executable.py

# 単一ファイルの実行ファイルの場合
python build_executable.py --one-file

# コンソールウィンドウなしのWindows実行ファイル
python build_executable.py --no-console

# 出力名と場所をカスタマイズ
python build_executable.py --name カスタム名 --output-dir ./my-builds
```

実行ファイルはデフォルトでは`dist`ディレクトリに作成されます。

#### 高度なカスタマイズ

ビルドプロセスの高度なカスタマイズには、含まれている`backlog-backup.spec`ファイルを変更し、PyInstallerを直接使用できます：

```bash
# PyInstallerをインストール
pip install pyinstaller>=5.8.0

# backlog-backup.specファイルを編集してビルドをカスタマイズ
# 次にspecファイルを使用してビルド
pyinstaller backlog-backup.spec
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

# APIキーを環境変数として実行
docker run -v $(pwd)/backup:/app/backup -e BACKLOG_API_KEY=YOUR_API_KEY backlog-backup --domain example.backlog.com --project PROJECT_KEY --all
```

## 使い方

### 基本的な使用方法

```bash
# アクセス可能なすべてのプロジェクトを一覧表示
backlog-backup --domain example.backlog.com --api-key YOUR_API_KEY --list-projects

# スペース内のすべての非アーカイブプロジェクトを一覧表示（管理者権限が必要）
backlog-backup --domain example.backlog.com --api-key YOUR_API_KEY --list-projects --include-all-space-projects --archived-projects non-archived-only

# プロジェクトの課題をバックアップ
backlog-backup --domain example.backlog.com --api-key YOUR_API_KEY --project PROJECT_KEY --issues --output ./backup

# プロジェクトのすべてをバックアップ
backlog-backup --domain example.backlog.com --api-key YOUR_API_KEY --project PROJECT_KEY --all --output ./backup

# 環境変数からAPIキーを使用
export BACKLOG_API_KEY=YOUR_API_KEY
backlog-backup --domain example.backlog.com --project PROJECT_KEY --all --output ./backup

# アクセス可能なすべてのプロジェクトをバックアップ
backlog-backup --domain example.backlog.com --api-key YOUR_API_KEY --all-projects --all --output ./backup

# 非アーカイブプロジェクトのみをバックアップ
backlog-backup --domain example.backlog.com --api-key YOUR_API_KEY --all-projects --archived-projects non-archived-only --all --output ./backup
```

### コマンドラインオプション

```
--version             バージョン情報を表示
-v, --verbose         詳細出力を有効化
--domain DOMAIN       Backlogドメイン（例：'example.backlog.com'）
--api-key API_KEY     Backlog APIキー（BACKLOG_API_KEY環境変数でも設定可能）
--project PROJECT     バックアップするBacklogプロジェクトキー
--all-projects        アクセス可能なすべてのプロジェクトをバックアップ
--list-projects       アクセス可能なすべてのプロジェクトを一覧表示
--include-all-space-projects
                      ユーザーがアクセス可能なプロジェクトだけでなく、スペース内のすべてのプロジェクトを対象にする（管理者権限が必要）
--archived-projects {all,archived-only,non-archived-only}
                      プロジェクトのアーカイブ状態でフィルタリング（デフォルト: 'all'）
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

MIT-0

## 参考情報

- [Backlog](https://backlog.com/ja/)
- [Backlog API](https://developer.nulab.com/ja/docs/backlog/)