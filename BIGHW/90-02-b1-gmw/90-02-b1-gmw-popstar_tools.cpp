/* 2352018 大数据 刘彦 */
#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <cstdlib> 
#include <ctime> 
#include <windows.h>
#include <conio.h>
#include <iomanip>
#include "../include/cmd_console_tools.h"
#include "../include/cmd_gmw_tools.h"
#include "../include/bighw.h"
#include "90-02-b1-gmw-popstar.h"

using namespace std;
/***************************************************************************
	函数名称：draw_map
	功    能：显示界面全局图形
	输入参数：
	返 回 值：
	说    明：
***************************************************************************/
void draw_map(int rows, int cols, const int border, int array[][MAX_COLS], int choice, CONSOLE_GRAPHICS_INFO* PopStar_CGI)
{
	/* 定义1-5的数字用何种形式显示在界面上（正常状态） */
	const BLOCK_DISPLAY_INFO bdi_normal[] = {
		{0, -1, -1, "  "},  //0不显示，用空格填充即可
		{1, COLOR_HBLUE, COLOR_BLACK, "★"},
		{2, COLOR_HGREEN, COLOR_BLACK, "★"},
		{3, COLOR_HCYAN, COLOR_BLACK, "★"},
		{4, COLOR_HRED, COLOR_BLACK, "★"},
		{5, COLOR_HPINK, COLOR_BLACK, "★"},
		{-999, -1, -1, NULL} //判断结束条件为-999
	};
	/* 定义1-5的数字用何种形式显示在界面上（当前选择项状态+选中后关联项状态） */
	const BLOCK_DISPLAY_INFO bdi_related[] = {
		{BDI_VALUE_BLANK, -1, -1, "  "},  //空白
		{1, COLOR_HBLUE, COLOR_WHITE, "★"},
		{2, COLOR_HGREEN, COLOR_WHITE, "★"},
		{3, COLOR_HCYAN, COLOR_WHITE, "★"},
		{4, COLOR_HRED, COLOR_WHITE, "★"},
		{5, COLOR_HPINK, COLOR_WHITE, "★"},
		{BDI_VALUE_END, -1, -1, NULL} //判断结束条件为-999
	};
	/* 定义1-5的数字用何种形式显示在界面上（选中状态） */
	const BLOCK_DISPLAY_INFO bdi_selected[] = {
		{BDI_VALUE_BLANK, -1, -1, "  "},  //空白
		{1, COLOR_HBLUE, COLOR_HWHITE, "★"},
		{2, COLOR_HGREEN, COLOR_HWHITE, "★"},
		{3, COLOR_HCYAN, COLOR_HWHITE, "★"},
		{4, COLOR_HRED, COLOR_HWHITE, "★"},
		{5, COLOR_HPINK, COLOR_HWHITE, "★"},
		{BDI_VALUE_END, -1, -1, NULL} //判断结束条件为-999
	};
	gmw_init(PopStar_CGI);

	gmw_set_color(PopStar_CGI, COLOR_BLACK, COLOR_HWHITE);
	gmw_set_font(PopStar_CGI, "新宋体", 16, 8);
	gmw_set_frame_style(PopStar_CGI, 6, 3, true);	//色块带边框，宽度为6，高度为3
	gmw_set_ext_rowcol(PopStar_CGI, 0, 3, 0, 5);
	gmw_set_frame_color(PopStar_CGI, COLOR_HWHITE, COLOR_BLACK);
	gmw_set_rowno_switch(PopStar_CGI, true);							//显示行号
	gmw_set_colno_switch(PopStar_CGI, true);							//显示列标
	gmw_set_block_border_switch(PopStar_CGI, true);
	char temp[256];
	int i, j;
	int if_g = 1;
	int total = 0;//总得分

	while (if_g)
	{
		/* 按row/col的值重设游戏主区域行列 */
		gmw_set_rowcol(PopStar_CGI, rows, cols);

		/* 显示框架 */
		gmw_draw_frame(PopStar_CGI);

		/* 状态栏显示内容 */
		sprintf(temp, "窗口大小：%d行 %d列", PopStar_CGI->lines, PopStar_CGI->cols);
		gmw_status_line(PopStar_CGI, TOP_STATUS_LINE, temp);
		gmw_status_line(PopStar_CGI, LOWER_STATUS_LINE, "箭头键/鼠标移动,回车键/单击左键选择");
		/* 将内部数组展现到屏幕上 */
		for (i = 0; i < rows; i++)
			for (j = 0; j < cols; j++)
				gmw_draw_block(PopStar_CGI, i, j, array[i][j], bdi_normal);
		int end = 0;
		end = move_by_keyboard_and_mouse(rows, cols, border, array, total, PopStar_CGI);
		if (end == 1)
			break;

	}
};



