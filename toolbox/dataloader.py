import ccxt
import numpy as np
import pandas as pd

def dataloader(symbol="BTC/USDT", timeframe="1h", limit=1500):
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
    symbol = symbol
    btc = binance.fetch_ohlcv(
            symbol=symbol,
            timeframe=timeframe, 
            since=None, 
            limit=limit
        )
    df = pd.DataFrame(data=btc, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
    df['body'] = df['close'] - df['open']
    df['size'] = df['high'] - df['low'] 
    df['middle'] = df['close'].rolling(window=20).mean()
    std = df['close'].rolling(20).std(ddof=0)
    df['upper'] = df['middle'] + 2 * std
    df['lower'] = df['middle'] - 2 * std
    
    df.set_index('datetime', inplace=True)
    
    return df

