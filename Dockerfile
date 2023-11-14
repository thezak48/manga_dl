FROM python:3.9-alpine

RUN echo "http://dl-4.alpinelinux.org/alpine/v3.14/main" >> /etc/apk/repositories && \
    echo "http://dl-4.alpinelinux.org/alpine/v3.14/community" >> /etc/apk/repositories


RUN apk --no-cache add chromium chromium-chromedriver
RUN pip install --upgrade pip

LABEL maintainer="thezak48" \
  org.opencontainers.image.created=$BUILD_DATE \
  org.opencontainers.image.url="https://github.com/thezak48/manga_dl" \
  org.opencontainers.image.source="https://github.com/thezak48/manga_dl" \
  org.opencontainers.image.version=$VERSION \
  org.opencontainers.image.revision=$VCS_REF \
  org.opencontainers.image.vendor="thezak48" \
  org.opencontainers.image.title="manga_dl" \
  org.opencontainers.image.description="manga_dl is an application to to download manga's, manhua's or manhwa's."

ENV PUID=1000
ENV PGID=1000
ENV PYTHONUNBUFFERED=1

COPY . /

RUN pip install --no-cache-dir -r requirements.txt

RUN addgroup -g $PGID appgroup && \
    adduser -D -u $PUID -G appgroup appuser && \
    mkdir -p /config && \
    chown -R appuser:appgroup /config
USER appuser

CMD [ "python", "/manga_dl.py" ]