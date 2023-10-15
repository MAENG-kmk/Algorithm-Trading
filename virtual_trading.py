import ccxt
import time
from toolbox.dataloader import dataloader
from toolbox.trade_tool import *
from telegram.ext import CommandHandler, Updater

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

#레버리지 설정
markets = binance.load_markets()
symbol = "BTC/USDT"
market = binance.market(symbol)
leverage = 1

resp = binance.fapiPrivate_post_leverage({
    'symbol': market['id'],
    'leverage': leverage
})

balance = binance.fetch_balance()
usdt = balance['free']['USDT']

messeage = "start trading"
send_message(messeage)
print(messeage)

state = {
    'position': None,
    'amount': 0,
    'balance': 1000000,
    'enterPrice': 0,
    'win': 0,
    'lose': 0,
    'cutPrice': None,
}

#텔레그램 명령어
tele_token = "5210226721:AAG95BNFRPXRME5MU_ytI_JIx7wgiW1XASU"
chat_id = 5135122806

updater = Updater(token=tele_token, use_context=True)
dispatcher = updater.dispatcher

stopAndGO = 1

def check(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="정상 작동중")

def stop_trade(update, context):
    global stopAndGO
    context.bot.send_message(chat_id=update.effective_chat.id, text="시스템 중지, 재시작 명령어: continue")
    stopAndGO = 0

def continue_trade(update, context):
    global stopAndGO
    context.bot.send_message(chat_id=update.effective_chat.id, text="시스템 재가동")
    stopAndGO = 1
    

check_handler = CommandHandler('check', check)
stop_trade_handler = CommandHandler('stop', stop_trade)
continue_trade_handler = CommandHandler('continue', continue_trade)
dispatcher.add_handler(check_handler)
dispatcher.add_handler(stop_trade_handler)
dispatcher.add_handler(continue_trade_handler)

updater.start_polling()

while True:
    try:
        if stopAndGO == 0:
            while stopAndGO == 0:
                time.sleep(1)
        
        ticker = binance.fetch_ticker("BTC/USDT")
        cur_price = ticker['last']
        print(state['position'])
        if state['position'] == None:
            data = dataloader(symbol="BTC/USDT", timeframe="4h", limit=12 * 24*20)
            balance = binance.fetch_balance()
            usdt = balance['free']['USDT']
            state['balance'] = usdt
            
            predictor = PredictNextCandle(data)
            predict = predictor.excute()
            enter_position(binance, cur_price, state, predict)
            time.sleep(5)
            
        else:
            if state['position'] == 'long':
                if state['cutPrice'] > cur_price:
                    close_position(binance, cur_price, state)
                    while True:
                        newData = dataloader(symbol="BTC/USDT", timeframe="4h", limit=12 * 24*20)
                        if newData.iloc[-2]['body'] - data.iloc[-2]['body'] != 0:
                            break
                        else:
                            time.sleep(10)                    
            elif state['position'] == 'short':
                if state['cutPrice'] < cur_price:
                    close_position(binance, cur_price, state)
                    while True:
                        newData = dataloader(symbol="BTC/USDT", timeframe="4h", limit=12 * 24*20)
                        if newData.iloc[-2]['body'] - data.iloc[-2]['body'] != 0:
                            break
                        else:
                            time.sleep(10)    
                            
            newData = dataloader(symbol="BTC/USDT", timeframe="4h", limit=12 * 24*20)
            if newData.iloc[-2]['body'] - data.iloc[-2]['body'] != 0:
                predictor = PredictNextCandle(newData)
                predict = predictor.excute()
                if predict == 'up' and state['position'] == "long":
                    messeage = "롱포지션 유지"
                    send_message(messeage)
                    data = dataloader(symbol="BTC/USDT", timeframe="4h", limit=12 * 24*20)
                elif predict == 'down' and state['position'] == "short":
                    messeage = "숏포지션 유지"
                    send_message(messeage)
                    data = dataloader(symbol="BTC/USDT", timeframe="4h", limit=12 * 24*20)
                else:
                    close_position(binance, cur_price, state)
                    messeage = "승리 횟수:{}, 패배 횟수: {}".format(state['win'], state['lose'])
                    send_message(messeage)
                    messeage = "--------------------------------------\n--------------------------------------\n--------------------------------------"
                    send_message(messeage)
            else:
                time.sleep(1)
            
    except Exception as e:
        send_message(("에러메세지: {}".format(e)))
        print("에러메세지: {}".format(e))