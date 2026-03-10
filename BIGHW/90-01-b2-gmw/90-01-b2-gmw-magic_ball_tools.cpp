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
#include "90-01-b2-gmw-magic_ball.h"

using namespace std;

/***************************************************************************
	函数名称：ball_base_all
	功    能：显示界面全局图形
	输入参数：
	返 回 值：
	说    明：
***************************************************************************/
int ball_base_all(CONSOLE_GRAPHICS_INFO* pMagicBall_CGI, int rows, int cols)
{
	/* 定义1-9的数字用何种形式显示在界面上（正常状态） */
	const BLOCK_DISPLAY_INFO bdi_normal[] = {
		{BDI_VALUE_BLANK, -1, -1, "  "},  //0不显示，用空格填充即可
		{1, COLOR_HBLACK, -1, "〇"},
		{2, COLOR_YELLOW, -1, "〇"},
		{3, COLOR_HGREEN, -1, "〇"},
		{4, COLOR_HCYAN, -1, "〇"},
		{5, COLOR_HRED, -1, "〇"},
		{6, COLOR_HPINK, -1, "〇"},
		{7, COLOR_HYELLOW, -1, "〇"},
		{8, COLOR_CYAN, -1, "〇"},
		{9, COLOR_WHITE, -1, "〇"},
		{BDI_VALUE_END, -1, -1, NULL} //判断结束条件为-999
	};
	const BLOCK_DISPLAY_INFO bdi_normal_choose[] = {
		{BDI_VALUE_BLANK, -1, -1, "  "},  //0不显示，用空格填充即可
		{1, COLOR_HBLACK, 15, "〇"},
		{2, COLOR_YELLOW, 15, "〇"},
		{3, COLOR_HGREEN, 15, "〇"},
		{4, COLOR_HCYAN, 15, "〇"},
		{5, COLOR_HRED, 15, "〇"},
		{6, COLOR_HPINK, 15, "〇"},
		{7, COLOR_HYELLOW, 15, "〇"},
		{8, COLOR_CYAN, 15, "〇"},
		{9, COLOR_WHITE, 15, "〇"},
		{BDI_VALUE_END, -1, -1, NULL} //判断结束条件为-999
	};
	/* 定义1-9的数字用何种形式显示在界面上（选中状态） */
	const BLOCK_DISPLAY_INFO bdi_selected[] = {
		{BDI_VALUE_BLANK, -1, -1, "  "},  //空白
		{1, COLOR_HBLACK, -1, "●"},
		{2, COLOR_YELLOW, -1, "●"},
		{3, COLOR_HGREEN, -1, "●"},
		{4, COLOR_HCYAN, -1, "●"},
		{5, COLOR_HRED, -1, "●"},
		{6, COLOR_HPINK, -1, "●"},
		{7, COLOR_HYELLOW, -1, "●"},
		{8, COLOR_CYAN, -1, "●"},
		{9, COLOR_WHITE, -1, "●"},
		{BDI_VALUE_END, -1, -1, NULL} //判断结束条件为-999
	};
	/* 定义1-9的数字用何种形式显示在界面上（可消除提示状态） */
	const BLOCK_DISPLAY_INFO bdi_prompt[] = {
		{BDI_VALUE_BLANK, -1, -1, "  "},  //空白
		{1, COLOR_HBLACK, -1, "◎"},
		{2, COLOR_YELLOW, -1, "◎"},
		{3, COLOR_HGREEN, -1, "◎"},
		{4, COLOR_HCYAN, -1, "◎"},
		{5, COLOR_HRED, -1, "◎"},
		{6, COLOR_HPINK, -1, "◎"},
		{7, COLOR_HYELLOW, -1, "◎"},
		{8, COLOR_CYAN, -1, "◎"},
		{9, COLOR_WHITE, -1, "◎"},
		{BDI_VALUE_END, -1, -1, NULL} //判断结束条件为-999
	};
	/* 定义1-9的数字用何种形式显示在界面上（可消除提示状态） */
	const BLOCK_DISPLAY_INFO bdi_prompt_choose[] = {
		{BDI_VALUE_BLANK, -1, -1, "  "},  //空白
		{1, COLOR_HBLACK, 15, "◎"},
		{2, COLOR_YELLOW, 15, "◎"},
		{3, COLOR_HGREEN, 15, "◎"},
		{4, COLOR_HCYAN, 15, "◎"},
		{5, COLOR_HRED, 15, "◎"},
		{6, COLOR_HPINK, 15, "◎"},
		{7, COLOR_HYELLOW, 15, "◎"},
		{8, COLOR_CYAN, 15, "◎"},
		{9, COLOR_WHITE, 15, "◎"},
		{BDI_VALUE_END, -1, -1, NULL} //判断结束条件为-999
	};
	/* 定义1-9的数字用何种形式显示在界面上（爆炸/消除状态） */
	const BLOCK_DISPLAY_INFO bdi_exploded[] = {
		{BDI_VALUE_BLANK, -1, -1, "  "},  //空白
		{1, COLOR_HBLACK, -1, "¤"},
		{2, COLOR_YELLOW, -1, "¤"},
		{3, COLOR_HGREEN, -1, "¤"},
		{4, COLOR_HCYAN, -1, "¤"},
		{5, COLOR_HRED, -1, "¤"},
		{6, COLOR_HPINK, -1, "¤"},
		{7, COLOR_HYELLOW, -1, "¤"},
		{8, COLOR_CYAN, -1, "¤"},
		{9, COLOR_WHITE, -1, "¤"},
		{BDI_VALUE_END, -1, -1, NULL} //判断结束条件为-999
	};

	srand(static_cast<unsigned int>(time(nullptr)));
	int array[MAX_ROWS][MAX_COLS];   //填充数组为随机数
	fill_array(array, rows, cols, 1);
	gmw_init(pMagicBall_CGI);
	gmw_set_font(pMagicBall_CGI, "新宋体", 32);							//字体
	gmw_set_ext_rowcol(pMagicBall_CGI, 0, 0, 0, 30);						//右边留30列
	gmw_set_color(pMagicBall_CGI, COLOR_BLACK, COLOR_HWHITE);			//整个窗口颜色
	gmw_set_frame_default_linetype(pMagicBall_CGI, 4);					//游戏主区域线型：横单竖双
	gmw_set_frame_color(pMagicBall_CGI, COLOR_HWHITE, COLOR_BLACK);		//游戏主区域颜色
	
	gmw_set_frame_style(pMagicBall_CGI, 2, 1, false);						//游戏主区域风格：每个色块宽2高1，无分隔线
	gmw_set_ext_rowcol(pMagicBall_CGI, 0, 3, 0, 10);						
	gmw_set_rowno_switch(pMagicBall_CGI, true);							//显示行号
	gmw_set_colno_switch(pMagicBall_CGI, true);							//显示列标
	gmw_set_status_line_switch(pMagicBall_CGI, TOP_STATUS_LINE, true);	//需要上状态栏
	gmw_set_status_line_switch(pMagicBall_CGI, LOWER_STATUS_LINE, true);	//需要下状态栏

	char temp[256];
	int i, j;
	int directions[4][2] = { {-1, 0}, {1, 0}, {0, -1}, {0, 1} };   //方向数组
	/* 按row/col的值重设游戏主区域行列 */
	gmw_set_rowcol(pMagicBall_CGI, rows, cols);

	/* 显示框架 */

	gmw_draw_frame(pMagicBall_CGI);

	/* 上状态栏显示内容 */

	sprintf(temp, "屏幕：%d行 %d列", pMagicBall_CGI->lines, pMagicBall_CGI->cols);
	cct_showstr(0, 0, temp, 0, 15);

	/* 将内部数组展现到屏幕上 */
	for (i = 0; i < rows; i++)
		for (j = 0; j < cols; j++) 
				gmw_draw_block(pMagicBall_CGI, i, j, array[i][j], bdi_normal);
	int arrayCopy[MAX_ROWS][MAX_COLS];
	int arrayCopy0[MAX_ROWS][MAX_COLS];
	int arrayCopy1[MAX_ROWS][MAX_COLS];

    copy_array(array, arrayCopy, rows, cols);
	copy_array(array, arrayCopy0, rows, cols);
	while (base_check1(arrayCopy, rows, cols)) 
	{
		for (i = 0; i < rows; i++)
			for (j = 0; j < cols; j++)
				gmw_draw_block(pMagicBall_CGI, i, j, arrayCopy[i][j], bdi_normal);
		// 第一步：标记可消除的块
		for (int i = 0; i < rows; i++) 
			for (int j = 0; j < cols; j++)
				if (base_check0(arrayCopy0, i, j, rows, cols)) 
					gmw_draw_block(pMagicBall_CGI, i, j, arrayCopy[i][j], bdi_selected);

		cct_setcursor(CURSOR_INVISIBLE);

		// 第二步：执行消除动画并将块设置为0
		copy_array(arrayCopy, arrayCopy1, rows, cols);
		for (int i = 0; i < rows; i++)
		{
			for (int j = 0; j < cols; j++) 
			{
				if (base_check0(arrayCopy1, i, j, rows, cols)) 
				{
					for (int k = 0; k < 5; k++) 
					{
						gmw_draw_block(pMagicBall_CGI, i, j, arrayCopy[i][j], bdi_exploded);
						Sleep(50);
						gmw_draw_block(pMagicBall_CGI, i, j, 0, bdi_normal); // 0是空白
						Sleep(50);
					}
					arrayCopy[i][j] = 0; // 设置为0
				}
			}
		}

		// 第三步：让上面的块下落
		for (int j = 0; j < cols; j++) 
		{
			int targetRow = rows - 1; // 从底部开始的目标行
			for (int i = rows - 1; i >= 0; --i) 
			{
				if (arrayCopy[i][j] != 0) // 找到非0块
				{ 
					// 如果目标行不等于当前行，则移动
					if (i != targetRow) 
					{
						gmw_move_block(pMagicBall_CGI, i, j, arrayCopy[i][j], 0, bdi_normal, UP_TO_DOWN, targetRow - i);
						Sleep(50);
					}
					arrayCopy[targetRow][j] = arrayCopy[i][j]; // 更新目标位置
					if (targetRow != i) 
						arrayCopy[i][j] = 0; // 将原位置设置为0
					targetRow--; // 移动目标行到上一行
				}
			}
		}

		// 第四步：填充新值
		srand(static_cast<unsigned int>(time(nullptr))); // 初始化随机数种子
		for (int i = 0; i < rows; i++) 
		{
			for (int j = 0; j < cols; j++) {

				if (arrayCopy[i][j] == 0) { // 如果是0，则填充新值
					arrayCopy[i][j] = (rand() % 9) + 1; // 填充1到9之间的随机值
					gmw_draw_block(pMagicBall_CGI, i, j, arrayCopy[i][j], bdi_normal); // 绘制新块
					Sleep(50);
				}
			}
		}
		copy_array(arrayCopy, arrayCopy0, rows, cols);
	}

	for (i = 0; i < rows; i++)
		for (j = 0; j < cols; j++)
		{
			if (base_check2(arrayCopy, directions, i, j, rows, cols))
				gmw_draw_block(pMagicBall_CGI, i, j, arrayCopy[i][j], bdi_prompt);
			else
				gmw_draw_block(pMagicBall_CGI, i, j, arrayCopy[i][j], bdi_normal);
		}
	int num0 = 0;
	int score_all = 0, score = 0;
	int loop = 1;
	int maction, old_mrow, old_mcol, mrow = -1, mcol = -1;
	int keycode1, keycode2;
	int ret;
	int i1 = 0, j1 = 0, i2 = 0, j2 = 0;
	int count0 = 0;
	cct_setcursor(CURSOR_INVISIBLE);
	while (loop) {
		count0 = 0;
		score = 0;
		old_mrow = mrow;
		old_mcol = mcol;
		ret = gmw_read_keyboard_and_mouse(pMagicBall_CGI, maction, mrow, mcol, keycode1, keycode2);

		if (ret == CCT_MOUSE_EVENT) 
		{
			if (maction == MOUSE_ONLY_MOVED) 
			{
				/* 这时，mrow、mcol肯定跟刚才不同 */

				/* 做一个色块变化（color_linez不是所有位置都有色块，此处直接用3代替），不同游戏此处不同，仅仅是个演示 */

				/* 原色块正常显示 */
				if (old_mrow >= 0 && old_mcol >= 0)
					if (base_check2(arrayCopy, directions, old_mrow, old_mcol, rows, cols))
						gmw_draw_block(pMagicBall_CGI, old_mrow, old_mcol, arrayCopy[old_mrow][old_mcol], bdi_prompt);
					else
						gmw_draw_block(pMagicBall_CGI, old_mrow, old_mcol, arrayCopy[old_mrow][old_mcol], bdi_normal);

				/* 新色块亮显（因为不是所有色块都有值，此处用3替代） */
				if (base_check2(arrayCopy, directions, mrow, mcol, rows, cols))
					gmw_draw_block(pMagicBall_CGI, mrow, mcol, arrayCopy[mrow][mcol], bdi_prompt_choose);
				else
					gmw_draw_block(pMagicBall_CGI, mrow, mcol, arrayCopy[mrow][mcol], bdi_normal_choose);

			}
			else if (maction == MOUSE_RIGHT_BUTTON_CLICK) 
			{
				/* 下状态栏显示内容 */
				gmw_status_line(pMagicBall_CGI, LOWER_STATUS_LINE, "[读到右键]", NULL);
				loop = 0;
			}
			else 
			{
				char temp0[256];
				num0++;
				if (base_check2(arrayCopy, directions, mrow, mcol, rows, cols))
				{
					sprintf(temp0, "[当前选择] %c行%d列", char('A' + mrow), mcol); //未考虑mrow超过26，mcol超过99的情况，如有需要，请自行处理
					gmw_status_line(pMagicBall_CGI, LOWER_STATUS_LINE, temp0);
					if (num0 % 2 == 1)
					{
					    i1 = mrow;
					    j1 = mcol;
					}
					if (num0 % 2 == 0)
					{
						i2 = mrow;
						j2 = mcol;
						int tmp0;
						tmp0 = arrayCopy[i1][j1];
						arrayCopy[i1][j1] = arrayCopy[i2][j2];
						arrayCopy[i2][j2] = tmp0;
						if (base_check0(arrayCopy, i1, j1, rows, cols) || base_check0(arrayCopy, i2, j2, rows, cols))
						{

							for (i = 0; i < rows; i++)
								for (j = 0; j < cols; j++)
									gmw_draw_block(pMagicBall_CGI, i, j, arrayCopy[i][j], bdi_normal);
							sprintf(temp, "交换%c行%d列<=>%c行%d列", char(i1 + 'A'), j1, char(i2 + 'A'), j2);
							gmw_status_line(pMagicBall_CGI, LOWER_STATUS_LINE, temp, NULL);
							

							while (base_check1(arrayCopy, rows, cols))
							{

								// 第一步：标记可消除的块
								for (int i = 0; i < rows; i++) 
									for (int j = 0; j < cols; j++) 
										if (base_check0(arrayCopy, i, j, rows, cols)) 
											gmw_draw_block(pMagicBall_CGI, i, j, arrayCopy[i][j], bdi_selected);
											Sleep(100);
								Sleep(100);
								cct_setcursor(CURSOR_INVISIBLE);

								// 第二步：执行消除动画并将块设置为0
								copy_array(arrayCopy, arrayCopy1, rows, cols);
								for (int i = 0; i < rows; i++)
								{
									for (int j = 0; j < cols; j++) 
									{
										if (base_check0(arrayCopy1, i, j, rows, cols)) 
										{
											for (int k = 0; k < 5; k++) 
											{
												gmw_draw_block(pMagicBall_CGI, i, j, arrayCopy[i][j], bdi_exploded);
												Sleep(50);
												gmw_draw_block(pMagicBall_CGI, i, j, 0, bdi_normal); // 0是空白
												Sleep(50);
											}
											arrayCopy[i][j] = 0; // 设置为0
										}
									}
								}

								// 第三步：让上面的块下落
								for (int j = 0; j < cols; j++) 
								{
									int targetRow = rows - 1; // 从底部开始的目标行
									for (int i = rows - 1; i >= 0; --i) 
									{
										if (arrayCopy[i][j] != 0)  // 找到非0块
										{
											// 如果目标行不等于当前行，则移动
											if (i != targetRow) 
											{
												gmw_move_block(pMagicBall_CGI, i, j, arrayCopy[i][j], 0, bdi_normal, UP_TO_DOWN, targetRow - i);
												Sleep(50);
											}
											arrayCopy[targetRow][j] = arrayCopy[i][j]; // 更新目标位置
											if (targetRow != i) 
												arrayCopy[i][j] = 0; // 将原位置设置为0
											targetRow--; // 移动目标行到上一行
										}
									}
								}

								// 第四步：填充新值
								srand(static_cast<unsigned int>(time(nullptr))); // 初始化随机数种子
								for (int i = 0; i < rows; i++) 
								{
									for (int j = 0; j < cols; j++) 
									{
										if (arrayCopy[i][j] == 0) // 如果是0，则填充新值
										{ 
											score++;
											arrayCopy[i][j] = (rand() % 9) + 1; // 填充1到9之间的随机值
											gmw_draw_block(pMagicBall_CGI, i, j, arrayCopy[i][j], bdi_normal); // 绘制新块
											Sleep(50);
										}
									}
								}
								copy_array(arrayCopy, arrayCopy0, rows, cols);
							}
							score_all += score;
							sprintf(temp, "屏幕：%d行 %d列 (当前分数:%d)", pMagicBall_CGI->lines, pMagicBall_CGI->cols, score_all);
							cct_showstr(0, 0, temp, 0, 15);
							for (i = 0; i < rows; i++)
								for (j = 0; j < cols; j++)
								{
									if (base_check2(arrayCopy, directions, i, j, rows, cols))
										gmw_draw_block(pMagicBall_CGI, i, j, arrayCopy[i][j], bdi_prompt);
									else
										gmw_draw_block(pMagicBall_CGI, i, j, arrayCopy[i][j], bdi_normal);
								}
							for (int i = 0; i < rows; i++)
							{
								for (int j = 0; j < cols; j++)
								{
									if (base_check2(arrayCopy0, directions, i, j, rows, cols))
									{
										count0++; // 如果找到满足条件的位置，增加计数
									}
								}
							}

							if (count0 == 0) 
								loop = 0; // 如果没有找到任何满足条件的位置，退出循环
					    }
						else
						{
							sprintf(temp, "不能交换%c行%d列<=>%c行%d列", char(i1 + 'A'), j1, char(i2 + 'A'), j2);
							gmw_status_line(pMagicBall_CGI, LOWER_STATUS_LINE, temp, NULL);
							num0 = 0;
						}
					
					}

				}
				else
				{
					i1 = mrow;
					j1 = mcol;
					sprintf(temp, "不能选择%c行%d列", char(i1 + 'A'), j1);
					gmw_status_line(pMagicBall_CGI, LOWER_STATUS_LINE, temp, NULL);
				}

				
			}
		}

	}
	sprintf(temp, "最终分数:%d", score_all);
	gmw_status_line(pMagicBall_CGI, LOWER_STATUS_LINE, temp, "无可消除项, 游戏结束!");
	Sleep(300);
	gmw_status_line(pMagicBall_CGI, LOWER_STATUS_LINE, "本小题结束，请输入End继续... ", "");
	return 0;
}
