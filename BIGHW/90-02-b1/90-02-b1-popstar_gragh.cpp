/* 2352018 大数据 刘彦 */
#include <iostream>
#include <cstdlib> 
#include <ctime> 
#include <windows.h>
#include <conio.h>
#include <iomanip>
#include "../include/cmd_console_tools.h"
#include "../include/bighw.h"
#include "90-02-b1-popstar.h"

using namespace std;

/***************************************************************************
	函数名称：draw_around
	功    能：选中以后显示周围相邻元素
	输入参数：
	返 回 值：
	说    明：
***************************************************************************/
bool draw_around(int rows, int cols, int border, int array[][MAX_COLS], int array_around[][MAX_COLS], int choice, int i_last, int j_last)
{
	// 复制原始数组到周围元素数组
	for (int i = 0; i < 10; i++) 
		for (int j = 0; j < 10; j++) 
			array_around[i][j] = array[i][j];

	// 检查周围相邻元素
	
	if (star_check(array, array_around, i_last, j_last) == 0)
	{
		cct_gotoxy(0, 4 + rows * (3 + border));
		cct_setcolor(COLOR_BLACK, COLOR_HYELLOW);
		cout << "周围无相同值 ";
		cct_setcolor(COLOR_BLACK, COLOR_WHITE);
		cout << "箭头键/鼠标移动 回车键/单击左键选择 Q退出";
		Sleep(1000);
		for (int i = 0; i < 10; i++)
			for (int j = 0; j < 10; j++)
				array_around[i][j] = array[i][j];
		return false;
	}

	// 显示相邻元素
	for (int i = 0; i < rows; i++) 
	{
		for (int j = 0; j < cols; j++) 
		{
			if (array_around[i][j] == '*') 
			{
				if (i != i_last || j != j_last) 
					draw_block(i, j, border, array, rows, cols, -2);
				else 
					draw_block(i_last, j_last, border, array, rows, cols, -1);
			}
		}
	}
	return true;
}

/***************************************************************************
	函数名称：popstar_compound
	功    能：合成相邻的星星
	输入参数：
	返 回 值：
	说    明：
***************************************************************************/
void pop_together(int rows, int cols, int border, int array[][MAX_COLS], int i_last, int j_last)
{
	int array_around[MAX_ROWS][MAX_COLS] = { 0 };
	for (int i = 0; i < 10; i++)
		for (int j = 0; j < 10; j++)
			array_around[i][j] = array[i][j];
	star_check(array, array_around, i_last, j_last);
	for (int i = 0; i < rows; i++) 
	{
		for (int j = 0; j < cols; j++) 
		{
			if (array_around[i][j] == '*') 
			{
				draw_block(i, j, border, array, rows, cols, 0);
			}
		}
	}
}
