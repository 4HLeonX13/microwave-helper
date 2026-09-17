FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 只複製執行所需檔案；密鑰、歷程與 Git 資料不會進入映像檔。
COPY server.py recipes.py external_api.py index.html style.css panel_demo.js ./
COPY assets/hmr-da2713-panel.png ./assets/hmr-da2713-panel.png

EXPOSE 8000

CMD ["python", "server.py"]