/***************************************************************************
	函数名称：move_by_keyboard_and_mouse
	功    能：记录鼠标很键盘移动位置
	输入参数：
	返 回 值：
	说    明：
***************************************************************************/
int move_by_keyboard_and_mouse(int rows, int cols, const int border, int array[][MAX_COLS], int total, CONSOLE_GRAPHICS_INFO* PopStar_CGI)
{
	/* 定义1-5的数字用何种形式显示在界面上（正常状态） */
	const BLOCK_DISPLAY_INFO bdi_normal[] = {
		{0, -1, -1, "  "},  //0不显示，用空格填充即可
		{1, COLOR_HBLUE, COLOR_BLACK, "★"},
		{2, COLOR_HGREEN, COLOR_BLACK, "★"},
		{3, COLOR_HCYAN, COLOR_BLACK, "★"},
		{4, COLOR_HRED, COLOR_BLACK, "★"},
		{5, COLOR_HPINK, COLOR_BLACK, "★"},
		{-999, -1, -1, NULL} //判断结束条件为-999
	};
	/* 定义1-5的数字用何种形式显示在界面上（当前选择项状态+选中后关联项状态） */
	const BLOCK_DISPLAY_INFO bdi_related[] = {
		{BDI_VALUE_BLANK, -1, -1, "  "},  //空白
		{1, COLOR_HBLUE, COLOR_WHITE, "★"},
		{2, COLOR_HGREEN, COLOR_WHITE, "★"},
		{3, COLOR_HCYAN, COLOR_WHITE, "★"},
		{4, COLOR_HRED, COLOR_WHITE, "★"},
		{5, COLOR_HPINK, COLOR_WHITE, "★"},
		{BDI_VALUE_END, -1, -1, NULL} //判断结束条件为-999
	};
	/* 定义1-5的数字用何种形式显示在界面上（选中状态） */
	const BLOCK_DISPLAY_INFO bdi_selected[] = {
		{BDI_VALUE_BLANK, -1, -1, "  "},  //空白
		{1, COLOR_HBLUE, COLOR_HWHITE, "★"},
		{2, COLOR_HGREEN, COLOR_HWHITE, "★"},
		{3, COLOR_HCYAN, COLOR_HWHITE, "★"},
		{4, COLOR_HRED, COLOR_HWHITE, "★"},
		{5, COLOR_HPINK, COLOR_HWHITE, "★"},
		{BDI_VALUE_END, -1, -1, NULL} //判断结束条件为-999
	};
	int ret, maction;
	int keycode1, keycode2;
	int array_around[MAX_ROWS][MAX_COLS] = { 0 };
	int count = -1;
	bool changed = false;
	int chosen = 0;
	int i_last = 0, j_last = 0;
	int i = 0, j = 0;
	int X = 4, Y = 3;
	int end = 0;
	char temp[255];

	cct_enable_mouse();
	cct_setcursor(CURSOR_INVISIBLE);
    gmw_status_line(PopStar_CGI, LOWER_STATUS_LINE, "箭头键/鼠标移动 回车键/单击左键选择 Q退出");

	while (1)
	{
		int i_now = 0, j_now = 0;
		int X_now,Y_now;
		ret = cct_read_keyboard_and_mouse(X_now, Y_now,maction, keycode1, keycode2);
		if (ret == CCT_MOUSE_EVENT)
		{

			location_trans(-1, i_now, j_now, X_now, Y_now, rows, cols, border);
			if (array[i_now][j_now] == 0)
				i_now = j_now = -1;
			if (array[i][j] == 0)
				i = j = -1;

			changed = (i != i_now || j != j_now);

			if (maction == MOUSE_ONLY_MOVED)
			{
				if (check_border(X_now, Y_now, border, rows, cols, array))
				{
					if (changed)
					{
						gmw_draw_block(PopStar_CGI, i_now, j_now, array[i_now][j_now], bdi_selected);
						if (check_border(X, Y, border, rows, cols, array))
							gmw_draw_block(PopStar_CGI, i, j, array[i][j], bdi_normal);
					}
					i_last = i_now;
					j_last = j_now;
				}
				else if (changed)
					gmw_draw_block(PopStar_CGI, i, j, array[i][j], bdi_normal);
			}
			else if (maction == MOUSE_RIGHT_BUTTON_CLICK)
				end = 1;
			else if (maction == MOUSE_LEFT_BUTTON_CLICK && check_border(X_now, Y_now, border, rows, cols, array))
			{
				gmw_draw_block(PopStar_CGI, i_now, j_now, array[i_now][j_now], bdi_selected);
				chosen++;
			}

			i = i_now, j = j_now;
			X = X_now, Y = Y_now;

			if (!(0 && !changed))
				print_title(ret, border, rows, cols, i_now, j_now, array, PopStar_CGI);
		}
		else if (ret == CCT_KEYBOARD_EVENT)
		{
			i_now = i_last;
			j_now = j_last;

			if (keycode1 == 224)
			{
				switch (keycode2)
				{
					case KB_ARROW_UP:
						i_now = find_new_position(i_last, -1, rows, array[j_last]);
						break;
					case KB_ARROW_DOWN:
						i_now = find_new_position(i_last, 1, rows, array[j_last]);
						break;
					case KB_ARROW_LEFT:
						j_now = find_new_position(j_last, -1, cols, array[i_last]);
						break;
					case KB_ARROW_RIGHT:
						j_now = find_new_position(j_last, 1, cols, array[i_last]);
						break;
				}
				gmw_draw_block(PopStar_CGI, i_now, j_now, array[i_now][j_now], bdi_related);
				gmw_draw_block(PopStar_CGI, i_last, j_last, array[i_last][j_last], bdi_normal);
			}
			else if (keycode1 == 13)  // 选中
			{
				gmw_draw_block(PopStar_CGI, i_last, j_last, array[i_last][j_last], bdi_related);
				chosen++;
				print_title(ret, border, rows, cols, i_last, j_last, array, PopStar_CGI);
				changed = 0;
			}
			else if (keycode1 == 'Q' || keycode1 == 'q')
				end = 1;

			if (!((0 && !changed) || chosen))
				print_title(ret, border, rows, cols, i_now, j_now, array, PopStar_CGI);

			i = i_now, j = j_now;//赋值旧的坐标值
			X = X_now, Y = Y_now;
			i_last = i_now;
			j_last = j_now;
		}
		if (chosen)
		{


			count++;
			if (count == 0)
			{
				// 显示周围元素
				int is_around = draw_around(rows, cols, border, array, array_around, 'G', i_last, j_last, PopStar_CGI);


				if (is_around == 0)
				{
					chosen = 0;
					count = -1; // 进行下一次循环
					continue;
				}
				continue;
			}
			else if (count > 0 && changed)
			{
				// 取消反显
				for (int i = 0; i < rows; i++)
				{
					for (int j = 0; j < cols; j++)
						gmw_draw_block(PopStar_CGI, i, j, array[i][j], bdi_normal);
				}
				chosen = 0;
				count = -1;
				changed = 0;
				continue;
			}

			if (chosen == 2)
			{
				// 合成逻辑
				pop_together(rows, cols, border, array, i_last, j_last, PopStar_CGI);
				// 下降逻辑
				element_fall(array, array_around, rows, cols, 1, border);
				go_right(array, rows, cols, 1, PopStar_CGI);


				// 判断剩余星星
				int left = 0;
				if (search_finish(array, left, rows, cols) == 0)
				{
					cct_setcolor(COLOR_BLACK, COLOR_HYELLOW);
					int score_gift = (left >= 10) ? 0 : (10 - left) * 180;
					total += score_gift;
					sprintf(temp, "奖励得分：%d 总得分：%d      ", score_gift, total);
					gmw_status_line(PopStar_CGI, TOP_STATUS_LINE, temp);
				
					sprintf(temp, "剩余%d个星星，无可消除项，本关结束！回车进入下一关", left);
					gmw_status_line(PopStar_CGI, LOWER_STATUS_LINE, temp);
					

					int xg, yg;
					cct_getxy(xg, yg);
					while (1)
					{
						char ch_g;
						ch_g = _getche();
						if (ch_g == 13)
							break;
						else
						{
							cct_gotoxy(xg, yg);
							putchar(' ');
							cct_gotoxy(xg, yg);
						}
					}
					cout << endl;
					end = 2;
					break;
				}

				// 更新得分
				int count1 = 0;
				int score = 0;
				for (int i = 0; i < rows; ++i)
				{
					for (int j = 0; j < cols; ++j)
					{
						if (array_around[i][j] == '*')
						{
							count1++;
						}
					}
				}
				score = count1 * count1 * 5;
				total += score;
				count1 = 0;
				for (int i = 0; i < 10; i++)
				{
					for (int j = 0; j < 10; j++)
					{
						array_around[i][j] = array[i][j];
					}
				}
				copy_array(array, array_around, rows, cols);
				count = -1;
				chosen = 0;
				sprintf(temp, "本次得分：%d 总分：%d      ", score, total);
				gmw_status_line(PopStar_CGI, TOP_STATUS_LINE, temp);

			}

		}


		if (end)
			break;
	}
	cct_disable_mouse();
	cct_setcursor(CURSOR_VISIBLE_NORMAL);
	return end;
}




