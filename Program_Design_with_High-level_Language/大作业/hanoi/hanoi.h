/* 2352018 信06 刘彦 */
#pragma once

/* ------------------------------------------------------------------------------------------------------

     本文件功能：
	1、为了保证 hanoi_main.cpp/hanoi_menu.cpp/hanoi_multiple_solutions.cpp 能相互访问函数的函数声明
	2、一个以上的cpp中用到的宏定义（#define）或全局只读（const）变量，个数不限
	3、可以参考 cmd_console_tools.h 的写法（认真阅读并体会）


   ------------------------------------------------------------------------------------------------------ */
#define LOC_X_A 11
#define LOC_X_B 21
#define LOC_X_C 31
#define LOC_Y_4 14
#define LOC_Y_8 34
#define LOC_ROW_X 0
#define LOC_ROW_Y 19
#define LOC_COLUMN 10
#define LOC_LINE_X 10
#define LOC_LINE_Y 13
#define LOC_ENTER_X 0
#define LOC_ENTER_Y 30
#define BOTTOM_WIDTH 23
#define BOTTOM_X 1
#define BOTTOM_Y 15
#define STICK_WIDTH 1
#define LOC_TOWER 32
#define TIME_SLEEP 45
#define X_9 60
#define Y_9 35
#define MAX_9 20

//菜单函数
int hanoi_menu();

//基础函数
void my_speed();   //处理移动速度,并返回设定的speed的值
void my_input(int& storey, char& src, char& dst, char& tmp);   //输入并处理输入错误
int hanoi_all(int choice);   //汇总整个汉诺塔的输出函数
char hanoi_move(int n, char src, char tmp, char dst);
void hanoi(int n, char src, char tmp, char dst, int choice);   //汉诺塔递归函数

//功能函数
void print();   //打印数组
void printTower1(int tower[], char label);   //打印数组第一列
void printTower2(int tower[], char label);   //打印数组第二列
void printTower3(int tower[], char label);   //打印数组第三列
void move(char src, char dst);   //移动数组
void moveA(char dst);   //移动数组A
void moveB(char dst);   //移动数组B
void moveC(char dst);   //移动数组C
void move_plate(char src, char dst);   //移动盘子
void print_line(int n, char src, char tmp, char dst, int choice);   //逐行输出数组
void print_row(int n, char src, char tmp, char dst, int choice);   //横向输出数组
void print_column_base(int choice);   //纵向输出数组的基础结构
void print_column_tower(int choice);   //纵向输出数组中的数
void init(int n, int src, int choice);   //初始化
int init_plate_height(char src);   //初始化盘子高度
int init_plate_width(char src);   //初始化盘子宽度
int init_plate_color(char src);   //初始化盘子颜色
int init_plate_dst(char dst);   //初始化目标柱
void getInput(char(&input)[MAX_9]);

//辅助函数
void draw_tower(int n, int src, int choice);   //打印底座，柱子和盘
void draw_move(char src, char x, int i);   //盘移动时的辅助函数1
void drawCharacter(int x, int y, int flag, int color, int width);   //盘移动时的辅助函数2
char capital(char x);   //转大写
void my_sleep();   //控制时间
void blank();