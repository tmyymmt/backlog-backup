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
- README_ja.md
    - READMEを日本語で書く

## 詳細

- APIキーはオプション指定ではなく、環境変数で指定できること


## 参考情報

- 以下をオフィシャルの情報として参照する
    - Backlogのサービス全般
        - https://backlog.com/ja/
    - BacklogのFAQ
        - https://support-ja.backlog.com/hc/ja
    - Backlogで提供されているAPI
        - https://developer.nulab.com/ja/docs/backlog/