/***************************************************************************
	函数名称：draw_around
	功    能：选中以后显示周围相邻元素
	输入参数：
	返 回 值：
	说    明：
***************************************************************************/
bool draw_around(int rows, int cols, int border, int array[][MAX_COLS], int array_around[][MAX_COLS], int choice, int i_last, int j_last, CONSOLE_GRAPHICS_INFO* PopStar_CGI)
{
	/* 定义1-5的数字用何种形式显示在界面上（当前选择项状态+选中后关联项状态） */
	const BLOCK_DISPLAY_INFO bdi_related[] = {
		{BDI_VALUE_BLANK, -1, -1, "  "},  //空白
		{1, COLOR_HBLUE, COLOR_WHITE, "★"},
		{2, COLOR_HGREEN, COLOR_WHITE, "★"},
		{3, COLOR_HCYAN, COLOR_WHITE, "★"},
		{4, COLOR_HRED, COLOR_WHITE, "★"},
		{5, COLOR_HPINK, COLOR_WHITE, "★"},
		{BDI_VALUE_END, -1, -1, NULL} //判断结束条件为-999
	};
	/* 定义1-5的数字用何种形式显示在界面上（选中状态） */
	const BLOCK_DISPLAY_INFO bdi_selected[] = {
		{BDI_VALUE_BLANK, -1, -1, "  "},  //空白
		{1, COLOR_HBLUE, COLOR_HWHITE, "★"},
		{2, COLOR_HGREEN, COLOR_HWHITE, "★"},
		{3, COLOR_HCYAN, COLOR_HWHITE, "★"},
		{4, COLOR_HRED, COLOR_HWHITE, "★"},
		{5, COLOR_HPINK, COLOR_HWHITE, "★"},
		{BDI_VALUE_END, -1, -1, NULL} //判断结束条件为-999
	};
	// 复制原始数组到周围元素数组
	for (int i = 0; i < 10; i++)
		for (int j = 0; j < 10; j++)
			array_around[i][j] = array[i][j];

	// 检查周围相邻元素

	if (star_check(array, array_around, i_last, j_last) == 0)
	{
		gmw_status_line(PopStar_CGI, LOWER_STATUS_LINE, "箭头键/鼠标移动 回车键/单击左键选择 Q退出", "周围无相同值");
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
					gmw_draw_block(PopStar_CGI, i, j, array[i][j], bdi_related);
				else
					gmw_draw_block(PopStar_CGI, i_last, j_last, array[i_last][j_last], bdi_selected);
			}
		}
	}
	return true;
}

