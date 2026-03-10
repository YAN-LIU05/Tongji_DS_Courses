/* 2352018 大数据 刘彦 */
#pragma once

#define MIN_ROWS  5
#define MAX_ROWS  10
#define MIN_COLS  5
#define MAX_COLS  10
#define TIME 20


int ball_base_all(int choice);   //base的汇总函数


void print_mark(int rows, int cols, int array[MIN_ROWS][MAX_ROWS]);   //打印初始可消除项
void print_tips(int rows, int cols, int array[MIN_ROWS][MAX_ROWS]);   //打印提示项
void base_remove(int array[MAX_ROWS][MAX_COLS], int rows, int cols, int choice);   //相同数字的消除和0的设置
void draw_ball(int i, int j, int color, int border);   //画出彩球
void draw_clean(int i, int j, int color);   //消除彩球
void draw_nine(int array[MIN_ROWS][MAX_ROWS], int rows, int cols, int choice);   //第9步的汇总函数
int draw_fall(int array[MAX_ROWS][MAX_COLS], int rows, int cols, int choice, int array0[MAX_ROWS][MAX_COLS], int have_score);   //消除彩球
void move_elements_down(int array[][MAX_COLS], int rows, int cols);   //让彩球下移



int tj_strcasecmp(const char* s1, const char* s2);   //比较字符串s1和s2的大小,英文字母不分大小写
