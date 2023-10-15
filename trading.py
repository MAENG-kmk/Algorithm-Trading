import ccxt
import pandas as pd
import datetime
import time
import math
import telegram

api_key = "w6wGRNsx88wZHGNi6j2j663hyvEpDNHrLE6E6UntucPkJ4Lqp8P4rasX1lAx9ylE"
secret = "EtbkzmsRjVw2NHqis4rLlIvrZN4HVfHp77Qdzd8wG1AbyoXttLV8EgS7z9Efz9ut"

binance = ccxt.binance(config={
    'apiKey': api_key, 
    'secret': secret,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})

def larry(ticker, cur_price):
  ohlcv = binance.fetch_ohlcv(
    symbol=ticker,
    timeframe='1d', 
    since=None, 
    limit=2
  )
  df = pd.DataFrame(data=ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
  df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
  
  k = 0.5
  
  last = df.iloc[0]
  
  range = last['high'] - last['low']
  long_target = last["close"] + k * range
  short_target = last["close"] - k * range
  if cur_price > long_target:
      return "long"
  elif cur_price < short_target:
      return "short"

def cal_amount(usdt_balance, cur_price):
    portion = 1
    usdt_trade = usdt_balance * portion
    amount = math.floor((usdt_trade * 1000)/cur_price) / 1000
    return amount 
  
def buy_order(binance, ticker, amount):
    binance.create_market_buy_order(symbol=ticker, amount=amount)
    
def sell_order(binance, ticker, amount):
    binance.create_market_sell_order(symbol=ticker, amount=amount)  
    
def send_message(text):
    tele_token = "5210226721:AAG95BNFRPXRME5MU_ytI_JIx7wgiW1XASU"
    chat_id = 5135122806
    bot = telegram.Bot(token = tele_token)
    bot.sendMessage(chat_id = chat_id, text = text)

tickers = binance.fetch_tickers()
portfolio = {}

balance = binance.fetch_balance()
balance = balance['free']['USDT']
bullets = [balance / 5] * 5

send_message("트레이딩 시작, 잔액: {}$".format(balance))
while True:
  try:
    if len(portfolio) >= 5:
      while True:
        hour_now = datetime.datetime.now().hour
        if hour_now == 9:
          for ticker in portfolio:
            if portfolio[ticker][0] == "long":
              sell_order(binance, ticker, portfolio[ticker][1])
            else:
              buy_order(binance, ticker, portfolio[ticker][1])
          portfolio = {}
          balance = binance.fetch_balance()
          balance = balance['free']['USDT']
          bullets = [balance / 5] * 5
          send_message("포지션 정리, 잔액: {}$".format(balance))
          break
        time.sleep(60)
        
    else:
      for ticker in tickers:
        if ticker.endswith('USDT') and ticker not in portfolio:
          ticker_data = binance.fetch_ticker(ticker)
          cur_price = ticker_data['last']
          position = larry(ticker, cur_price)
          if position == "long":
            amount = cal_amount(bullets.pop(), cur_price)
            buy_order(binance, ticker, amount)
            portfolio[ticker] = ["long", amount]
            send_message("{} long 포지션 진입".format(ticker))
            if len(portfolio) >= 5:
              break
          elif position == "short":
            amount = cal_amount(bullets.pop(), cur_price)
            sell_order(binance, ticker, amount)
            portfolio[ticker] = ["short", amount]
            send_message("{} short 포지션 진입".format(ticker))
            if len(portfolio) >= 5:
              break
      time.sleep(60)
      
  except Exception as e:
    print(e)
    send_message("에러메시지: {}".format(e))
    