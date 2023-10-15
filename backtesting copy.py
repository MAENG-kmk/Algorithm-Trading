from toolbox.dataloader import dataloader
from toolbox.larry import larry
from toolbox.rsi import rsi
from toolbox.candle import candle
from toolbox.bolinger import bolinger
from matplotlib import pyplot as plt
import pandas as pd
import csv

class Backtesting:
    def __init__(self, data):
        self.data = data[1000:]                    # 데이터
        self.leverage = 1                   # 레버리지
        self.fee = 0.0008 * self.leverage   # 수수료
        self.stop_loss = 0.1/self.leverage  # 스탑로스 퍼센트
        self.ror = 1                        # 수익률
        self.winning_rate_history = []      # 승률 히스토리
        self.history = []                   # 트레이딩 히스토리
        self.count_result = [0, 0, 0, 0]    # long, short 승, 패 카운트. 순서대로 long win, long lose, short win, short lose
        self.state = {                      
                      "position": None,     # 진입 포지션
                      "entry_price": None,  # 진입 가격
                      "stop_loss": None     # 스탑로스
                      }
        self.mdd = 0
        
    # state 초기화 함수
    def clear_state(self):
        self.state["position"] = None
        self.state["entry_price"] = None
        self.state["stop_loss"] = None
                
    # 백테스트 실행
    def excute(self):
        for i in range(20, len(self.data) - 2):
            # 현재 진입한 포지션이 없을 때
            if self.state["position"] == None:
                ################################################################
                # 데이터 슬라이싱, 트레이딩 로직 수정하는 부분
                data = self.data[i-1:i+1]
                position, target_price = larry(data)
                ################################################################
                if position == None:        # 포지션이 결정되지 않았으면 걍 건너뜀
                    continue
                elif position == 'long':
                    self.state["position"] = position
                    self.state["entry_price"] = target_price
                    self.state["stop_loss"] = target_price * (1 - self.stop_loss)
                else:
                    self.state["position"] = position
                    self.state["entry_price"] = target_price
                    self.state["stop_loss"] = target_price * (1 + self.stop_loss)
                        
                # 현재 진입한 포지션이 롱일 때
                if self.state["position"] == "long":
                    #################################################################
                    # 포지션 정리 로직 수정하는 부분

                    #################################################################

                    if self.state["stop_loss"] > self.data.iloc[i]["low"]:    # 스탑로스보다 가격이 더 내려가면 스탑로스에서 스탑
                        ror = self.state["stop_loss"] / self.state["entry_price"] - self.fee
                        print("스탑로스맞았다")
                    else:
                        ror = self.data.iloc[i]["close"] / self.state["entry_price"] - self.fee

                    self.ror *= ror
                    self.history.append(self.ror * 100)

                    if ror > 1:
                        self.count_result[0] += 1
                        print("{} 승리, 수익률: {}, 누적 수익률: {}".format(self.state["position"], (ror-1) * 100, (self.ror-1) * 100))
                    else:
                        self.count_result[1] += 1
                        print("{} 패배, 수익률: {}, 누적 수익률: {}".format(self.state["position"], (ror-1) * 100, (self.ror-1) * 100))

                    score = int((self.count_result[0] + self.count_result[2]) / sum(self.count_result) * 1000) / 10
                    self.winning_rate_history.append(score)

                    self.clear_state()

                # 현재 진입한 포지션이 숏일 때
                elif self.state["position"] == 'short':
                    #################################################################
                    # 포지션 정리 로직 수정하는 부분

                    #################################################################

                    if self.state["stop_loss"] < self.data.iloc[i]["high"]:        # 스탑로스
                        ror = 2 - self.state["stop_loss"] / self.state["entry_price"] - self.fee
                        print("스탑로스맞았다")
                    else:    
                        ror = 2 - self.data.iloc[i]["close"] / self.state["entry_price"] - self.fee

                    self.ror *= ror
                    self.history.append(self.ror * 100)

                    if ror > 1:
                        self.count_result[2] += 1
                        print("{} 승리, 수익률: {}, 누적 수익률: {}".format(self.state["position"], (ror-1) * 100, (self.ror-1) * 100))
                    else:
                        self.count_result[3] += 1
                        print("{} 패배, 수익률: {}, 누적 수익률: {}".format(self.state["position"], (ror-1) * 100, (self.ror-1) * 100))

                    score = int((self.count_result[0] + self.count_result[2]) / sum(self.count_result) * 1000) / 10
                    self.winning_rate_history.append(score)

                    self.clear_state()
                
    # 결과
    def result(self):
        score = int((self.count_result[0] + self.count_result[2]) / sum(self.count_result) * 1000) / 10
        x = range(len(self.history))
        y = self.history
        y_ = self.winning_rate_history
        ror = "Total ror: {}%, Winning rate: {}%".format(int((self.ror - 1) * 1000) / 10, score)
        count = "Win: {}reps, {}reps | Lose: {}reps, {}reps".format(self.count_result[0], self.count_result[2], self.count_result[1], self.count_result[3])
        plt.plot(x, y, 'r')
        plt.plot(x, y_, 'b')
        plt.title(ror + "\n" + count)
        plt.legend(("ror", "winning rate"))
        plt.show()
            
# 데이터셋 불러오기
dataset = dataloader(symbol="BTC/USDT", timeframe="1d", limit=1500)
print(dataset)
# 백테스트 실행
# backtest = Backtesting(dataset)
# backtest.excute()
# backtest.result()
