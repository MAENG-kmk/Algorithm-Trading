import telegram
import math
import time

def send_message(text):
    tele_token = "5210226721:AAG95BNFRPXRME5MU_ytI_JIx7wgiW1XASU"
    chat_id = 5135122806
    bot = telegram.Bot(token = tele_token)
    bot.sendMessage(chat_id = chat_id, text = text)
    
def cal_amount(usdt_balance, cur_price):
    portion = 0.99
    usdt_trade = usdt_balance * portion * 10
    amount = math.floor((usdt_trade * 1000000)/cur_price) / 1000000
    return amount 
    
def buy_order(binance, amount):
    binance.create_market_buy_order(symbol="BTC/USDT", amount=amount)
    
def sell_order(binance, amount):
    binance.create_market_sell_order(symbol="BTC/USDT", amount=amount)    

def enter_position(binance, cur_price, state, predict):
    if predict == "up":
        balance = state['balance']
        amount = cal_amount(balance, cur_price)
        state['amount'] = amount
        buy_order(binance, amount)
        state['position'] = "long"
        state['enterPrice'] = cur_price
        state['cutPrice'] = cur_price * 0.99
        
        send_message("롱 포지션 진입, 수량:{}".format(amount))
        
    elif predict == "down":
        balance = state['balance']
        amount = cal_amount(balance, cur_price)
        state['amount'] = amount
        sell_order(binance, amount)
        state['position'] = "short"
        state['enterPrice'] = cur_price        
        state['cutPrice'] = cur_price * 1.01
        
        send_message("숏 포지션 진입, 수량:{}".format(amount))   
        
def close_position(binance, cur_price, state):
    if state['position'] == "long":
        sell_order(binance, state['amount'])
        time.sleep(1)
        balance = binance.fetch_balance()
        usdt = balance['free']['USDT']
        state['balance'] = usdt
        state['amount'] = 0
        state['position'] = None
        state['cutPrice'] = None
        if cur_price > state['enterPrice']:
            state['win'] += 1
            send_message("롱포지션 정리, 결과: 승, 잔액:{:.2f}USDT".format(state['balance']))
        else:
            state['lose'] += 1
            send_message("롱포지션 정리, 결과: 패, 잔액:{:.2f}USDT".format(state['balance']))         
        state['enterPrice'] = 0
        
    elif state['position'] == "short":
        buy_order(binance, state['amount'])
        time.sleep(1)
        balance = binance.fetch_balance()
        usdt = balance['free']['USDT']
        state['balance'] = usdt
        state['amount'] = 0
        state['position'] = None
        state['cutPrice'] = None
        if cur_price < state['enterPrice']:
            state['win'] += 1
            send_message("숏포지션 정리, 결과: 승, 잔액:{:.2f}USDT".format(state['balance']))
        else:
            state['lose'] += 1
            send_message("숏포지션 정리, 결과: 패, 잔액:{:.2f}USDT".format(state['balance'])) 
        state['enterPrice'] = 0