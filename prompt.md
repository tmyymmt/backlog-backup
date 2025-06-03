# 指示

- 要件を満たすアプリを作成してください

# 要件

## 概要

- Backlogから、プロジェクト単位でデータをバックアップするCLIアプリ
- プロジェクト内のバックアップ対象
    - 課題
        - 課題の一覧表
        - 各課題の詳細内容
    - Wiki
    - ファイル
    - Git
    - Subversion
- アクセスできる全てのプロジェクトについて下記も可能
    - 一覧表
    - 全てのプロジェクトを対象として指定

## 方針

- APIで取得できる情報はAPIで取得する
- APIでは取得できない情報はヘッドレスブラウザでスクレイピングする
    - 1秒間に1アクセスに留めること

## 環境

- 使用するバージョン
    - LTSの最新版
- 開発環境も本番環境もDockerで用意する
- OS
    - Ubuntu
- 開発言語
    - Python

## ファイル構成

- README.md
    - READMEを英語で書く
    - 本ファイルの参考情報に記載した内容も参考情報として記載する
- README_ja.md
    - READMEを日本語で書く
    - 本ファイルの参考情報に記載した内容も参考情報として記載する

## 詳細

- APIキーはオプション指定ではなく、環境変数で指定できること
- git cloneやsvn checkoutなどのリポジトリからのデータ取得時の認証にはAPIキーとは別のIDとパスワードを使用すること
- wikiについて、jsonで全情報を保存し、そのjsonのcontentを.mdファイルとして保存してください

## 参考情報

- 以下をオフィシャルの情報として参照する
    - Backlogのサービス全般
        - https://backlog.com/ja/
    - BacklogのFAQ
        - https://support-ja.backlog.com/hc/ja
    - Backlogで提供されているAPI
        - https://developer.nulab.com/ja/docs/backlog/

## 動作確認の方法

全てのプロジェクトを対象で、実際に実行して、動作確認をしてください。

以下を使用してください。
- ドメイン: XXXXXXXXXX.backlog.com
- APIキー: rep2Ua7jSQqD7cPkjHu6gePoJcPZkDBZboYgckuEryPqf3CXOu2mMKamVIh8GCec

git cloneやsvn checkoutなどのリポジトリからのデータ取得時の認証には以下を使用してください。
- ID: foobar@example.com
- PW: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

回答は日本語で。
