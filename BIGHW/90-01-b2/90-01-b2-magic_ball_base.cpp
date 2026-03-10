/* 2352018 大数据 刘彦 */
#include <iostream>
#include <cstdlib> 
#include <ctime> 
#include <windows.h>
#include <conio.h>
#include <iomanip>
#include "../include/cmd_console_tools.h"
#include "../include/bighw.h"
#include "90-01-b2-magic_ball.h"

using namespace std;

/***************************************************************************
  函数名称：ball_base_all
  功    能：base的汇总函数
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
int ball_base_all(int choice)
{
    int rows, cols;
    int x, y;
    int X = 0, Y = 0;   //鼠标位置
    int ret, maction;
    int keycode1, keycode2;
    int loop = 1;
    char hang;
    int lie;
    int directions[4][2] = { {-1, 0}, {1, 0}, {0, -1}, {0, 1} };   //方向数组

    // 输入验证
    while (1)
    {
        cout << "请输入行数(5-9)：" << endl;
        cin >> rows;

        if (rows >= MIN_ROWS && rows <= MAX_ROWS)
            break;
        else if (!cin.good())
        {
            cin.clear();
            cin.ignore(INT_MAX, '\n');
        }
    }
    while (1)
    {
        cout << "请输入列数(5-9)：" << endl;
        cin >> cols;

        if (cols >= MIN_COLS && cols <= MAX_COLS)
            break;
        else if (!cin.good())
        {
            cin.clear();
            cin.ignore(INT_MAX, '\n');
        }
    }

    int array[MAX_ROWS][MAX_COLS];   //填充数组为随机数
    fill_array(array, rows, cols, 1);
    cout << endl;
    cout << "初始数组：" << endl;
    print_origin(rows, cols, array, 1, 0);
    if (choice > 0 && choice <= 3)
        cout << "按回车键进行寻找初始可消除项的操作...";
    if (choice == 4)
        cout << "按回车键显示图形...";
    cct_getxy(x, y);

    char ch = _getch();
    while (1)
    {
        if (ch == '\r')
            break;
        ch = _getch();
    }
    // 打印初始数组和标识可消除项
    if (base_check1(array, rows, cols))
    {
        switch (choice)
        {
            case 1:
                print_mark(rows, cols, array);
                break;
            case 2:
            case 3:
                base_remove(array, rows, cols, choice);
                break;
            case 4:
            case 6:
                cct_cls();
                int a, b, c, d;
                cct_getconsoleborder(a, b, c, d);
                cct_setcolor();
                cct_cls();
                d = cols + 5;
                c = rows * 2 + 4;
                cct_setconsoleborder(c + 25, d + 5);
                cct_gotoxy(0, 0);
                cct_setfontsize("新宋体", 28);
                cout << "屏幕：" << d + 1 << "行" << 40 << "列";
                draw_border(rows, cols, 0, choice, 1);
                if (choice == 4)
                {
                    for (int i = 0; i < rows; i++)
                    {
                        for (int j = 0; j < cols; j++)
                        {
                            draw_ball(i, j, array[i][j], 0);
                            Sleep(TIME);
                        }
                    }
                }
                if (choice == 6)
                {

                    for (int i = 0; i < rows; i++)
                    {
                        for (int j = 0; j < cols; j++)
                        {
                            x = 2 * j + 2;
                            y = i + 2;
                            cct_gotoxy(x, y);
                            cct_setcolor(array[i][j], COLOR_BLACK);
                            if (base_check0(array, i, j, rows, cols))
                                cout << "●";
                            else
                                cout << "〇";
                            cct_gotoxy(x, y + 1);
                        }
                    }
                }
                cct_setcolor();
                set_botton(0, 0);
                break;
            case 5:
            case 7:
            case 8:
                cct_cls();
                cct_getconsoleborder(a, b, c, d);
                cct_setcolor();
                cct_cls();
                d = 2 * cols + 5;
                c = rows * 4 + 4;
                cct_setconsoleborder(c + 25, d + 4);
                cct_gotoxy(0, 0);
                cct_setfontsize("新宋体", 28);
                cout << "屏幕：" << d << "行" << 40 << "列";
                if (choice == 8)
                {
                    cout << "(当前分数：0 右键退出)";
                }
                draw_border(rows, cols, 1, choice, 1);
                if (choice == 5)
                {
                    for (int i = 0; i < rows; i++)
                    {
                        for (int j = 0; j < cols; j++)
                        {
                            draw_ball(i, j, array[i][j], 1);
                            Sleep(TIME);
                        }
                    }
                }
                if (choice == 7 || choice == 8)
                {

                    for (int i = 0; i < rows; i++)
                    {
                        for (int j = 0; j < cols; j++)
                        {
                            x = 4 * j + 2;
                            y = 2 * i + 2;
                            cct_gotoxy(x, y);
                            cct_setcolor(array[i][j], COLOR_BLACK);
                            if (base_check0(array, i, j, rows, cols))
                                cout << "●";
                            else
                                cout << "〇";
                            cct_gotoxy(x, y + 1);
                        }

                    }
                    int array0[MAX_ROWS][MAX_COLS];
                    for (int i = 0; i < rows; ++i) {
                        for (int j = 0; j < cols; ++j) {
                            array0[i][j] = array[i][j];
                        }
                    }
                    cout << endl;

                    if (choice == 8)
                    {
                        while (1)
                        {
                            draw_fall(array, rows, cols, choice, array0, 0);
                            for (int i = 0; i < rows; ++i)
                            {
                                for (int j = 0; j < cols; ++j)
                                    array[i][j] = array0[i][j];
                            }
                            for (int i = 0; i < rows; ++i)
                            {
                                for (int j = 0; j < cols; ++j)
                                {
                                    // 检查并标记可消除项
                                    if (base_check2(array, directions, i, j, rows, cols))
                                    {
                                        draw_ball(i, j, array[i][j], 2);
                                    }

                                }
                            }
                            if (base_check1(array, rows, cols))
                                continue;
                            else
                                break;

                        }
                    }
                }
                if (choice == 8)
                {
                    int x8, y8;
                    x8 = 0;
                    y8 = 2 * rows + 2;
                    cct_enable_mouse();
                    cct_setcursor(CURSOR_INVISIBLE);
                    while (loop)
                    {
                        ret = cct_read_keyboard_and_mouse(X, Y, maction, keycode1, keycode2);
                        cct_gotoxy(x8, y8);
                        cct_setcolor();
                        cout << "[当前光标] ";

                        if (ret == CCT_MOUSE_EVENT)
                        {
                            if (X <= 4 * cols && Y <= 2 * rows + 1)
                            {
                                hang = 'A' + Y / 2 - 1;
                                lie = int(X / 4) + 1;
                                if ((X % 4 == 2 || X % 4 == 3) && Y % 2 == 0 && Y > 0)
                                {
                                    cout << hang << "行" << lie << "列";

                                    switch (maction)
                                    {
                                        case MOUSE_LEFT_BUTTON_CLICK:
                                            if (base_check2(array, directions, Y / 2 - 1, lie - 1, rows, cols))
                                            {
                                                cct_gotoxy(x8, y8);
                                                cout << "当前选择" << hang << "行" << lie << "列";
                                                Sleep(TIME * 20);

                                                loop = 0;
                                            }
                                            else
                                            {
                                                cct_gotoxy(x8, y8);
                                                cout << "不能选择" << hang << "行" << lie << "列";
                                            }
                                            break;
                                        case MOUSE_RIGHT_BUTTON_CLICK:
                                            loop = 0;
                                            cct_gotoxy(x8, y8);
                                            break;
                                    }
                                }

                                else
                                {
                                    cout << "位置非法";
                                }
                                cout << "        ";
                                cct_gotoxy(x8, y8);

                            }
                            else
                            {
                                cout << "位置非法";
                                cout << "        ";
                                cct_gotoxy(x8, y8);
                            }
                        }
                    }
                }
                cct_setcolor();
                set_botton(0, 0);
                break;
            case 9:
                draw_nine(array, rows, cols, choice);
                set_botton(0, 0);
                break;
        }
        if (choice != 7 && choice != 8 && choice != 9)
            cout << endl;
    }

    else
    {
        switch (choice)
        {
            case 1:
            case 2:
                cct_gotoxy(x, y);
                cout << "初始无可消除项，本小题无法测试，请再次运行";
                break;
            case 3:
                cct_gotoxy(x, y);
                cout << "初始无可消除项" << endl;
                print_tips(rows, cols, array);
                break;
            case 4:
            case 6:
                cct_cls();
                int a, b, c, d;
                cct_getconsoleborder(a, b, c, d);
                cct_setcolor();
                cct_cls();

                d = cols + 5;
                c = rows * 2 + 4;
                cct_setconsoleborder(c + 25, d + 5);
                cct_gotoxy(0, 0);
                cct_setfontsize("新宋体", 28);
                cout << "屏幕：" << d + 1 << "行" << 40 << "列";
                draw_border(rows, cols, 0, choice, 1);

                for (int i = 0; i < rows; i++)
                {
                    for (int j = 0; j < cols; j++)
                    {
                        draw_ball(i, j, array[i][j], 0);
                        if (choice == 4)
                            Sleep(TIME);
                    }
                }

                cct_setcolor();
                set_botton(0, 0);
                break;
            case 5:
            case 7:
            case 8:
                cct_cls();
                cct_getconsoleborder(a, b, c, d);
                cct_setcolor();
                cct_cls();

                d = 2 * cols + 5;
                c = rows * 4 + 4;
                cct_setconsoleborder(c + 25, d + 4);

                cct_gotoxy(0, 0);
                cct_setfontsize("新宋体", 28);
                cout << "屏幕：" << d << "行" << 40 << "列";
                if (choice == 7)
                {
                    cout << "(未找到初始可消除项)";
                }

                if (choice == 8)
                {
                    cout << "(当前分数：0 右键退出)";
                }


                draw_border(rows, cols, 1, choice, 1);
                for (int i = 0; i < rows; i++)
                {
                    for (int j = 0; j < cols; j++)
                    {
                        draw_ball(i, j, array[i][j], 1);
                        if (choice == 5)
                            Sleep(TIME);
                    }
                }
                if (choice == 7 || choice == 8)
                {
                    int x0, y0;
                    cout << endl;
                    cct_getxy(x0, y0);
                    cct_setcolor(COLOR_BLACK, COLOR_WHITE);// 重置颜色
                    if (choice == 7)
                    {
                        cout << "按回车键显示消除提示...";

                        char ch3 = _getch();
                        while (1)
                        {
                            if (ch3 == '\r')
                                break;
                            ch3 = _getch();
                        }
                    }



                    for (int i = 0; i < rows; ++i)
                    {
                        for (int j = 0; j < cols; ++j)
                        {
                            // 检查并标记可消除项
                            if (base_check2(array, directions, i, j, rows, cols))
                            {
                                draw_ball(i, j, array[i][j], 2);
                            }

                        }
                    }
                    cct_setcolor(COLOR_BLACK, COLOR_WHITE);// 重置颜色
                    cct_gotoxy(x0, y0);
                }

                if (choice == 8)
                {
                    int x8, y8;
                    cct_enable_mouse();
                    cct_setcursor(CURSOR_INVISIBLE);
                    while (loop)
                    {
                        ret = cct_read_keyboard_and_mouse(X, Y, maction, keycode1, keycode2);
                        cct_getxy(x8, y8);
                        cct_gotoxy(x8, y8);
                        cout << "[当前光标] ";

                        if (ret == CCT_MOUSE_EVENT)
                        {
                            if (X <= 4 * cols && Y <= 2 * rows + 1)
                            {
                                hang = 'A' + Y / 2 - 1;
                                lie = int(X / 4) + 1;
                                if ((X % 4 == 2 || X % 4 == 3) && Y % 2 == 0 && Y > 0)
                                {
                                    cout << hang << "行" << lie << "列";
                                    switch (maction)
                                    {
                                        case MOUSE_LEFT_BUTTON_CLICK:
                                            if (base_check2(array, directions, Y / 2 - 1, lie - 1, rows, cols))
                                            {
                                                cct_gotoxy(x8, y8);
                                                cout << "当前选择" << hang << "行" << lie << "列";
                                                loop = 0;
                                            }
                                            else
                                            {
                                                cct_gotoxy(x8, y8);
                                                cout << "不能选择" << hang << "行" << lie << "列";
                                            }
                                            break;
                                        case MOUSE_RIGHT_BUTTON_CLICK:
                                            loop = 0;
                                            cct_gotoxy(x8, y8);
                                            break;
                                    }
                                }
                                else
                                {
                                    cout << "位置非法";
                                }
                                cout << "        ";
                                cct_gotoxy(x8, y8);
                            }
                            else
                            {
                                cout << "位置非法";
                                cout << "        ";
                                cct_gotoxy(x8, y8);
                            }
                        }
                    }
                }
                cct_setcolor();
                set_botton(0, 0);
                break;
            case 9:
                draw_nine(array, rows, cols, choice);
                set_botton(0, 0);
                break;

        }

        if (choice != 7 && choice != 8 && choice != 9)
            cout << endl;
    }


    // 可以在这里添加其他功能

    return 0;
}


/***************************************************************************
  函数名称：base_remove
  功    能：相同数字的消除和0的设置
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void base_remove(int array[MAX_ROWS][MAX_COLS], int rows, int cols, int choice)
{
    bool can_remove;
    do {

        can_remove = 0;
        // 记录可消除项的位置和数量
        int remove_position[100][2];
        int remove_count = 0;

        // 寻找可消除项并记录位置
        for (int i = 0; i < rows; ++i)
        {
            for (int j = 0; j < cols; ++j)
            {
                if (base_check0(array, i, j, rows, cols))
                {
                    remove_position[remove_count][0] = i; // 行
                    remove_position[remove_count][1] = j; // 列
                    remove_count++;
                    can_remove = 1;
                }
            }
        }

        if (!can_remove)
            break;
        print_mark(rows, cols, array);
        cout << "按回车键进行数组下落除0操作...";
        char ch1 = _getch();
        while (1)
        {
            if (ch1 == '\r')
                break;
            ch1 = _getch();

        }
        cout << endl;
        cout << "下落除0后的数组(不同色标识)：" << endl;
        // 执行消除操作：将可消除项设置为0
        for (int k = 0; k < remove_count; ++k)
        {
            int i = remove_position[k][0];
            int j = remove_position[k][1];
            array[i][j] = 0;
        }
        zero_drop(array, rows, cols);
        cout << "  | ";
        for (int j = 0; j < cols; ++j)
            cout << " " << j + 1 << " ";
        cout << endl;
        cout << "--+-";;
        for (int i = 0; i < cols; ++i)
            cout << "---";
        cout << endl;
        for (int i = 0; i < rows; ++i)
        {
            cout << static_cast<char>('A' + i) << " | ";
            for (int j = 0; j < cols; ++j)
            {
                // 检查并标记可消除项
                if (array[i][j] == 0)
                {
                    cout << " ";
                    cct_setcolor(COLOR_YELLOW, COLOR_BLACK);
                    cout << array[i][j];
                    cct_setcolor(COLOR_BLACK, COLOR_WHITE); // 重置颜色
                    cout << " ";
                }
                else {
                    cout << " " << array[i][j] << " ";
                }
            }
            cout << endl;
        }
        cout << endl;


        cout << "按回车键进行新值填充...";
        char ch2 = _getch();    // 等待用户按下回车键
        while (1)
        {
            if (ch2 == '\r')
                break;
            ch2 = _getch();  // 获取用户按下的键的 ASCII 值

        }
        cout << endl;
        // 让上面的非0项下落

        srand(static_cast<unsigned int>(time(nullptr)));


        cout << "  | ";
        for (int j = 0; j < cols; ++j)
            cout << " " << j + 1 << " ";
        cout << endl;
        cout << "--+-";;
        for (int i = 0; i < cols; ++i)
            cout << "---";
        cout << endl;
        for (int i = 0; i < rows; ++i) {
            cout << static_cast<char>('A' + i) << " | ";
            for (int j = 0; j < cols; ++j) {
                // 检查并标记可消除项
                if (array[i][j] == 0) {
                    cout << " ";
                    cct_setcolor(COLOR_HYELLOW, COLOR_HBLUE);
                    array[i][j] = (rand() % 9) + 1;
                    cout << array[i][j];
                    cct_setcolor(COLOR_BLACK, COLOR_WHITE); // 重置颜色
                    cout << " ";
                }
                else {
                    cout << " " << array[i][j] << " ";
                }
            }
            cout << endl;
        }


    } while (can_remove); // 如果有可消除项，重复以上过程
    cout << endl;
    cout << "初始已无可消除项";
    if (choice == 3)
    {
        print_tips(rows, cols, array);
    }
}