# Basic Image Environment
FROM python:latest

RUN pip install numpy 

RUN pip install --upgrade pip

RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
  tar -xvzf ta-lib-0.4.0-src.tar.gz && \
  cd ta-lib/ && \
  ./configure --prefix=/usr && \
  make && \
  make install

RUN rm -R ta-lib ta-lib-0.4.0-src.tar.gz

# 指定 Image 中的工作目錄
WORKDIR /FlaskServer

# 將 Dockerfile 所在目錄下的所有檔案複製到 Image 的工作目錄 /FlaskServer 底下
ADD . /FlaskServer

# 在 Image 中執行的指令：安裝 requirements.txt 中所指定的 dependencies
RUN pip install -r requirements.txt

EXPOSE 5010/tcp 5000/tcp

# Container 啟動指令：Container 啟動後通過 python 運行 runserver.py
CMD ["python", "runserver.py"]