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
#include "90-02-b2-mine_sweeper.h"

using namespace std;

/***************************************************************************
  函数名称：mine_map_all
  功    能：扫雷所有操作
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
int mine_map_all(CONSOLE_GRAPHICS_INFO* MineSweeper_CGI, int choice)
{
    // 初始化变量和地图
    int mine_map[MAX_ROWS_MINE + 2][MAX_COLS_MINE + 2];
    int if_mine[MAX_ROWS_MINE + 2][MAX_COLS_MINE + 2];
    int mines;
    int remain0;
    char temp[255];
    int rows, cols;

    // 根据选择设置行列数和地雷数
    switch (choice)
    {
        case 1:
            rows = 9;
            cols = 9;
            mines = 10;
            break;
        case 2:
            rows = 16;
            cols = 16;
            mines = 40;
            break;
        case 3:
            rows = 16;
            cols = 30;
            mines = 99;
            break;
    }

    // 定义显示块的颜色和样式
    const BLOCK_DISPLAY_INFO bdi_normal[] = {
                {BDI_VALUE_BLANK, COLOR_HWHITE, -1, NULL},  //0不显示，用空格填充即可
                {1, COLOR_WHITE, 1, NULL},
                {2, COLOR_WHITE, 2, NULL},
                {3, COLOR_WHITE, 3, NULL},
                {4, COLOR_WHITE, 4, NULL},
                {5, COLOR_WHITE, 5, NULL},
                {6, COLOR_WHITE, 6, NULL},
                {7, COLOR_WHITE, 7, NULL},
                {8, COLOR_WHITE, 8, NULL},
                {9, COLOR_WHITE, COLOR_HRED, "*"},
                {BDI_VALUE_END, -1, -1, NULL} //判断结束条件为-999
    };
    const BLOCK_DISPLAY_INFO bdi_mark[] = {
                {BDI_VALUE_BLANK, COLOR_HWHITE, -1, NULL},  //0不显示，用空格填充即可
                {1, COLOR_HRED, COLOR_RED, "#"},
                {2, COLOR_YELLOW, COLOR_YELLOW, NULL},
                {BDI_VALUE_END, -1, -1, NULL} //判断结束条件为-999
    };

    // 初始化游戏界面
    gmw_init(MineSweeper_CGI);
    gmw_set_rowcol(MineSweeper_CGI, rows, cols);
    gmw_set_font(MineSweeper_CGI, "新宋体", 24);							//字体
    gmw_set_ext_rowcol(MineSweeper_CGI, 0, 0, 0, 1000);						//右边留30列
    gmw_set_color(MineSweeper_CGI, COLOR_BLACK, COLOR_HWHITE);			//整个窗口颜色
    gmw_set_frame_default_linetype(MineSweeper_CGI, 4);					//游戏主区域线型：横单竖双
    gmw_set_frame_color(MineSweeper_CGI, COLOR_HWHITE, COLOR_BLACK);		//游戏主区域颜色
    gmw_set_frame_style(MineSweeper_CGI, 2, 1, true);						//游戏主区域风格：每个色块宽2高1，无分隔线
    gmw_set_ext_rowcol(MineSweeper_CGI, 0, 3, 0, 10);						
    gmw_set_rowno_switch(MineSweeper_CGI, true);							//显示行号
    gmw_set_colno_switch(MineSweeper_CGI, true);							//显示列标
    gmw_set_status_line_switch(MineSweeper_CGI, TOP_STATUS_LINE, true);	//需要上状态栏
    gmw_set_status_line_switch(MineSweeper_CGI, LOWER_STATUS_LINE, true);	//需要下状态栏
    // 绘制框架
    gmw_draw_frame(MineSweeper_CGI);

    // 状态栏初始信息
    gmw_status_line(MineSweeper_CGI, TOP_STATUS_LINE, "ESC退出,空格显示时间");
    gmw_status_line(MineSweeper_CGI, LOWER_STATUS_LINE, "[当前光标]");
    srand(unsigned int(time(0)));

    // 初始化地图数组
    for (int i = 0; i < MAX_ROWS_MINE + 2; i++)
    {
        for (int j = 0; j < MAX_COLS_MINE + 2; j++)
        {
            if_mine[i][j] = 0; // 无雷标记
            mine_map[i][j] = 0; // 未打开标记
        }
    }

    // 随机放置地雷
    for (int i = 0; i < mines; i++)
    {
        int r = 1 + rand() % rows; // 随机行
        int c = 1 + rand() % cols; // 随机列
        if (if_mine[r][c] == 9) // 检查是否已放置地雷
        {
            i--; // 重试
            continue;
        }
        else
            if_mine[r][c] = 9; // 放置地雷
    }

    // 计算每个格子周围的地雷数量
    for (int i = 1; i <= rows; i++)
    {
        for (int j = 1; j <= cols; j++)
        {
            if (if_mine[i][j] == 9)
                continue; // 地雷格子跳过
            else
                if_mine[i][j] = check_mine(i, j, mine_map, if_mine);
        }
    }

    // 初始填充：全部关闭
    for (int i = 0; i < rows; i++)
        for (int j = 0; j < cols; j++)
            gmw_draw_block(MineSweeper_CGI, i, j, 2, bdi_mark);

    // 游戏主循环
    int MRow, MCol, MAction, keycode1, keycode2;
    int time = 0; // 记录是否为第一次
    bool win = false; // 是否胜利
    int remain = mines; // 记录剩余地雷数

    time_t start_time = clock(); // 记录开始时间
    while (1) {
        int ret = gmw_read_keyboard_and_mouse(MineSweeper_CGI, MAction, MRow, MCol, keycode1, keycode2, true);
        cct_setcursor(CURSOR_INVISIBLE); // 隐藏光标
        switch (ret)
        {
            case CCT_MOUSE_EVENT:
                if (MAction == MOUSE_LEFT_BUTTON_CLICK) // 左击打开
                {
                    if (mine_map[MRow + 1][MCol + 1] == 0) {
                        if (if_mine[MRow + 1][MCol + 1] == 9) // 踩雷
                        {
                            mine_map[MRow + 1][MCol + 1] = 1;
                            gmw_draw_block(MineSweeper_CGI, MRow, MCol, if_mine[MRow + 1][MCol + 1], bdi_normal);
                            time_t end_time = clock();
                            sprintf(temp, "当前时间:%f秒,ESC退出,空格显示时间", double(end_time - start_time) / CLOCKS_PER_SEC);
                            gmw_status_line(MineSweeper_CGI, TOP_STATUS_LINE, temp);
                            gmw_status_line(MineSweeper_CGI, LOWER_STATUS_LINE, "游戏结束,你输了");
                            return -1; // 退出
                        }

                        // 打开未知区域
                        open_unknown_area(MRow + 1, MCol + 1, rows, cols, mine_map, if_mine);
                        // 更新显示状态
                        for (int i = 0; i < rows; i++)
                        {
                            for (int j = 0; j < cols; j++)
                            {
                                if (mine_map[i + 1][j + 1] == 0) // 关闭
                                    gmw_draw_block(MineSweeper_CGI, i, j, 2, bdi_mark);
                                else if (mine_map[i + 1][j + 1] == 1) // 打开
                                    gmw_draw_block(MineSweeper_CGI, i, j, if_mine[i + 1][j + 1], bdi_normal);
                                else if (mine_map[i + 1][j + 1] == -1) // 标记
                                    gmw_draw_block(MineSweeper_CGI, i, j, 1, bdi_mark);
                            }
                        }
                    }

                    // 更新剩余雷数
                    remain0 = remain < 0 ? 0 : remain;
                    sprintf(temp, "剩余雷数:%d个,ESC退出,空格显示时间", remain0);
                    gmw_status_line(MineSweeper_CGI, TOP_STATUS_LINE, temp);
                }

                // 处理右键点击
                if (MAction == MOUSE_RIGHT_BUTTON_CLICK) {
                    if (mine_map[MRow + 1][MCol + 1] == 0) {
                        mine_map[MRow + 1][MCol + 1] = -1; // 标记雷
                        gmw_draw_block(MineSweeper_CGI, MRow, MCol, 1, bdi_mark);
                        remain--;
                    }
                    else if (mine_map[MRow + 1][MCol + 1] == -1) {
                        mine_map[MRow + 1][MCol + 1] = 0; // 取消标记
                        gmw_draw_block(MineSweeper_CGI, MRow, MCol, 2, bdi_mark);
                        remain++;
                    }

                    // 更新剩余雷数
                    remain0 = remain < 0 ? 0 : remain;
                    sprintf(temp, "剩余雷数:%d个,ESC退出,空格显示时间", remain0);
                    gmw_status_line(MineSweeper_CGI, TOP_STATUS_LINE, temp);
                }
                break;

            case CCT_KEYBOARD_EVENT:
                if (keycode1 == 27) // ESC退出
                    return -1;
                else if (keycode1 == 32) { // 空格显示时间
                    time_t end_time = clock();
                    sprintf(temp, "当前时间:%f秒,ESC退出,空格显示时间", double(end_time - start_time) / CLOCKS_PER_SEC);
                    gmw_status_line(MineSweeper_CGI, TOP_STATUS_LINE, temp);
                }
        }

        // 检测是否获胜
        int cnt = 0;
        for (int i = 1; i <= rows; i++)
        {
            for (int j = 1; j <= cols; j++)
            {
                if (mine_map[i][j] == 1)
                    cnt++; // 计数已打开的格子
            }
        }
        if (cnt == (rows * cols - mines)) // 胜利条件
        { 
            for (int i = 0; i < rows; i++)
            {
                for (int j = 0; j < cols; j++)
                {
                    if (mine_map[i + 1][j + 1] == 0) // 关闭
                        gmw_draw_block(MineSweeper_CGI, i, j, 2, bdi_mark);
                    else if (mine_map[i + 1][j + 1] == 1) // 打开
                        gmw_draw_block(MineSweeper_CGI, i, j, if_mine[i + 1][j + 1], bdi_normal);
                    else if (mine_map[i + 1][j + 1] == -1) // 标记
                        gmw_draw_block(MineSweeper_CGI, i, j, 1, bdi_mark);
                }
            }

            // 游戏胜利处理
            time_t end_time = clock(); // 记录结束时间
            double elapsed_time = double(end_time - start_time) / CLOCKS_PER_SEC;
            sprintf(temp, "当前时间:%f秒,ESC退出,空格显示时间", elapsed_time);
            gmw_status_line(MineSweeper_CGI, TOP_STATUS_LINE, temp);
            gmw_status_line(MineSweeper_CGI, LOWER_STATUS_LINE, ",你赢了", "游戏结束");
            return 0; // 退出
        }
    }
    return 0; // 默认返回
}


/***************************************************************************
  函数名称：check_mine
  功    能：计数
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
int check_mine(int row, int col, int mine_map[MAX_ROWS_MINE + 2][MAX_COLS_MINE + 2], int if_mine[MAX_ROWS_MINE + 2][MAX_COLS_MINE + 2])
{
	int cnt = 0;
	for (int i = row - 1; i <= row + 1; i++) {
		for (int j = col - 1; j <= col + 1; j++) {
			if (i == row && j == col)
				continue;
			if (if_mine[i][j] == 9)
				cnt++;
		}
	}
	return cnt;
}

/***************************************************************************
  函数名称：open_unknown_area
  功    能：打开没有雷的地方
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void open_unknown_area(int row, int col, int row_num, int col_num, int mine_map[MAX_ROWS_MINE + 2][MAX_COLS_MINE + 2], int if_mine[MAX_ROWS_MINE + 2][MAX_COLS_MINE + 2])
{
	// 边界检查
	if (row < 1 || row > row_num || col < 1 || col > col_num) {
		return; // 超出范围
	}

	// 打开当前方块
	mine_map[row][col] = 1;

	// 如果是空方块，递归打开周围的方块
	if (if_mine[row][col] == 0) {
		for (int i = row - 1; i <= row + 1; i++) {
			for (int j = col - 1; j <= col + 1; j++) {
				// 确保新位置在有效范围内且未打开
				if (mine_map[i][j] == 0) {
					open_unknown_area(i, j, row_num, col_num, mine_map, if_mine);
				}
			}
		}
	}
}