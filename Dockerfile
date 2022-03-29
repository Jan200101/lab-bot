FROM python:3

ARG GL_ACCESS_TOKEN
ARG GL_SECRET

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir .

RUN lab-bot setup \
    --name="docker" \
    --access_token="$GL_ACCESS_TOKEN" \
    --secret="$GL_SECRET"

CMD [ "lab-bot", "run", "docker" ]