/***************************************************************************
	函数名称：pop_together
	功    能：合成相邻的星星
	输入参数：
	返 回 值：
	说    明：
***************************************************************************/
void pop_together(int rows, int cols, int border, int array[][MAX_COLS], int i_last, int j_last, CONSOLE_GRAPHICS_INFO* PopStar_CGI)
{
	const BLOCK_DISPLAY_INFO bdi_normal[] = {
		{0, -1, -1, "  "},  //0不显示，用空格填充即可
		{1, COLOR_HBLUE, COLOR_BLACK, "★"},
		{2, COLOR_HGREEN, COLOR_BLACK, "★"},
		{3, COLOR_HCYAN, COLOR_BLACK, "★"},
		{4, COLOR_HRED, COLOR_BLACK, "★"},
		{5, COLOR_HPINK, COLOR_BLACK, "★"},
		{-999, -1, -1, NULL} //判断结束条件为-999
	};
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
				gmw_draw_block(PopStar_CGI, i, j, 0, bdi_normal);
				//draw_block(i, j, border, array, rows, cols, 0);
			}
		}
	}
}


/***************************************************************************
  函数名称：star_replace0
  功    能：检查是否可消除的函数
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/

void star_replace0(int mp[MAX_ROWS][MAX_COLS], int flag[MAX_ROWS][MAX_COLS], int mark[MAX_ROWS][MAX_COLS], int row, int col, int x, int y, int target)
{

	if (x < 0 || x >= row || y < 0 || y >= col || flag[x][y] || mp[x][y] != target)
		return;
	flag[x][y] = 1;
	mark[x][y] = 1;

	int dx[] = { 1, -1, 0, 0 };
	int dy[] = { 0, 0, 1, -1 };
	for (int i = 0; i < 4; i++)
	{
		int nx = x + dx[i];
		int ny = y + dy[i];
		star_replace0(mp, flag, mark, row, col, nx, ny, target);
	}

}


/***************************************************************************
  函数名称：star_check
  功    能：检查是否有相同的相邻元素
  输入参数：
  返 回 值：
  说    明：有一个重载函数
***************************************************************************/
int star_check(int mp[MAX_ROWS][MAX_COLS], int row, int col, int x, int y)
{
	int flag[MAX_ROWS][MAX_COLS];
	int mark[MAX_ROWS][MAX_COLS];
	memset(flag, 0, sizeof(flag));
	memset(mark, 0, sizeof(mark));

	int target = mp[x][y];

	star_replace0(mp, flag, mark, row, col, x, y, target);

	int dx[] = { 1, -1, 0, 0 };
	int dy[] = { 0, 0, 1, -1 };
	bool has_adjacent_same = false;

	for (int i = 0; i < 4; i++)
	{
		int nx = x + dx[i];
		int ny = y + dy[i];
		if (nx >= 0 && nx < row && ny >= 0 && ny < col && mark[nx][ny] == 1)
		{
			has_adjacent_same = true;
			break;
		}
	}

	return has_adjacent_same;
}

