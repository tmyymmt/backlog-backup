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

### 認証

このツールはプロジェクトデータにアクセスするためにBacklog APIキーが必要です。さらに、GitやSubversionリポジトリをバックアップする場合は、別の認証情報が必要な場合があります。

#### APIキー
- `--api-key`パラメータまたは`BACKLOG_API_KEY`環境変数で設定
- すべての操作に必要

#### Git/SVNリポジトリ認証
- Gitには`--git-username`/`--git-password`パラメータまたは`BACKLOG_GIT_USERNAME`/`BACKLOG_GIT_PASSWORD`環境変数で設定
- SVNには`--svn-username`/`--svn-password`パラメータまたは`BACKLOG_SVN_USERNAME`/`BACKLOG_SVN_PASSWORD`環境変数で設定
- 認証が必要なリポジトリをバックアップする場合のみ必要

**セキュリティに関する注意**: セキュリティ上の理由から、パスワードやAPIキーにはコマンドライン引数ではなく環境変数の使用を推奨します。コマンドライン引数はプロセス一覧に表示される可能性があります。

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

# リポジトリバックアップでGit/SVN認証を使用
backlog-backup --domain example.backlog.com --api-key YOUR_API_KEY --project PROJECT_KEY --git --svn --git-username YOUR_GIT_USERNAME --git-password YOUR_GIT_PASSWORD --svn-username YOUR_SVN_USERNAME --svn-password YOUR_SVN_PASSWORD --output ./backup

# すべての認証に環境変数を使用
export BACKLOG_API_KEY=YOUR_API_KEY
export BACKLOG_GIT_USERNAME=YOUR_GIT_USERNAME
export BACKLOG_GIT_PASSWORD=YOUR_GIT_PASSWORD
export BACKLOG_SVN_USERNAME=YOUR_SVN_USERNAME
export BACKLOG_SVN_PASSWORD=YOUR_SVN_PASSWORD
backlog-backup --domain example.backlog.com --project PROJECT_KEY --all --output ./backup

# アクセス可能なすべてのプロジェクトをバックアップ
backlog-backup --domain example.backlog.com --api-key YOUR_API_KEY --all-projects --all --output ./backup

# 非アーカイブプロジェクトのみをバックアップ
backlog-backup --domain example.backlog.com --api-key YOUR_API_KEY --all-projects --archived-projects non-archived-only --all --output ./backup
```

### 高度な使用例

```bash
# 課題とWikiのみをバックアップ（ファイルとリポジトリは除外）
backlog-backup --domain example.backlog.com --api-key YOUR_API_KEY --project PROJECT_KEY --issues --wiki --output ./backup

# 認証付きでリポジトリを含むすべてのデータをバックアップ
backlog-backup --domain example.backlog.com --api-key YOUR_API_KEY --project PROJECT_KEY --all --git-username user@example.com --git-password yourpassword --svn-username user@example.com --svn-password yourpassword --output ./backup

# アーカイブされたプロジェクトのみを一覧表示（管理者権限が必要）
backlog-backup --domain example.backlog.com --api-key YOUR_API_KEY --list-projects --include-all-space-projects --archived-projects archived-only

# カスタムディレクトリに詳細出力付きでバックアップ
backlog-backup --domain example.backlog.com --api-key YOUR_API_KEY --project PROJECT_KEY --all --output /path/to/backup --verbose
```

### コマンドラインオプション

```
--version             バージョン情報を表示
-v, --verbose         詳細出力を有効化
--domain DOMAIN       Backlogドメイン（例：'example.backlog.com'）
--api-key API_KEY     Backlog APIキー（BACKLOG_API_KEY環境変数でも設定可能）
--git-username        Gitリポジトリ認証用のユーザー名（BACKLOG_GIT_USERNAME環境変数でも設定可能）
--git-password        Gitリポジトリ認証用のパスワード（BACKLOG_GIT_PASSWORD環境変数でも設定可能）
--svn-username        SVNリポジトリ認証用のユーザー名（BACKLOG_SVN_USERNAME環境変数でも設定可能）
--svn-password        SVNリポジトリ認証用のパスワード（BACKLOG_SVN_PASSWORD環境変数でも設定可能）
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

