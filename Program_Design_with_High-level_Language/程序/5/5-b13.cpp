/* 2352018 信06 刘彦 */
#include <iostream>
#include <cstdlib>
#include <time.h>
using namespace std;

#define ROW 10
#define COL 26

void print(int field[ROW][26])
{
    int i, j;
    for (i = 0; i < ROW; ++i)
    {
        for (j = 0; j < COL; ++j)
        {
            switch (field[i][j]) 
            {
                case 0:
                    cout << "0";
                    break;
                case -1:
                    cout << "*";
                    break;
                default:
                    cout << field[i][j];
                    break;
            }
            cout << " ";
        }
        cout << endl;
    }
}

void count(int field[ROW][COL])
{
    int i, j, r, c;
    int row, col;
    for (i = 0; i < ROW; ++i)
    {
        for (j = 0; j < COL; ++j)
        {
            if (field[i][j] == 0) { // 非雷位置
                int count = 0;
                for (r = -1; r <= 1; ++r)
                {
                    for (c = -1; c <= 1; ++c)
                    {
                        row = i + r;
                        col = j + c;
                        if (row >= 0 && row < ROW && col >= 0 && col < COL && (r != 0 || c != 0))
                        {
                            if (field[row][col] == -1)
                            {
                                count++;
                            }
                        }
                    }
                }
                field[i][j] = count; // 存储周围的雷数
            }
        }
    }
}

int main() 
{
    int field[ROW][COL] = { 0 }; // 雷区数组
    int Count = 0; // 雷的数量

    // 使用当前时间作为种子来初始化随机数生成器
    srand((unsigned int)(time(0)));

    // 随机放置50颗雷
    while (Count < 50) 
    {
        int row = rand() % ROW;
        int col = rand() % COL;
        if (field[row][col] == 0) // 确保位置还没有雷
        { 
            field[row][col] = -1; // 使用-1表示雷
            Count++;
        }
    }

    // 计算每个非雷位置周围的雷数
    count(field);

    // 打印雷区
    print(field);

    return 0;
}