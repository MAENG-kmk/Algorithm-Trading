from toolbox.dataloader import dataloader
from toolbox.larry import larry
from toolbox.rsi import rsi
from toolbox.candle import candle
from toolbox.bolinger import bolinger
from matplotlib import pyplot as plt


class Backtesting:
    def __init__(self, data):
        self.data = data                    # 데이터
        self.leverage = 1                   # 레버리지
        self.fee = 0.0008 * self.leverage   # 수수료
        self.stop_loss = 0.1/self.leverage  # 스탑로스 퍼센트
        self.score_long = 0
        self.score_short = 0
        self.history_long = []                   
        self.history_short = []
        self.count_result = [0, 0, 0, 0]    # long, short 승, 패 카운트. 순서대로 long win, long lose, short win, short lose
        self.state = {                      
                      "position": None,     # 진입 포지션
                      }
        
    # state 초기화 함수
    def clear_state(self):
        self.state["position"] = None
        
    # 포지션 결정 함수
    def position(self, data):
        a = bolinger(data)
        if a == "long" and rsi(data) == "long":
            return "long"
        elif a == "short" and rsi(data) == "short":
            return "short"
        else:
            return None
        
    # 예측 실행
    def excute(self):
        for i in range(20, len(self.data) - 2):
            # 현재 진입한 포지션이 없을 때
            if self.state["position"] == None:
                ################################################################
                # 데이터 슬라이싱, 트레이딩 로직 수정하는 부분
                data = self.data[i - 18:i+1]
                position = self.position(data)
                ################################################################
                if position == None:        # 포지션이 결정되지 않았으면 걍 건너뜀
                    continue
                else:
                    self.state["position"] = position
                        
            # 현재 진입한 포지션이 롱일 때
            elif self.state["position"] == "long":
                if self.data.iloc[i]["body"] > 0:
                    self.count_result[0] += 1
                    self.score_long += 1
                else:
                    self.count_result[1] += 1
                    self.score_long -= 1
                    
                self.history_long.append(self.score_long)
                self.history_short.append(self.score_short)
                
                self.clear_state()
                
            # 현재 진입한 포지션이 숏일 때
            else:
                if self.data.iloc[i]["body"] < 0:
                    self.count_result[2] += 1
                    self.score_short += 1
                else:
                    self.count_result[3] += 1
                    self.score_short -= 1
                    
                self.history_long.append(self.score_long)
                self.history_short.append(self.score_short)

                self.clear_state()
                
    # 결과
    def result(self):
        score = int((self.count_result[0] + self.count_result[2]) / sum(self.count_result) * 1000) / 10
        x1 = range(len(self.history_long))
        y1 = self.history_long
        x2 = range(len(self.history_short))
        y2 = self.history_short
        count = "Long Win: {}, Long Lose: {} \n Short Win: {}, Short Lose: {}".format(self.count_result[0], self.count_result[1], self.count_result[2], self.count_result[3])
        plt.plot(x1, y1, 'r')
        plt.plot(x2, y2, 'b')
        plt.title(count + "\n" + "Winning rate: {}".format(score))
        plt.legend(("long", "short"))
        plt.show()

            
# 데이터셋 불러오기
dataset = dataloader(symbol="BTC/USDT", timeframe="4h", limit=1500)
# 백테스트 실행
backtest = Backtesting(dataset)
backtest.excute()
backtest.result()
