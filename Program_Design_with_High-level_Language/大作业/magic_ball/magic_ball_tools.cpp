/* 2352018 信06 刘彦 */
#include <iostream>
#include <conio.h>
#include "cmd_console_tools.h"
#include "magic_ball.h"
using namespace std;

/***************************************************************************
  函数名称：
  功    能：比较字符串s1和s2的大小,英文字母不分大小写
  输入参数：
  返 回 值：相等为0,不等则为第1个不相等字符的ASCII差值
  说    明：
***************************************************************************/
int tj_strcasecmp(const char* s1, const char* s2)
{
    /* 注意：函数内不允许定义任何形式的数组（包括静态数组） */
    if (s1 == NULL || s2 == NULL)
    {
        int t = (s1 != NULL) - (s2 != NULL);
        return t;
    }
    char s_1, s_2;
    while (1)
    {
        if (*s1 >= 'A' && *s1 <= 'Z')
        {
            s_1 = *s1 + 'a' - 'A';
        }
        else
        {
            s_1 = *s1;
        }
        if (*s2 >= 'A' && *s2 <= 'Z')
        {
            s_2 = *s2 + 'a' - 'A';
        }
        else
        {
            s_2 = *s2;
        }
        if (s_1 == s_2)
        {
            if (s_1 == '\0')
                break;
            s1++;
            s2++;
        }
        else
        {
            break;
        }
    }
    return s_1 - s_2;
}

/***************************************************************************
  函数名称：set_botton
  功    能：设置坐标
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void set_botton(bool set, int num)
{
    static int Y = 0;
    if (set)
        Y = num;
    else
        cct_gotoxy(0, Y);
}