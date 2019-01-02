# -*- coding: utf-8 -*-
class HandleTest(object):
    def __init__(self):
        pass

    def get_score(self, current_value, value_list, rate):
        wight1 = rate  #权重
        actualCountMax1 = max(value_list) #单项最大计数，
        actualCountMin1 = min(value_list) #单项最小计数，得分最少的人
        if actualCountMax1 == actualCountMin1:
            return wight1*0.7
        actual_a = current_value #某人单项原始计数，肯定在单项最小计数和最大计数之间

        scorePerWight = float(100-60)/wight1 #过程，可忽略
        actualCountPerWight = float(actualCountMax1 - actualCountMin1)/wight1 #过程，可忽略
        #得到某人单项分数，在60~100之间。
        score_1_a = float(100-60)/(actualCountMax1 - actualCountMin1)*(actual_a-actualCountMin1) + 60
        #得到映射到权重下的分数
        score_1_a_scale = score_1_a/100*wight1
        return score_1_a_scale



if __name__ == '__main__':
    Test = HandleTest()
    for i in [73.1, 76.9, 77.8, 77.8, 72.2]:
        print Test.get_score(i,[73.1, 76.9, 77.8, 77.8, 72.2], 50)
