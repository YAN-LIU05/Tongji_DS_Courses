/* 2352018 信06 刘彦 */
/* 2351440 王子安 2353801 佐健晔 2351767 张峻赫 2352036 雷达 2351134 吕奎辰 2351883 陈奕名*/
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>

#define ROW 10
#define COL 26

int main() 
{
    char field[ROW][COL];
    int Count = 0;
    int i, j;
    int x, y;

    // 读取输入
    for (i = 0; i < ROW; i++) 
    {
        for (j = 0; j < COL; j++)
        {
            // 每次读取一个字符
            scanf(" %c", &field[i][j]); // 使用 %c 读取字符，并忽略空白字符
            if (field[i][j] == '*') 
            {
                Count++; // 统计星号数量
            }
        }
    }

    // 检查雷的个数是否为50
    if (Count != 50) 
    {
        printf("错误1\n");
        return 1;
    }

    // 检查每个非雷位置周围的雷数
    for (i = 0; i < ROW; i++) 
    {
        for (j = 0; j < COL; j++) 
        {
            if (field[i][j] >= '0' && field[i][j] <= '8') 
            {
                int count = 0;
                // 检查周围的雷数
                for (x = -1; x <= 1; x++) 
                {
                    for (y = -1; y <= 1; y++) 
                    {
                        int i1 = i + x;
                        int j1 = j + y;
                        if (i1 >= 0 && i1 < ROW && j1 >= 0 && j1 < COL && field[i1][j1] == '*') 
                        {
                            count++;
                        }
                    }
                }
                // 比较计算的雷数与实际的雷数
                if (field[i][j] != count + '0') 
                {
                    printf("错误2\n");
                    return 1;
                }
            }
        }
    }

    // 如果所有检查都通过
    printf("正确\n");
    return 0;
}