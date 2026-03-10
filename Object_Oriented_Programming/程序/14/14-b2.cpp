/* 2352018 大数据 刘彦 */
#include <iostream>
#include <iomanip>
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <time.h>
/* 如果有需要，此处可以添加头文件 */
	
using namespace std;

/* 允许定义常变量/宏定义，但不允许定义全局变量 */
#define TOTAL_CARDS 54 // 总牌数
#define CARDS_PER_PLAYER 17 // 每人发的牌数
#define NUMBER_OF_PLAYERS 3 // 玩家数量
#define REMAINING_CARDS 3 // 剩余的牌数
#if defined(__linux__) 
#define CHOICE 0
#else
#define CHOICE 1
#endif

/* 可以添加自己需要的函数 */

/***************************************************************************
  函数名称：
  功    能：打印某个玩家的牌面信息，如果是地主，后面加标记
  输入参数：
  返 回 值：
  说    明：
 ***************************************************************************/
int print(const char* prompt, const bool landlord, const unsigned long long player)
{
	/* 只允许定义不超过三个基本类型的简单变量，不能定义数组变量、结构体、string等 */
    int count = 0;

    cout << prompt;

    for (int i = 0; i < TOTAL_CARDS; ++i)
        if (player & (1ULL << i))
        {
            // 打印花色和点数
            if (i == 52)
                cout << "BJ "; // 小王
            else if (i == 53)
                cout << "RJ "; // 大王
            else
            {
                char suit;
                int rank = i / 4 + 3; // 从3开始

                if (CHOICE)   //判断编译器
                {
                    switch (i % 4)
                    {
                        case 0: suit = '\5'; // 梅花
                            break; 
                        case 1: suit = '\4'; // 方块
                            break; 
                        case 2: suit = '\3'; // 红心
                            break; 
                        case 3: suit = '\6'; // 黑桃
                            break; 
                    }
                }
                else
                {
                    switch (i % 4)
                    {
                        case 0: suit = 'C'; // 梅花
                            break; 
                        case 1: suit = 'D'; // 方块
                            break; 
                        case 2: suit = 'H'; // 红心
                            break; 
                        case 3: suit = 'S'; // 黑桃
                            break; 
                    }
                }

                // 特殊处理点数
                switch (rank)
                {
                    case 10:
                        cout << suit << "T ";  // 10
                        break;
                    case 11:
                        cout << suit << "J ";  // J
                        break;
                    case 12:
                        cout << suit << "Q "; // Q
                        break;
                    case 13:
                        cout << suit << "K "; // K
                        break;
                    case 14:
                        cout << suit << "A ";  // A
                        break;
                    case 15:
                        cout << suit << "2 ";  // 2
                        break;
                    default:
                        if (rank >= 3 && rank <= 9)
                            cout << suit << rank << " "; // 3-9
                        break;
                }
            }
            count++;
        }

    if (landlord)
        cout << "(地主)";
    cout << endl;
    return 0;
}

/***************************************************************************
  函数名称：
  功    能：发牌（含键盘输入地主）
  输入参数：
  返 回 值：
  说    明：
 ***************************************************************************/
int deal(unsigned long long* player)
{
	/* 只允许定义不超过十个基本类型的简单变量，不能定义数组变量、结构体、string等 */
    srand(static_cast<unsigned int>(time(nullptr)));
    long long card = (1ULL << 54) - 1;
    int landlord = 0;

    for (int i = 0; i < CARDS_PER_PLAYER; i++) // 发牌轮次
    { 
        for (int j = 0; j < NUMBER_OF_PLAYERS; j++) // 一次为三位玩家发牌
        { 
            int num = rand() % TOTAL_CARDS; // 生成0-53范围内的随机数
            if (card & ((long long)1 << num)) // 检查当前位置是否未被分配
            { 
                card &= ~(1LL << num); // 标记为已发牌
                *(player + j) |= ((unsigned long long) 1 << num);   // 将牌发给玩家
            }
            else  // 当前位置已被分配
                --j;
        }
        cout << "第" << i + 1 << "轮结束：" << endl;
        print("甲的牌：", 0, *player);
        print("乙的牌：", 0, *(player + 1));
        print("丙的牌：", 0, *(player + 2));
    }
    cout << endl;

    // 直接在这里实现输入逻辑
    cout << "请选择一个地主[0-2]：" << endl;
    while (1) 
    {
        cin >> landlord;
        if (!cin) 
        {
            cin.clear();
            cin.ignore(65536, '\n');
        }
        else if (landlord >= 0 && landlord <= 2) 
            break;
        cout << "请选择一个地主[0-2]：" << endl;
    }

    for (int i = 0; i < TOTAL_CARDS; i++)  // 遍历剩余牌堆，将剩余的牌发给地主
    {
        if (card & ((long long)1 << i))  // 检查当前位置是否未被分配
        {
            card &= ~(1LL << i); // 标记为已发牌
            *(player + landlord) |= ((unsigned long long) 1 << i);   // 将牌发给地主
        }
    }
    return landlord;
}

/***************************************************************************
  函数名称：
  功    能：
  输入参数：
  返 回 值：
  说    明：main函数，不准修改
 ***************************************************************************/
int main()
{
	unsigned long long player[3] = { 0 }; //存放三个玩家的发牌信息
	int landlord; //返回0-2表示哪个玩家是地主

	cout << "按回车键开始发牌";
	while (getchar() != '\n')
		;

	landlord = deal(player);
	print("甲的牌：", (landlord == 0), player[0]);
	print("乙的牌：", (landlord == 1), player[1]);
	print("丙的牌：", (landlord == 2), player[2]);

	return 0;
}