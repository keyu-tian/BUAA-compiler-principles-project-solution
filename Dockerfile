FROM python:3
WORKDIR /app/
COPY src requirements.txt /app/
RUN ls -l
RUN pip install -r requirements.txt
RUN echo "Kevin's here!"
