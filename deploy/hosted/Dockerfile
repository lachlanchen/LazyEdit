# Build from repository root using the restrictive .dockerignore alongside this file.
FROM node:22-bookworm-slim AS web
WORKDIR /build
COPY app/package.json app/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY app/ ./
ENV EXPO_PUBLIC_API_URL="" EXPO_PUBLIC_REMOTE_STUDIO=1 LAZYEDIT_REMOTE_STUDIO=1 CI=1 NODE_OPTIONS=--max-old-space-size=2048
RUN npx expo export --platform web --max-workers 2 --output-dir /webdist

FROM node:22-bookworm-slim AS gateway
WORKDIR /opt/lazyedit
COPY studio/ ./studio/
COPY hosted/ ./hosted/
RUN chmod -R a+rX /opt/lazyedit
USER node
CMD ["node", "hosted/gateway.mjs", "/registry/gateway.json"]

FROM gateway AS provisioner
USER root
COPY --from=docker:29-cli /usr/local/bin/docker /usr/local/bin/docker
COPY --from=docker:29-cli /usr/local/libexec/docker/cli-plugins/ /usr/local/libexec/docker/cli-plugins/
USER node
CMD ["node", "hosted/provision-loop.mjs", "/registry"]

FROM node:22-bookworm-slim AS workspace
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-venv python3-dev build-essential ffmpeg handbrake-cli chromium chromium-driver \
    xvfb x11vnc novnc websockify openbox xdotool wmctrl x11-utils \
    libzbar0 libgl1 libglib2.0-0 libsndfile1 espeak-ng fonts-noto-cjk fonts-noto-color-emoji \
    ca-certificates curl opencc && rm -rf /var/lib/apt/lists/*
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY deploy/hosted/requirements.txt /tmp/requirements.txt
# CPU is portable and does not claim a shared GPU. GPU scheduling is a separate operator decision.
RUN --mount=type=cache,target=/root/.cache/pip,id=lazyedit-hosted-pip \
    pip install --upgrade pip \
 && pip install torch==2.9.1 torchaudio==2.9.1 torchvision==0.24.1 --index-url https://download.pytorch.org/whl/cpu --extra-index-url https://pypi.org/simple \
 && pip install -r /tmp/requirements.txt
WORKDIR /opt/lazyedit
COPY app.py config.py settings.py video_preprocessor.py video_rebuilder.py ./
COPY lazyedit/ ./lazyedit/
COPY agi/ ./agi/
COPY AutoPublish/ ./AutoPublish/
COPY furigana/ ./furigana/
COPY whisper_with_lang_detect/ ./whisper_with_lang_detect/
COPY vit-gpt2-image-captioning/ ./vit-gpt2-image-captioning/
COPY fonts/ ./fonts/
COPY studio/ ./studio/
COPY hosted/ ./hosted/
COPY --from=web /webdist ./webdist
RUN chmod -R a+rX /opt/lazyedit \
 && node hosted/build-web.mjs \
 && mkdir -p /state \
 && chown node:node /state \
 && ln -s /state/cache cache \
 && ln -s /state/temp temp \
 && ln -s /state/translation_logs translation_logs \
 && ln -s /state/publisher/logs AutoPublish/logs \
 && ln -s /state/publisher/temp AutoPublish/temp \
 && ln -s /state/publisher/temp_screenshot AutoPublish/temp_screenshot
USER node
ENV HOME=/state/home
CMD ["python", "hosted/entrypoint.py"]
