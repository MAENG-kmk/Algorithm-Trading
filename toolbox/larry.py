def larry(data):
    k = 0.65

    last = data.iloc[-2]
    cur = data.iloc[-1]
    
    range = last['high'] - last['low']
    if range < last['high'] / 50:
        return None, None
    
    long_target = last["close"] + k * range
    short_target = last["close"] - k * range
    if cur["high"] > long_target:
        return "long", long_target
    elif cur["low"] < short_target:
        return "short", short_target
        
    return None, None