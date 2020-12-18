FROM python:3
# RUN pip install xxx yyy zzz -i https://pypi.tuna.tsinghua.edu.cn/simple
WORKDIR /app/
COPY src /app/