def larry(data):
    k = 0.3
    
    last = data.iloc[-2]
    cur = data.iloc[-1]
    
    volAvg = 0
    for i in range(-3, -8, -1):
        vol = data.iloc[i]['volume']
        volAvg += vol / 5
    
    lastVol = last['volume']
    if lastVol > volAvg:
        return None, None
    
    larryRange = last['high'] - last['low']
    if larryRange < last['high'] / 50:
        return None, None
    
    long_target = last["close"] + k * larryRange
    short_target = last["close"] - k * larryRange
    if cur["high"] > long_target:
        return "long", long_target
    elif cur["low"] < short_target:
        return "short", short_target
        
    return None, None