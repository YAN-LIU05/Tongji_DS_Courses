import random

jack_money = 0
rose_money = 0

def play_game():
    global jack_money
    global rose_money

    # Jack和Rose随机选择正反面
    jack_choice = random.choice(['正面', '反面'])
    rose_choice = random.choice(['正面','正面','正面', '反面', '反面', '反面','反面', '反面'])

    # 根据游戏规则计算输赢
    if jack_choice == '正面' and rose_choice == '正面':
        jack_money += 3
        rose_money -= 3
    elif jack_choice == '反面' and rose_choice == '反面':
        jack_money += 1
        rose_money -= 1
    else:
        rose_money += 2
        jack_money -= 2

if __name__ == "__main__":
    for _ in range(1000000):
        play_game()

    # 输出最终的输赢情况
    print(f"Jack的最终金额: {jack_money}元")
    print(f"Rose的最终金额: {rose_money}元")
    if jack_money > rose_money:
        print("Jack胜利！")
    elif jack_money < rose_money:
        print("Rose胜利！")
