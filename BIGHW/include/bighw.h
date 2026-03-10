/* 2352018 大数据 刘彦 */
#pragma once

#define MAX_COLS  10
#define MAX_ROWS  10
#define TIME 20

char all_menu(int num);

int tj_strlen(const char* str);
char* tj_strcpy(char* s1, const char* s2);
int tj_strcasecmp(const char* s1, const char* s2);

void print_origin(int rows, int cols, int array[][MAX_ROWS], int num1, int num2);
void set_botton(bool set, int num);
void single_outline(int col, const int border);
void draw_border(int rows, int cols, bool border, int choice, int which);
void location_trans(const int drc, int& i, int& j, int& X, int& Y, int rows, int cols, int border);
void draw_block(int i, int j, int border, int array[][MAX_COLS], int rows, int cols, int state);
void element_fall(int array[][MAX_COLS], int array_around[][MAX_COLS], int rows, int cols, int have_block, int opt);
void zero_drop(int array[MAX_ROWS][MAX_COLS], int rows, int cols);
int find_empty_above(int i_last, int j_last, int array[][MAX_COLS], int rows);
void fill_array(int array[MAX_ROWS][MAX_COLS], int rows, int cols, int num);
void copy_array(const int source[MAX_ROWS][MAX_COLS], int destination[MAX_ROWS][MAX_COLS], int rows, int cols);

bool base_check0(const int array[MAX_ROWS][MAX_COLS], int row, int col, int rows, int cols);   //检查是否可以消除
bool base_check1(const int array[MAX_ROWS][MAX_COLS], int rows, int cols);   //检查是否有初始可消除项
bool base_check2(const int array[MAX_ROWS][MAX_COLS], const int directions[4][2], int row, int col, int rows, int cols);   //检查是否可以提示