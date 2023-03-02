from re import A
from subprocess import call
from matplotlib.pyplot import switch_backend
from numpy import round_
from game.players import BasePokerPlayer

Poker_Coler = ['S', 'H', 'C', 'D'] # 黑桃、紅心、方塊、梅花 = 0, 1, 2, 3
Poker_Number = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']

def number(x: str):
    if x == 'A':
        return 15
    elif x == 'T':
        return 10
    elif x == 'J':
        return 11
    elif x == 'Q':
        return 12
    elif x == 'K':
        return 13
    else:
        return int(x)

def suit(x: str):
    if x == 'S':
        return 0
    elif x == 'H':
        return 1
    elif x == 'C':
        return 2
    else:
        return 3    

def analysis(numberList: list, Su: bool, ratio: int):
    table = [[85,68,67,66,66,64,63,63,62,62,61,60,59],[66,83,64,64,63,61,60,59,58,58,57,56,55],[65,62,80,61,61,59,58,56,55,55,54,53,52],[65,62,59,78,59,57,56,54,53,52,51,50,50],[64,61,59,57,75,56,54,53,51,49,49,48,47],[62,59,57,55,53,72,53,51,50,48,46,46,45],[61,58,55,53,52,50,69,50,49,47,45,43,43],[60,57,54,52,50,48,47,67,48,46,45,43,41],[59,56,53,50,48,47,46,45,64,46,44,42,40],[60,55,52,49,47,45,44,43,43,61,44,43,41],[59,54,51,48,46,43,42,41,41,41,58,42,40],[58,54,50,48,45,43,40,39,39,39,38,55,39],[57,53,49,47,44,42,40,37,37,37,36,35,51]]
    NumberToIndex = [15,13,12,11,10,9,8,7,6,5,3,2]
    x, y = NumberToIndex.index(numberList[0]), NumberToIndex.index(numberList[1])
    prob = table[min(x, y)][max(x, y)] if Su else table[max(x, y)][min(x, y)]
    if prob > ratio:
        return True
    else:
        return False

def WaitToEnd(gameIndex: int, MyMoney: int, EnemyMoney: int, PotMoney: int, stage: str):
    if stage != "preflop":
        return False
    MoneyRange = MyMoney - EnemyMoney
    RestGame = 20 - gameIndex + 1
    if RestGame % 2 == 0 and MoneyRange > 15 * RestGame / 2:
        return True
    elif RestGame % 2 == 1 and MoneyRange > 10 + 15 * (RestGame - 1) / 2:
        return True
    else:
        return False

class blindGuess(BasePokerPlayer):
    # 選擇到起始的好牌就All in入場，反之則直接放棄。
    def declare_action(self, valid_actions, hole_card, round_state):
        numberFit, SuitFit = [], []
        numberFit.append(number(hole_card[0][1]))
        numberFit.append(number(hole_card[1][1]))
        SuitFit.append(suit(hole_card[0][0]))
        SuitFit.append(suit(hole_card[1][0]))
        if round_state["street"] == "preflop":
            if analysis(numberFit, SuitFit[0] == SuitFit[1], 60):
                return valid_actions[1]["action"], valid_actions[1]["amount"]
            else:
                return valid_actions[0]["action"], valid_actions[0]["amount"] 
        else:
            return valid_actions[2]["action"], valid_actions[2]["amount"]["max"]
    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        # print(round_state["action_histories"])
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        # print(winners[0]["name"])
        pass

class IWantToPass(BasePokerPlayer):  # Do not forget to make parent class as "BasePokerPlayer"
    raised = False
    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state):

        # 常用變數宣告
        MyNumberID = round_state["next_player"]
        GameIndex = round_state["round_count"] 
        
        numberFit, SuitFit = [], []
        numberFit.append(number(hole_card[0][1]))
        numberFit.append(number(hole_card[1][1]))
        SuitFit.append(suit(hole_card[0][0]))
        SuitFit.append(suit(hole_card[1][0]))

        MyMoney = round_state["seats"][MyNumberID]["stack"]
        EnemyMoney = round_state["seats"][(MyNumberID + 1) % 2]["stack"]
        PotMoney = round_state["pot"]["main"]["amount"]

        # 根據不同的回合來決定使用的策略:
        stage = round_state["street"]

        # 計算如果要投注應該要投注多少:
        ExceptValue =  EnemyMoney - MyMoney
        ExceptValue = max(ExceptValue, valid_actions[2]["amount"]["min"])

        # 策略一: 保證能贏的情況下加速遊戲進度
        if WaitToEnd(GameIndex, MyMoney, EnemyMoney, PotMoney,stage):
            return valid_actions[0]["action"], valid_actions[0]["amount"]
        
        # 策略二: 分析手牌好不好
        if stage == 'preflop':
            if analysis(numberFit, SuitFit[0] == SuitFit[1], 60):
                self.raised = True
                return valid_actions[1]["action"], valid_actions[1]["amount"]
            else:
                return valid_actions[0]["action"], valid_actions[0]["amount"]
        elif self.raised:
            if analysis(numberFit, SuitFit[0] == SuitFit[1], 75):
                return valid_actions[2]["action"], min(ExceptValue * 1.5, valid_actions[2]["amount"]["max"])
            elif analysis(numberFit, SuitFit[0] == SuitFit[1], 68):
                return valid_actions[2]["action"], min(ExceptValue * 1.2, valid_actions[2]["amount"]["max"])
            return valid_actions[2]["action"], min(ExceptValue, valid_actions[2]["amount"]["max"])

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        # print(round_state["action_histories"])
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        # print(winners[0]["name"])
        pass


def setup_ai():
    return IWantToPass()
