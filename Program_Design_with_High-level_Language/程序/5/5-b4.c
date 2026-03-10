/* 2352018 信06 刘彦 */
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
  
int main()
{
    int scores[1000];
    int count[101] = { 0 };
    int x = 0;
    int score;

    printf("请输入成绩（最多1000个），负数结束输入\n");

    while (x < 1000 && scanf("%d", &score) && score >= 0)
    {
        scores[x++] = score;
        if (score <= 100)
        {
            count[score]++;
        }
    }
    if (x == 0)
    {
        printf("无有效输入\n");
        return 0;
    }
    printf("输入的数组为:\n");
    for (int i = 0; i < x; ++i)
    {
        printf("%d ", scores[i]);
        if ((i + 1) % 10 == 0)
        {
            printf("\n");
        }
    }
    printf("\n");

    printf("分数与人数的对应关系为:\n");
    for (int i = 100; i >= 0; --i)
    {
        if (count[i] > 0)
        {
            printf("%d %d\n", i, count[i]);
        }
    }
    printf("\n");

    return 0;
}