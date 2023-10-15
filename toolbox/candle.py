# 캔들 모양
def candle(df):
    if df.iloc[-1]['high'] - max(df.iloc[-1]['open'], df.iloc[-1]['close']) > abs(df.iloc[-1]['body']) * 2:
        # return "meteor" # 유성형
        return "short"
    if min(df.iloc[-1]['open'], df.iloc[-1]['close']) - df.iloc[-1]['low'] > abs(df.iloc[-1]['body']) * 2:
        # return "hammer" # 망치형
        return "long"
    return None