int star_check(int array[][MAX_COLS], int array_around[][MAX_COLS], int row0, int col0)
{
	array_around[row0][col0] = '*';

	// 定义相邻位置的偏移量
	int directions[4][2] =
	{
		{-1, 0}, // 上
		{0, -1}, // 左
		{0, 1},  // 右
		{1, 0}   // 下
	};

	// 查找相邻元素
	for (int i = 0; i < 4; i++)
	{
		int new_row = row0 + directions[i][0];
		int new_column = col0 + directions[i][1];

		if (new_row >= 0 && new_row < 10 && new_column >= 0 && new_column < 10)
		{
			if (array[row0][col0] == array[new_row][new_column] &&
				array_around[new_row][new_column] != '*')
			{
				array_around[new_row][new_column] = '*';
				star_check(array, array_around, new_row, new_column);
			}
		}
	}

	// 统计标记的元素数量
	int count = 0;
	for (int i = 0; i < 10; i++)
	{
		for (int j = 0; j < 10; j++)
		{
			if (array_around[i][j] == '*')
				count++;
		}
	}

	return (count == 1) ? 0 : 1; // 返回是否有相邻元素
}

/***************************************************************************
	函数名称：find_new_position
	功    能：查找在给定行中的新位置
	输入参数：
	返 回 值：
	说    明：
***************************************************************************/
int find_new_position(int start, int direction, int cols, int rows[])
{
	int j_now = start;
	if (direction < 0)
	{
		for (int j_left = start - 1; j_left >= 0; j_left--)
		{
			if (rows[j_left] != 0)
			{
				j_now = j_left;
				break;
			}
		}
		if (j_now == start)
		{
			for (int j_1 = cols - 1; j_1 >= start; j_1--)
			{
				if (rows[j_1] != 0)
				{
					j_now = j_1;
					break;
				}
			}
		}
	}
	else {
		for (int j_right = start + 1; j_right < cols; j_right++)
		{
			if (rows[j_right] != 0)
			{
				j_now = j_right;
				break;
			}
		}
		if (j_now == start) {
			for (int j_1 = 0; j_1 <= start; j_1++)
			{
				if (rows[j_1] != 0)
				{
					j_now = j_1;
					break;
				}
			}
		}
	}
	return j_now;
}

