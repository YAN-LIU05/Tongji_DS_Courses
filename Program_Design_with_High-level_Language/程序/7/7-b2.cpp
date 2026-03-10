/* 2352018 信06 刘彦 */

/* 1、按需加入头文件
   2、不允许定义全部变量，包括静态全局，但不显示const及define
   3、允许定义需要的结构体、函数等，但仅限本源程序文件使用 */
#include <iostream>
#include <conio.h>
#include "cmd_console_tools.h"
#include "7-b2.h"
using namespace std;

#define MAX_ITEMS 10
#define MAX_VISIBLE_ITEMS 10  // 可视区域内最多显示的菜单项数量
/* 例：声明仅本源程序文件需要的结构体，不要放到.h中
       仅为示例，不需要可删除 */

static int tj_strncpy(char s1[], const char s2[], const int len) {
    int i;

    // 复制s2到s1，最多复制len个字符
    for (i = 0; i < len && s2[i] != '\0'; i++) {
        s1[i] = s2[i];
    }

    // 如果s2的长度小于len，剩余的s1[i]填充为null字符
    for (; i < len; i++) {
        s1[i] = '\0';
    }

    // 返回实际复制的字符数，包括空字符终止符
    return i;
}

/***************************************************************************
  函数名称：
  功    能：供测试用例调用的函数，函数声明在头文件中
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
int pop_menu(const char menu[][MAX_ITEM_LEN], const PopMenu* original_para)
{
    if (!original_para || !menu) return -1; // 参数检查

    int selected = 0; // 当前选中的菜单项索引
    int itemCount = 0;
    int scrollOffset = 0; // 用于滚动的偏移量

    // 计算菜单项数量
    for (int i = 0; itemCount < 10; ++i) {
        ++itemCount;
    }

    // 循环显示菜单，直到用户选择一个项
    while (true) {
        
        int itemY = original_para->start_y;
        int titleLength = strlen(original_para->title);
        int titleStartX;
        int width0;
        if (original_para->width % 2 != 0)
        {
            width0 = original_para->width + 1;
            if (original_para->width < int(strlen(original_para->title)))
                width0 = strlen(original_para->title);
        }
            
        else
        {
            width0 = original_para->width;
            if (original_para->width < titleLength)
                width0 = strlen(original_para->title);
        }
            
        if (original_para->width < titleLength)
            titleStartX = original_para->start_x;
        else
            titleStartX = (width0 - titleLength) / 2;
        cct_setcolor(original_para->bg_color, original_para->fg_color);
        if (original_para->start_x != 0)
            cct_gotoxy(original_para->start_x - 1, original_para->start_y);
        else
            cct_gotoxy(original_para->start_x, original_para->start_y);
        // 绘制上边框和标题
        int actualHigh = 10;
        int height = original_para->high;
        if (original_para->high > 10) {
            height = actualHigh; // 调整高度以适应实际的菜单项数量
        }
        cout << "╔";
        if (original_para->width >= int(strlen(original_para->title)))
        {
            if (strlen(original_para->title) % 2 != 0)
            {
                for (int j = 0; j < titleStartX - 1 + original_para->start_x; j += 2) {
                    cout << "═";
                }
            }
            else
            {
                for (int j = 0; j < titleStartX - 1 + original_para->start_x + 2; j += 2) {
                    cout << "═";
                }
            }
            cct_setcolor(original_para->bg_color, original_para->fg_color);
            if (strlen(original_para->title) % 2 != 0)
                cct_gotoxy(titleStartX + original_para->start_x - 4, original_para->start_y);
            else
            {
                cout << "═";
                cct_gotoxy(titleStartX + original_para->start_x - 2, original_para->start_y);
            }
        }
        else
            cct_setcolor(original_para->bg_color, original_para->fg_color);
       

        cout << original_para->title;

        if (original_para->width >= int(strlen(original_para->title)))
        {
            if (strlen(original_para->title) % 2 != 0)
                cct_gotoxy(titleStartX + original_para->start_x + titleLength - 3, original_para->start_y);
            else
                cct_gotoxy(titleStartX + original_para->start_x + titleLength - 2, original_para->start_y);

        }
        
        
        if (original_para->width >= int(strlen(original_para->title)))
        {
            for (int j = original_para->start_x + 10; j < width0 - 2; j += 2) {
                cout << "═";
            }
        }


        cout << "╗" << endl;
        if (strlen(original_para->title) % 2 != 0)
        {
            for (int i = 0; i < height + 1; i++) {
                cct_gotoxy(original_para->start_x - 1, original_para->start_y + i + 1);
                cout << "║";

                cct_gotoxy(original_para->start_x + width0 - 1, original_para->start_y + i + 1);
                cout << "║" << endl;
            }
        }
        else
        {
            for (int i = 0; i < height + 1; i++) {
                cct_gotoxy(original_para->start_x - 1, original_para->start_y + i + 1);
                cout << "║";

                cct_gotoxy(original_para->start_x + width0 + 1, original_para->start_y + i + 1);
                cout << "║" << endl;
            }
        }
        
        // 绘制下边框
        cct_gotoxy(original_para->start_x - 1, original_para->start_y + height + 1);
        cout << "╚";

        if (strlen(original_para->title) % 2 != 0)
        {
            for (int j = 0; j < width0 - 2; j += 2) {
                cout << "═";
            }
        }
        else
        {
            for (int j = 0; j < width0; j += 2) {
                cout << "═";
            }
        }

        cout << "╝" << endl;

        // 绘制菜单标题
        cct_setcolor(original_para->bg_color, original_para->fg_color);



        // 绘制菜单项
        for (int i = 0; i < original_para->high && i + scrollOffset < itemCount; ++i) {
            int itemX = original_para->start_x + 1; // 菜单项的x坐标
            int itemY = original_para->start_y + 2 + i; // 菜单项的y坐标
            char displayItem[MAX_ITEM_LEN + 1];
            cct_gotoxy(itemX, itemY - 1);


            if (i == selected)
            {
                cct_setcolor(original_para->fg_color, original_para->bg_color);
            }
            else
            {
                cct_setcolor(original_para->bg_color, original_para->fg_color);
            }

            tj_strncpy(displayItem, menu[i + scrollOffset], width0);
            if (itemCount % 2 != 0)
            {

                displayItem[width0 + 1] = '\0';
            }
            else
                displayItem[width0] = '\0';
            int content_width = width0 - 2;


            // 打印菜单项
            cout << displayItem;

            int itemLength = strlen(menu[i + scrollOffset]);
            int spaces = content_width - itemLength; // 需要打印的空格数

            // 确保spaces是非负数，避免无限循环
            if (spaces >= 0) {
                for (int j = 0; j < spaces; ++j) {
                    cout << ' '; // 打印空格
                }
            }

        }

        // 等待用户输入
        char key = _getch();
        if (key == 13) { // 用户按回车键
            break;
        }
        else if (key == 72 && selected > 0) { // 用户按上箭头键
            --selected;
            if (selected < scrollOffset) scrollOffset = selected;
        }
        else if (key == 80 && selected < itemCount - 1 - scrollOffset) { // 用户按下箭头键
            ++selected;
            if (selected - scrollOffset == original_para->high - 1) scrollOffset = selected - original_para->high + 2;
        }
        else if (key == 27) { // 用户按Esc键退出
            selected = -1;
            break;
        }
    }

    // 返回选中的菜单项索引（从1开始计数），未选择则返回-1
    return selected + 1;
}