import ccxt
import pandas as pd
import datetime
import time
import math
import telegram
from telegram.ext import CommandHandler, Updater

tele_token = "5210226721:AAG95BNFRPXRME5MU_ytI_JIx7wgiW1XASU"
chat_id = 5135122806

updater = Updater(token=tele_token, use_context=True)
dispatcher = updater.dispatcher

def send_message(text):
    bot = telegram.Bot(token = tele_token)
    bot.sendMessage(chat_id = chat_id, text = text)

def check(update, context):
  global portfolio, binance
  message = ""
  for ticker in portfolio:
    text = "{}: {}포지션, 수량:{} \n\n".format(ticker, portfolio[ticker][0], portfolio[ticker][1])
    message += text
  balance = binance.fetch_balance()['total']['USDT']
  message += "\n\n현재 평가 잔고: {:.1f}".format(balance)
  context.bot.send_message(chat_id=update.effective_chat.id, text=message)
  
def stop_trade(update, context):
    global isRunning
    context.bot.send_message(chat_id=update.effective_chat.id, text="시스템 중지, 재시작 명령어: start")
    isRunning = False

def start_trade(update, context):
    global isRunning, balance, bullet, tickers, portfolio
    balance = binance.fetch_balance()
    balance = balance['free']['USDT']
    bullet = balance / 5
    tickers = binance.fetch_tickers()
    portfolio = {}
    send_message("트레이딩 시작, 잔액: {:.1f}$".format(balance))
    
    isRunning = True
    context.bot.send_message(chat_id=update.effective_chat.id, text="시스템 재가동")
    

check_handler = CommandHandler('check', check)
stop_trade_handler = CommandHandler('stop', stop_trade)
start_trade_handler = CommandHandler('start', start_trade)

dispatcher.add_handler(check_handler)
dispatcher.add_handler(stop_trade_handler)
dispatcher.add_handler(start_trade_handler)

updater.start_polling()


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
  
  k = 0.65
  
  last = df.iloc[0]
  
  range = last['high'] - last['low']
  if range < last['high'] / 50:
      return None
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



isRunning = False

balance = binance.fetch_balance()
balance = balance['free']['USDT']
bullet = balance / 5
tickers = binance.fetch_tickers()
portfolio = {}

while True:
  while isRunning:
    try:
      if len(portfolio) >= 5:
        while isRunning:
          hour_now = datetime.datetime.now().hour
          minute = datetime.datetime.now().minute
          if hour_now == 9 and minute <= 1:
            closeMessage = ""
            totalRor = 0
            for ticker in portfolio:
              ticker_data = binance.fetch_ticker(ticker)
              cur_price = ticker_data['last']
              percentage = cur_price / portfolio[ticker][2]
              if portfolio[ticker][0] == "long":
                ror = (percentage - 1 - 0.0008) * 100
                totalRor += ror / 5
                sell_order(binance, ticker, portfolio[ticker][1])
                closeMessage += "{} long 포지션 정리 \n수익률: {:.2f}% \n\n".format(ticker, ror)
              else:
                ror = (1 - percentage - 0.0008) * 100
                totalRor += ror / 5
                buy_order(binance, ticker, portfolio[ticker][1])
                closeMessage += "{} short 포지션 정리 \n수익률: {:.2f}% \n\n".format(ticker, ror)
            portfolio = {}
            balance = binance.fetch_balance()
            balance = balance['free']['USDT']
            bullet = balance / 5
            closeMessage += "\n잔액: {:.1f}$, 총 수익률: {:.2f}%".format(balance, totalRor)
            send_message(closeMessage)
            break
          time.sleep(60)

      else:
        for ticker in tickers:
          if ticker.endswith('USDT') and ticker not in portfolio:
            ticker_data = binance.fetch_ticker(ticker)
            cur_price = ticker_data['last']
            position = larry(ticker, cur_price)
            if position == "long":
              market = binance.market(ticker)
              binance.fapiPrivate_post_leverage({
                'symbol': market['id'],
                'leverage': 1
              })
              amount = cal_amount(bullet, cur_price)
              buy_order(binance, ticker, amount)
              portfolio[ticker] = ["long", amount, cur_price]
              send_message("{} long 포지션 진입".format(ticker))
              if len(portfolio) >= 5:
                break
            elif position == "short":
              market = binance.market(ticker)
              binance.fapiPrivate_post_leverage({
                'symbol': market['id'],
                'leverage': 1
              })
              amount = cal_amount(bullet, cur_price)
              sell_order(binance, ticker, amount)
              portfolio[ticker] = ["short", amount, cur_price]
              send_message("{} short 포지션 진입".format(ticker))
              if len(portfolio) >= 5:
                break
        time.sleep(60)

    except Exception as e:
      print(e)
      send_message("에러메시지: {}".format(e))   
  time.sleep(60)