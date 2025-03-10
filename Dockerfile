
# Python ベースイメージ
FROM python:3.10

# 作業ディレクトリを作成
WORKDIR /app

# 依存関係をコピー
COPY requirements.txt /app/

# 仮想環境を作成し、パッケージをインストール
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# アプリケーションのコードをコピー
COPY . /app/

# 環境変数を設定
ENV PATH="/opt/venv/bin:$PATH"

# サーバーを起動
CMD ["gunicorn", "math_db.wsgi:application", "--bind", "0.0.0.0:8000"]

