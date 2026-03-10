/* 2352018 信06 刘彦 */
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>

int leap(int year) 
{
    return (year % 4 == 0 && year % 100 != 0) || (year % 400 == 0);
}

int Month(int month, int isLeap) 
{ 
    int days[] = { 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 };  
    if (isLeap && month == 2)   // 如果是闰年，则2月有29天,其他月天数不变
    {
        return 29;
    }

    return days[month - 1];
}

int Year(int year, int month, int day) 
{
    int L = leap(year);
    int d = 0;
    for (int i = 1; i < month; ++i) 
    {
        d += Month(i, L);
    }
    d += day;
    return d;
}

int main()
{
    int year, month, day;
    printf("请输入年，月，日\n");
    scanf("%d %d %d", &year, &month, &day);

    if (month < 1 || month > 12)
    {
        printf("输入错误-月份不正确\n");
        return 1;
    }
    else if (day < 1 || day > Month(month, leap(year)))
    {
        printf("输入错误-日与月的关系非法\n");
        return 1;
    }

    int result = Year(year, month, day);
    printf("%d-%d-%d是%d年的第%d天\n", year, month, day, year, result);

    return 0;
}