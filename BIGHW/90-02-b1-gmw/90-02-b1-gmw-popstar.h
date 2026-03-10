/* 2352018 ¥Û ˝æ› ¡ı—Â */
#pragma once

#define MIN_ROWS  8
#define MAX_ROWS  10
#define MIN_COLS  8
#define MAX_COLS  10
#define MAX_LENGTH 255

void draw_map(int rows, int cols, const int border, int array[][MAX_COLS], int choice, CONSOLE_GRAPHICS_INFO* pPopStar_CGI);
bool check_border(int X, int Y, int border, int rows, int cols, int array[][MAX_COLS]);
int move_by_keyboard_and_mouse(int rows, int cols, const int border, int array[][MAX_COLS], int total, CONSOLE_GRAPHICS_INFO* pPopStar_CGI);
void print_title(int ret, int border, int rows, int cols, int i, int j, int array[][MAX_COLS], CONSOLE_GRAPHICS_INFO* PopStar_CGI);
int find_new_position(int start, int direction, int cols, int rows[]);
int search_finish(int array[MAX_ROWS][MAX_COLS], int& left, int row, int col);
void star_replace0(int mp[MAX_ROWS][MAX_COLS], int flag[MAX_ROWS][MAX_COLS], int mark[MAX_ROWS][MAX_COLS], int row, int col, int x, int y, int target);
int star_check(int array[][MAX_COLS], int array_around[][MAX_COLS], int row0, int col0);
int star_check(int mp[MAX_ROWS][MAX_COLS], int row, int col, int x, int y);
void pop_together(int rows, int cols, int border, int array[][MAX_COLS], int i_last, int j_last, CONSOLE_GRAPHICS_INFO* PopStar_CGI);
void move_zero_column_to_right(int array[MAX_ROWS][MAX_COLS], int rows, int cols, int col_to_move, int have_block, CONSOLE_GRAPHICS_INFO* pPopStar_CGI);
void go_right(int array[][MAX_COLS], int rows, int cols, int have_block, CONSOLE_GRAPHICS_INFO* pPopStar_CGI);
bool draw_around(int rows, int cols, int border, int array[][MAX_COLS], int array_around[][MAX_COLS], int choice, int i_last, int j_last, CONSOLE_GRAPHICS_INFO* PopStar_CGI);