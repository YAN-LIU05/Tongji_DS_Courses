/* 2352018 信06 刘彦 */
#include <iostream>  
using namespace std;

bool check(int sudoku[9][9]) 
{
    int row[9][10] = { 0 }; // 用于检查行
    int col[9][10] = { 0 }; // 用于检查列
    int box[3][3][10] = { 0 }; // 用于检查3x3宫格

    for (int i = 0; i < 9; i++) 
    {
        for (int j = 0; j < 9; j++)
        {
            int num = sudoku[i][j];
            if (num > 0 && num <= 9) 
            {
                // 检查行
                if (row[i][num]) 
                    return false;
                row[i][num] = 1;
                // 检查列
                if (col[j][num]) 
                    return false;
                col[j][num] = 1;
                // 检查3x3宫格
                int box_row = i / 3;
                int box_col = j / 3;
                if (box[box_row][box_col][num]) 
                    return false;
                box[box_row][box_col][num] = 1;
            }
            else if (num != 0) 
                // 如果数字不是0且不在1-9之间，说明输入无效
                return false;
        }
    }
    return true;
}

int main() 
{
    int i = 0, j = 0;
    int sudoku[9][9];
    cout << "请输入9*9的矩阵，值为1-9之间" << endl;

    while (1) {
        cin >> sudoku[i][j];
        if (cin.good() && sudoku[i][j] >= 1 && sudoku[i][j] <= 9) 
        {
            j++;
            if (j == 9) 
            {
                i++;
                j = 0;
            }
            if (i == 9) 
            {
                break;
            }
        }
        else if (cin.good()) 
        {
            cout << "请重新输入第" << i + 1 << "行" << j + 1 << "列(行列均从1开始计数)的值" << endl;
        }
        else 
        {
            cin.clear();
            cin.ignore(65536, '\n');
            cout << "请重新输入第" << i + 1 << "行" << j + 1 << "列(行列均从1开始计数)的值" << endl;
        }
    }
    if (check(sudoku)) 
    {
        cout << "是数独的解" << endl;
    }
    else
    {
        cout << "不是数独的解" << endl;
    }

    return 0;
}