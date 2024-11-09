FROM quay.io/unstructured-io/base-images:wolfi-base-latest AS base

USER root

WORKDIR /app

COPY ./requirements.txt requirements.txt
COPY main.py main.py
COPY docs/ docs/

RUN chown -R notebook-user:notebook-user /app && \
  apk add font-ubuntu git && \
  fc-cache -fv && \
  ln -s /usr/bin/python3.11 /usr/bin/python3 && \
  pip3 install -r requirements.txt

USER notebook-user

ENV PATH="${PATH}:/home/notebook-user/.local/bin"
ENV TESSDATA_PREFIX=/usr/local/share/tessdata

CMD ["python3", "main.py"]
