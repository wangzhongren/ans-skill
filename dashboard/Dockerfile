FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /opt/ans

RUN groupadd --system --gid 10001 dashboard \
    && useradd --system --uid 10001 --gid dashboard --home /nonexistent --shell /usr/sbin/nologin dashboard \
    && mkdir -p /data \
    && chown dashboard:dashboard /data

COPY --chown=dashboard:dashboard *.py *.html *.css *.js /opt/ans/dashboard/

USER dashboard
EXPOSE 8765

CMD ["python", "-m", "dashboard.server", "--cloud-state", "/data", "--listen-host", "0.0.0.0", "--port", "8765"]
