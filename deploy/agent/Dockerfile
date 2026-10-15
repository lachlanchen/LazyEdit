FROM node:22-bookworm-slim
ARG AGINTI_VERSION=0.20.331
ARG CODEX_VERSION=0.162.1
RUN apt-get update && apt-get install -y --no-install-recommends python3 ca-certificates git \
 && rm -rf /var/lib/apt/lists/* \
 && npm install -g --ignore-scripts @lazyingart/agintiflow@${AGINTI_VERSION} @openai/codex@${CODEX_VERSION} \
 && npm cache clean --force
WORKDIR /opt/studio
COPY --chmod=444 studio/agent_plan.py studio/agent_sandbox.py ./
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 HOME=/tmp
USER 1000:1000
CMD ["python3", "/opt/studio/agent_sandbox.py"]