/***************************************************************************
	函数名称：print_title
	功    能：显示当前鼠标位置/键盘位置/提示信息等
	输入参数：
	返 回 值：
	说    明：
***************************************************************************/
void print_title(int ret, int border, int rows, int cols, int i, int j, int array[][MAX_COLS], CONSOLE_GRAPHICS_INFO* PopStar_CGI)
{
	char temp[255];
	int X = i, Y = j;
	location_trans(1, i, j, X, Y, rows, cols, border);
	bool valid_position = check_border(X, Y, border, rows, cols, array);

	// 打印信息
	if (ret == CCT_MOUSE_EVENT || (ret == CCT_KEYBOARD_EVENT && border == 0))
	{
		if (valid_position) {
			if (ret == CCT_MOUSE_EVENT)
			{
				sprintf(temp, "[当前鼠标] %c行%c列                       ", (char)(i + 'A'), (char)(j + '0'));
				gmw_status_line(PopStar_CGI, LOWER_STATUS_LINE, temp);
			} 
			else if (ret == CCT_KEYBOARD_EVENT)
			{
				sprintf(temp, "[当前键盘] %c行%c列                       ", (char)(i + 'A'), (char)(j + '0'));
				gmw_status_line(PopStar_CGI, LOWER_STATUS_LINE, temp);
			}
		}
		else {
			if (ret == CCT_MOUSE_EVENT)
				gmw_status_line(PopStar_CGI, LOWER_STATUS_LINE, "[当前鼠标] 位置非法                                                    ");
			else if (ret == CCT_KEYBOARD_EVENT)
				gmw_status_line(PopStar_CGI, LOWER_STATUS_LINE, "[当前键盘] 位置非法                                                    ");
		}
	}
}

