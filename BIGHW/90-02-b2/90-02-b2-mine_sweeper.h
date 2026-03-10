/* 2352018 ¥Û ˝æ› ¡ı—Â */
#pragma once

#define MAX_ROWS_MINE 16
#define MAX_COLS_MINE 30


int check_mine(int row, int col, int mine_map[18][32], int if_mine[18][32]);
int mine_map_all(CONSOLE_GRAPHICS_INFO* MineSweeper_CGI, int choice);
void open_unknown_area(int row, int col, int row_num, int col_num, int mine_map[18][32], int if_mine[18][32]);