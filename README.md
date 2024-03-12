# dc3client

[デジタルカーリング3](https://github.com/digitalcurling/DigitalCurling3/wiki)用のクライアントライブラリです。

問題を発見した場合、GitHubのissueに投稿してください。

## インストール

Python 3.10以上が必要です。pip経由でインストールできます。

```bash
pip install dc3client
```

## 使い方

ドキュメントは[こちら](https://kawamlab.github.io/DC3-python/)を参照してください。
また、使い方や対戦環境の構築方法は[DC3-python-template](https://github.com/kawamlab/DC3-python-template)を参照してください。


## ドキュメント更新用メモ

```sh
sphinx-quickstart docs # init
```
```sh
sphinx-apidoc -f -o ./docs/source/ ./
sphinx-build  ./docs/source/ ./docs/
```