/***************************************************************************
	函数名称：check_border
	功    能：根据不同的border判断是否在合法区域
	输入参数：
	返 回 值：
	说    明：
***************************************************************************/
bool check_border(int X, int Y, int border, int rows, int cols, int array[][MAX_COLS])
{
	// 计算合法区域的范围
	int y_min = 3;
	int y_max = 3 + rows * (3 + border);
	int x_min = 4;
	int x_max = 4 + (6 + border * 2) * cols;

	// 检查是否在基本范围内
	if (Y < y_min || Y >= y_max || X < x_min || X >= x_max)
		return false;


	// 如果 border 为 1，进行额外的检查
	if (border == 1)
		if (!((Y - 3) % 4 <= 2 && (X - 4) % 8 <= 5))
			return false;

	// 转换坐标并检查数组值
	int i = X, j = Y;
	location_trans(-1, i, j, X, Y, rows, cols, border);
	return array[i][j] != 0; // 如果值不为0，返回 true
}

/***************************************************************************
	函数名称：go_right
	功    能：查看有无全零，将全零移动至最右侧
	返 回 值：
	说    明：
***************************************************************************/
void go_right(int array[][MAX_COLS], int rows, int cols, int have_block, CONSOLE_GRAPHICS_INFO* PopStar_CGI)
{
	int count = 0; // 记录已移动的全零列的数量

	for (int j = 0; j < cols - count; j++)
	{
		bool is_all_zero = true;

		// 检查列是否全为零
		for (int i = 0; i < rows; i++)
		{
			if (array[i][j] != 0)
			{
				is_all_zero = false;
				break;
			}
		}

		if (is_all_zero)
		{
			// 记录全零列的位置
			int col_to_move = j;
			count++;
			// 将全零列移动到最右侧
			move_zero_column_to_right(array, rows, cols, col_to_move, have_block, PopStar_CGI);
			j--; // 重新检查当前列的位置
		}
	}
}

/***************************************************************************
	函数名称：move_zero_column_to_right
	功    能：移动指定列到最右侧的函数
	返 回 值：
	说    明：
***************************************************************************/
void move_zero_column_to_right(int array[MAX_ROWS][MAX_COLS], int rows, int cols, int col_to_move, int have_block, CONSOLE_GRAPHICS_INFO* PopStar_CGI)
{
	const BLOCK_DISPLAY_INFO bdi_normal[] = {
		{0, -1, -1, "  "},  //0不显示，用空格填充即可
		{1, COLOR_HBLUE, COLOR_BLACK, "★"},
		{2, COLOR_HGREEN, COLOR_BLACK, "★"},
		{3, COLOR_HCYAN, COLOR_BLACK, "★"},
		{4, COLOR_HRED, COLOR_BLACK, "★"},
		{5, COLOR_HPINK, COLOR_BLACK, "★"},
		{-999, -1, -1, NULL} //判断结束条件为-999
	};

	for (int m = 0; m < rows; m++)
	{
		for (int n = col_to_move; n < cols - 1; n++)
		{
			array[m][n] = array[m][n + 1];
			array[m][n + 1] = 0;
			if (array[m][n] != 0 && have_block == 1)
			{
				gmw_draw_block(PopStar_CGI, m, n, array[m][n], bdi_normal);
				Sleep(10);
				gmw_draw_block(PopStar_CGI, m, n + 1, 0, bdi_normal);
				Sleep(10);
			}

		}
	}
}

/***************************************************************************
	函数名称：search_finish
	功    能：看不是0的元素->是否还有可消灭的星星
	返 回 值：0/1
	说    明：null
***************************************************************************/
int search_finish(int array[MAX_ROWS][MAX_COLS], int& left, int row, int col)
{
	int is_have = 0;
	for (int i = 0; i < row; i++)
	{
		for (int j = 0; j < col; j++)
		{
			if (array[i][j] != 0)
			{
				int array_around[MAX_ROWS][MAX_COLS] = { 0 };
				int is_have_have = 0;
				is_have_have = star_check(array, row, col, i, j);
				if (is_have_have == 1)
					is_have = 1;
				left++;
			}
		}
	}
	if (is_have)
		return 1;
	else
		return 0;

}