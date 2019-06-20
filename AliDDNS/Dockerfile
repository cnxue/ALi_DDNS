FROM python:3.6
MAINTAINER <j_tim@qq.com>
ENV TZ=Asia/Shanghai
WORKDIR /mnt/app
COPY app /mnt/app
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && pip install -r requirements.txt
CMD ["python","alidns.py"]
