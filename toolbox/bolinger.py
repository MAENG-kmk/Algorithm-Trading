def bolinger(data):
    cur = data.iloc[-1]
    first = data.iloc[-3]
    second = data.iloc[-2]
    if cur['high'] > cur['upper']:
        return 'long'
    if cur['low'] < cur['lower']:
        return 'short'
    return None