## トラブルシューティング

### よくある問題

#### 認証エラー
- **APIキーの問題**: APIキーが有効で、アクセスしようとするプロジェクトに必要な権限があることを確認してください。
- **リポジトリ認証**: Git/SVNリポジトリは、APIキーとは別の認証情報が必要な場合があります。

#### 権限エラー
- **管理者権限が必要**: `--include-all-space-projects`などの一部の操作には、Backlogスペースでの管理者権限が必要です。
- **プロジェクトアクセス**: バックアップしようとするプロジェクトにアクセス権があることを確認してください。

#### ネットワークとレート制限
- **APIレート制限**: ツールはBacklog APIのレート制限を自動的に処理しますが、非常に大きなプロジェクトのバックアップには時間がかかる場合があります。
- **Webスクレイピングフォールバック**: APIアクセスが制限されている場合、ツールは適切なレート制限（1秒あたり1リクエスト）でWebスクレイピングにフォールバックします。

#### ファイルとディレクトリの問題
- **出力ディレクトリ**: 出力ディレクトリが書き込み可能で、十分なディスク容量があることを確認してください。
- **大きなファイル**: 非常に大きなファイル添付のダウンロードには時間がかかる場合があります。

### デバッグモード

詳細なトラブルシューティング情報には、詳細フラグを使用してください：

```bash
backlog-backup --domain example.backlog.com --api-key YOUR_API_KEY --project PROJECT_KEY --all --verbose
```

## ディレクトリ構造

バックアップツールは以下のディレクトリ構造を作成します：

```
output_directory/
└── project_key/
    ├── issues/
    │   ├── issue_list.csv          # 全課題の概要をCSV形式で保存
    │   ├── ISSUE-1.json           # 課題の詳細データをJSON形式で保存
    │   ├── ISSUE-2.json
    │   └── attachments/
    │       └── ISSUE-1/
    │           └── attachment1.png # 課題の添付ファイル
    ├── wiki/
    │   ├── wiki_index.json        # Wikiページのインデックス
    │   ├── Page1.json             # WikiページデータをJSON形式で保存
    │   ├── Page1.md              # Wikiページ内容をMarkdown形式で保存
    │   └── attachments/
    │       └── Page1/
    │           └── attachment1.png # Wikiページの添付ファイル
    ├── files/
    │   └── directory_structure_mirroring_backlog  # 元のディレクトリ構造を維持したプロジェクトファイル
    ├── git/
    │   └── repository1/           # Gitリポジトリのクローン
    └── svn/
        └── repository1/           # SVNリポジトリのチェックアウト
```

### ファイル形式の詳細

- **課題**: 
  - `issue_list.csv`: 全課題の概要情報（ID、タイトル、ステータス、担当者など）
  - `ISSUE-{番号}.json`: コメント、添付ファイル、変更履歴を含む完全な課題データ
  - 添付ファイルは課題ごとに整理してダウンロード

- **Wiki**: 
  - `wiki_index.json`: メタデータ付きの全Wikiページのインデックス
  - `{ページ名}.json`: 内容とメタデータを含む完全なページデータ
  - `{ページ名}.md`: 読みやすいようにMarkdownとして抽出されたページ内容
  - 添付ファイルはページごとに整理してダウンロード

- **ファイル**: 元のBacklogファイル構造を保持
- **リポジトリ**: オフラインアクセス用の完全なリポジトリクローン/チェックアウト

## ライセンス

MIT-0

## 貢献

貢献を歓迎します！プルリクエストの提出をお気軽にどうぞ。大きな変更については、まず何を変更したいかを議論するためのissueを開いてください。

### 開発環境のセットアップ

1. リポジトリをクローン
2. 依存関係をインストール: `pip install -e ".[scraping,build]"`
3. テストを実行: `python -m pytest tests/`

## 参考情報

- [Backlog](https://backlog.com/ja/)
- [Backlog API](https://developer.nulab.com/ja/docs/backlog/)