# warise-polls

[![PyPI - Version](https://img.shields.io/pypi/v/django-hatch.svg)](https://pypi.org/project/django-hatch)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-hatch.svg)](https://pypi.org/project/django-hatch)

-----

**目次**

- [詳細](#詳細)
- [インストール](#インストール)
- [アップロード](#アップロード)
- [Djangoプロジェクトに設定（テスト）](#Djangoプロジェクトに設定（テスト）)
- [License](#license)

## 詳細

このリポジトリは[Hatch](https://hatch.pypa.io/latest/)プロジェクトマネージャーを使ったDjangoプロジェクトの開発またはテスト（お試し）ツールです。

配布用としてDjangoアプリをアップロードする環境を自動構築または配布用としてアップロードされたDjangoアプリをこのDjangoプロジェクトに組み込んでテストすることができます。

使用方法は以下からご覧ください。

## インストール

実行環境は「Windows Sybsystem for Linux 2」のUbuntuです。


Pythonの環境は任意です。

私はpyenvを使用してPython3.7の環境を設定しています。

```console
$ pyenv local 3.7

$ python3 --version
Python 3.7.0
```

仮想環境を作成して有効にし、`Hatch`をインストールします。

```console
$ python3 -m venv .venv && . .venv/bin/activate

$ pip install --upgrade pip

$ pip install hatch keyrings.alt
```

リポジトリを落として「wagtail-polls」ディレクトリに入ります。

```console
$ git clone https://github.com/kenno-warise/wagtail-polls.git

$ cd wagtail-polls
```

hatchコマンドでデータベースの作成・スーパーユーザーの作成・サーバーの起動を行います。

```console
$ hatch run makemigrations polls && hatch run migrate

$ hatch run createsuperuser

$ hatch run runserver
```

ショートカットとしてHatchの「run」コマンドで実行できるDjangoのコマンドは`pyproject.toml`の「tool.hatch.envs.default.scripts」テーブルによって登録しています。

```toml
[tool.hatch.envs.default.scripts]
makemigrations = "python3 manage.py makemigrations {args}"
migrate = "python3 manage.py migrate"
createsuperuser = "python3 manage.py createsuperuser"
runserver = "python3 manage.py runserver"
startapp = "python3 manage.py startapp {args}"
shell = "python3 manage.py shell"
test = "python3 manage.py test {args}"
cov = "coverage run --include=polls/* --omit=polls/test*,polls/__init__.py,polls/migrations manage.py test {args}"
cov-report = "coverage report -m"
```

## アップロード

Hatchの「version」コマンドでDjangoアプリのバージョン情報を確認できます。

```console
$ hatch version
0.0.1
```

DjangoアプリをパッケージングしてPyPIにアップロードする。

`pyproject.toml`に配布するファイルと配布しないファイルを設定できます。

```toml
[tool.hatch.build]
include = ["polls/*"] # templatesとstaticも含まれます。
exclude = ["polls/migrations/*"]
```

上記以外にあれば追記します。

バージョンを更新する場合は「version」コマンドを実行します。

```console
$ hatch version micro
Old: 0.0.1
New: 0.0.2
```

ビルドを実行します。

```console
$ hatch build
```

アーティファクトを公開します。

```console
$ hatch publish
```

## Djangoプロジェクトに設定（テスト）

アップロード済みのDjangoアプリを設定します。

`myproject/settings.py`

`pkg`の部分をDjangoアプリ名に当てはめます。

```python
INSTALLED_APPS = [
    ...,
    "polls",
    "wagtail.contrib.routable_page",
]
```


`requirements.txt`

`pkg`の部分をDjangoアプリ名に当てはめます。

```
...
warise-polls
```

必要であればマイグレートとスーパーユーザーを作成します。

```console
$ python manage.py makemigrations polls

$ python manage.py migrate

$ python manage.py createsuperuser
```

サーバーを起動します。

```console
$ hatch run runserver
```

## License

`warise-polls` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
