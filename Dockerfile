FROM python:3.12-alpine

RUN echo "http://dl-4.alpinelinux.org/alpine/v3.14/main" >> /etc/apk/repositories && \
    echo "http://dl-4.alpinelinux.org/alpine/v3.14/community" >> /etc/apk/repositories


RUN apk --no-cache add chromium chromium-chromedriver shadow
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

ENV APP_DIR="/app" CONFIG_DIR="/config" PUID="1000" PGID="1000" UMASK="002" TZ="Etc/UTC"
ENV PYTHONUNBUFFERED=1

RUN mkdir "${APP_DIR}" && \
    mkdir "${CONFIG_DIR}" && \
    useradd -u 1000 -U -d "${CONFIG_DIR}" -s /bin/false  manga && \
    usermod -G users manga

VOLUME ["${CONFIG_DIR}"]

COPY . ${APP_DIR}

WORKDIR ${APP_DIR}

RUN pip install --no-cache-dir -r requirements.txt


CMD [ "python", "./manga_dl.py" ]