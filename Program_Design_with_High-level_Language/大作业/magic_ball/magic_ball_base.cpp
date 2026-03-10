/* 2352018 信06 刘彦 */
#include <iostream>
#include <cstdlib> 
#include <ctime> 
#include <windows.h>
#include <conio.h>
#include <iomanip>
#include "cmd_console_tools.h"
#include "magic_ball.h"

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

    srand(static_cast<unsigned int>(time(nullptr)));

    int array[MAX_ROWS][MAX_COLS];   //填充数组为随机数
    for (int i = 0; i < rows; ++i)
    {
        for (int j = 0; j < cols; ++j)
            array[i][j] = (rand() % 9) + 1;
    }
    print_origin(rows, cols, array);
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
                draw_border(rows, cols, 0, choice);
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
                draw_border(rows, cols, 1, choice);
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
                draw_border(rows, cols, 0, choice);

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


                draw_border(rows, cols, 1, choice);
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
  函数名称：print_origin
  功    能：打印初始数组
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void print_origin(int rows, int cols, int array[MIN_ROWS][MAX_ROWS])
{
    cout << endl;
    cout << "初始数组：" << endl;
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
            cout << " " << array[i][j] << " ";
        cout << endl;
    }
    cout << endl;
}

/***************************************************************************
  函数名称：print_mark
  功    能：打印初始可消除项
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void print_mark(int rows, int cols, int array[MIN_ROWS][MAX_ROWS])
{
    cout << endl;
    cout << "初始可消除项（不同色标识）：" << endl;
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
            if (base_check0(array, i, j, rows, cols))
            {
                cout << " ";
                cct_setcolor(COLOR_HYELLOW, COLOR_HBLUE);
                cout << array[i][j];
                cct_setcolor(COLOR_BLACK, COLOR_WHITE);// 重置颜色
                cout << " ";
            }
            else
                cout << " " << array[i][j] << " ";
        }
        cout << endl;
    }
    cout << endl;
}

/***************************************************************************
  函数名称：print_tips
  功    能：打印提示项
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void print_tips(int rows, int cols, int array[MIN_ROWS][MAX_ROWS])
{
    int directions[4][2] = { {-1, 0}, {1, 0}, {0, -1}, {0, 1} };   //方向数组
    cout << endl;
    cout << "可选择的消除提示（不同色标识）：" << endl;
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
            if (base_check2(array, directions, i, j, rows, cols))
            {
                cout << " ";
                cct_setcolor(COLOR_HYELLOW, COLOR_HBLUE);
                cout << array[i][j];
                cct_setcolor(COLOR_BLACK, COLOR_WHITE);// 重置颜色
                cout << " ";
            }
            else
                cout << " " << array[i][j] << " ";
        }
        cout << endl;
    }
}

/***************************************************************************
  函数名称：base_check0
  功    能：检查是否可以消除
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
bool base_check0(const int array[MAX_ROWS][MAX_COLS], int row, int col, int rows, int cols)
{
    if (row >= rows || col >= cols)
        return 0;

    int count = 1; // 从目标元素开始计数
    for (int j = col + 1; j < cols && count < 3; j++) //向右检查
    {
        if (array[row][j] == array[row][col])
        {
            count++;
            if (count >= 3)
                return 1;
        }
        else
            break; // 遇到不同的元素，停止检查
    }
    for (int j = col - 1; j >= 0 && count < 3; j--) //向左检查
    {
        if (array[row][j] == array[row][col])
        {
            count++;
            if (count >= 3)
                return 1;
        }
        else
            break; // 遇到不同的元素，停止检查
    }

    count = 1; // 重置计数
    for (int i = row + 1; i < rows && count < 3; i++) //向下检查
    {
        if (array[i][col] == array[row][col])
        {
            count++;
            if (count >= 3)
                return 1;
        }
        else
            break; // 遇到不同的元素，停止检查
    }
    for (int i = row - 1; i >= 0 && count < 3; i--) //向上检查
    {
        if (array[i][col] == array[row][col])
        {
            count++;
            if (count >= 3)
                return 1;
        }
        else
            break; // 遇到不同的元素，停止检查
    }

    return 0; // 没有找到可消除项
}

/***************************************************************************
  函数名称：base_check1
  功    能：检查是否有初始可消除项
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
bool base_check1(const int array[MAX_ROWS][MAX_COLS], int rows, int cols)
{
    int num = 0;
    for (int i = 0; i < rows; ++i)
    {
        for (int j = 0; j < cols; ++j)
        {
            if (base_check0(array, i, j, rows, cols))
                num++;
        }
    }
    if (num)
        return 1;
    else
        return 0;
}

/***************************************************************************
  函数名称：base_check2
  功    能：检查是否可以提示
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
bool base_check2(const int array[MAX_ROWS][MAX_COLS], const int directions[4][2], int row, int col, int rows, int cols)
{
    if (row < 0 || row >= rows || col < 0 || col >= cols)
        return 0;

    // 创建一个数组的副本以模拟交换
    int arrayCopy[MAX_ROWS][MAX_COLS];
    for (int i = 0; i < rows; ++i)
    {
        for (int j = 0; j < cols; ++j)
            arrayCopy[i][j] = array[i][j];
    }

    // 检查相邻元素交换后是否满足消除条件
    for (int i = 0; i < 4; ++i)
    {
        int nextRow = row + directions[i][0];
        int nextCol = col + directions[i][1];
        if (nextRow >= 0 && nextRow < rows && nextCol >= 0 && nextCol < cols)   //交换
        {
            int temp = arrayCopy[nextRow][nextCol];
            arrayCopy[nextRow][nextCol] = arrayCopy[row][col];
            arrayCopy[row][col] = temp;

            if (col - 1 >= 0 && row - 1 >= 0)
            {
                if (base_check0(arrayCopy, row, col, rows, cols) || base_check0(arrayCopy, row + 1, col, rows, cols) || base_check0(arrayCopy, row - 1, col, rows, cols)
                    || base_check0(arrayCopy, row, col + 1, rows, cols) || base_check0(arrayCopy, row, col - 1, rows, cols))
                    return 1;
            }
            else if (col - 1 >= 0 && row - 1 < 0)
            {
                if (base_check0(arrayCopy, row, col, rows, cols) || base_check0(arrayCopy, row + 1, col, rows, cols) || base_check0(arrayCopy, row, col + 1, rows, cols)
                    || base_check0(arrayCopy, row, col - 1, rows, cols))
                    return 1;
            }
            else if (col - 1 < 0 && row - 1 >= 0)
            {
                if (base_check0(arrayCopy, row, col, rows, cols) || base_check0(arrayCopy, row + 1, col, rows, cols) || base_check0(arrayCopy, row - 1, col, rows, cols)
                    || base_check0(arrayCopy, row, col + 1, rows, cols))
                    return 1;
            }
            else
            {
                if (base_check0(arrayCopy, row, col, rows, cols) || base_check0(arrayCopy, row + 1, col, rows, cols) || base_check0(arrayCopy, row, col + 1, rows, cols))
                    return 1;
            }

            // 恢复交换前的数组状态
            temp = arrayCopy[nextRow][nextCol];
            arrayCopy[nextRow][nextCol] = arrayCopy[row][col];
            arrayCopy[row][col] = temp;
        }
    }

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
        for (int k = 0; k < remove_count; ++k) {
            int i = remove_position[k][0];
            int j = remove_position[k][1];
            array[i][j] = 0;
        }
        // 从矩阵底部开始向上遍历，让0上面的非0元素下移
        for (int j = 0; j < cols; ++j)   //从矩阵底部开始向上遍历
        {
            for (int i = rows - 1; i >= 0; --i)   //如果当前元素是0，则需要下移上面的非0元素
            {
                if (array[i][j] == 0)  //从当前位置向上查找第一个非0元素
                {
                    for (int k = i - 1; k >= 0; --k)
                    {
                        if (array[k][j] != 0)
                        {
                            // 将找到的非0元素移动到当前0的位置
                            array[i][j] = array[k][j];
                            // 并将原来的位置设置为0
                            array[k][j] = 0;
                            break;
                        }
                    }
                }
            }
        }
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