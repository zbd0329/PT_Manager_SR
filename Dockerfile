# 1️⃣ Python 3.9 슬림 버전 사용
FROM python:3.9-slim

# 2️⃣ 작업 디렉토리 설정
WORKDIR /app

# 3️⃣ 기본 패키지 업데이트 및 Node.js 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 4️⃣ Node.js 의존성 설치 (최적화)
COPY package*.json ./
RUN npm install --production && rm -rf /root/.npm

# 5️⃣ Python 가상 환경 생성 및 활성화
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 6️⃣ Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 7️⃣ 정적 파일 디렉토리 생성
RUN mkdir -p app/static/css \
    && mkdir -p app/static/js/lib

# 8️⃣ node_modules에서 필요한 JS/CSS 파일 복사
RUN cp node_modules/bootstrap/dist/css/bootstrap.min.css app/static/css/ \
    && cp node_modules/bootstrap/dist/js/bootstrap.min.js app/static/js/lib/ \
    && cp node_modules/sweetalert2/dist/sweetalert2.all.min.js app/static/js/lib/

# 9️⃣ 애플리케이션 코드 복사
COPY app/ ./app/

# 🔟 포트 8000 노출
EXPOSE 8000

# 1️⃣1️⃣ 애플리케이션 실행 (uvicorn)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
