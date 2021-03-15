fork元のREADME

# 3行要約データセット

WebDB Forum 2017 の「TL;DR 3行要約に着目したニューラル文書要約」という発表論文内で構築されたデータセットです．  
論文の内容に関しては，学位論文「[文書構造に着目したニューラル文書要約](http://cl.sd.tmu.ac.jp/~komachi/thesis/2017-mthesis-kodaira.pdf)」を参照してください．  
または，こちらの動画[3行要約に着目したニューラル文書要約](https://youtu.be/cEDj0WgkTbM)@youtube参照．    


## 概要

LivedoorNews（ [https://news.livedoor.com/](https://news.livedoor.com/) ）からクロールしてデータセットの構築を行います．
`data/`以下にあるcsvファイルにサイトの情報が記述されています．  
各列の詳細は以下，

1列目は記事の公開年  
2列目は記事の公開月  
3列目は記事のカテゴリ  
4列目は記事のID  
4列目はタイプラベル（0が並列，1が直列）  

記事IDからサイトのURLが作成できます．
3行要約が載っているURLは  
```http://news.livedoor.com/topics/detail/xxxxxxxx/```  
記事が載っているURLは  
```http://news.livedoor.com/article/detail/xxxxxxxx/```  
`xxxxxxxx`にIDを入れてください．


**−−−−−−−−−−−−−−− ↓ added by kSatoN −−−−−−−−−−−−−−−**

## フォークでの追加内容

データを整形し，クロールし，~~LSTMモデルを作成する~~Pythonスクリプトを追加しました。また，その動作確認用にdata/develop.csvから最初の100件を抜き出したdata/debug.csvを用意しました。


## よくわからなかったもの

次のものに関してはフォーク元の仕様がよくわからなかったため，テキトーに処理しています。

- データのカテゴリーの数値の意味
- train.csvの記事IDにおいて「.」「.j」「j」「s」などが付いているものがあったが，それらの意味


## Pythonスクリプトの実行

### 仮想環境構築

Python自体の環境構築はできているものとします（ターミナルで`python3`コマンドを利用できる状態）。なおPython 3.6以降が必要です。このリポジトリーの直下のディレクトリーに移動し，次のコマンドを実行すると仮想環境が構築されます（%より後を入力してください）。

```sh
% python3 -m venv ./Python-venv
```

仮想環境の入り方・抜け方は詳しくは書きませんが，それぞれ `. ./Python-venv/bin/activate`，`deactivate` でできます。

仮想環境に入った状態（コマンドラインの最初に「(Python-venv)」と表示された状態）で，次のコマンドを実行し，必要なライブラリーをインストールします。

```sh
(Python-venv) % pip3 install --upgrade pip
(Python-venv) % pip3 install wheel
(Python-venv) % pip3 install -r ./Python-venv/requirements.txt
```

~~さらに，PyTorchのインストールが必要です。仮想環境に入っている状態で，PyTorchのサイト（[https://pytorch.org/get-started/locally/](https://pytorch.org/get-started/locally/)）の「Start Locally」で，次のように選択したときに表の最後の「Run this Command」に表示されるコマンドを実行してください。~~

- **PyTorch Build**：Stable
- **Your OS**：（お使いのOSを選択）
- **Package**：Pip
- **Language**：Python
- **CUDA**：（GeForceのグラボを使っている場合 → （CUDAのバージョン），そうでない or 分からない → 「NONE」）


### 実行

#### (1) 元のデータセット → JSON形式へ

元のデータセットからLivedoorNewsインスタンスを生成し，その内部状態の配列をJSONとして書き出します。出力先は「Python-venv/dataset/crawl」ディレクトリーです。

```sh
(Python-venv) % python3 ./Python-venv/sources/csv_to_json.py
```

#### (2) クロールしてタイトル，要約，本文を取得

(1)で生成したJSONを基にクロールし，LivedoorNewsインスタンスにタイトル，要約，本文の情報を付加し，1記事（インスタンス）をひとつのJSONファイルとして書き出します。「Python-venv/dataset/crawl/（debug ／ develop ／ test ／ train）」ディレクトリーに「（ID）.json」として書き出します。

事前準備：「Python-venv/conf/User-Agent.txt」でユーザーエージェント文字列を指定できます。ブラウザーと全く同じにするような悪用はご遠慮ください。

ログ出力のカウントの意味は次のとおりです。

- エラー：HTTPエラー（ステータスコード200番台以外），HTML解析エラー（返ってきたHTMLの構造が他のものと違う記事），削除済みの記事，JSON書き込み失敗の合計回数
- 重大エラー：JSON書き込み失敗（クローリングは成功）の回数
- 削除済み：HTTP通信は成功したが，本文が削除されていた記事の数

```sh
(Python-venv) % python3 ./Python-venv/sources/crawl.py
```

#### ~~(3) LSTMで学習~~

正しく学習できていなかったため，commitしていません。

```sh
(Python-venv) % python3 ./Python-venv/sources/learn.py
```


## 注意事項

すでに削除されている記事が多く見られました（2021年1月現在で4割ほど）。クロール時に削除されている記事は無視するようにしています。今後も削除される記事が増える可能性があることを考えると，データ量の観点からも，このデータをそのまま利用せず，新しくデータセットを作成したほうが良いかもしれません。

入力に対する例外処理をしていません。クロール対象や開始インデックス・終了インデックスで規定以外の入力をすると例外で処理が止まったり，異常な動作をする可能性があります。
