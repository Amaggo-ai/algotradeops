FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
ENV MODE=backtest STRATEGY=sma_cross SYMBOLS=AAPL,MSFT CASH=100000
CMD ["python","-m","app.main"]
