/* 2352018 大数据 刘彦 */
#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <climits>
#include <conio.h>
#include <iomanip>
#include <windows.h>
#include <sstream>
#include "../include/cmd_console_tools.h"
#include "../include/cmd_gmw_tools.h"
using namespace std;

/* --------------------------------------------------
		此处可以给出需要的静态全局变量（尽可能少，最好没有）、静态全局只读变量/宏定义（个数不限）等
   -------------------------------------------------- */


   /* --------------------------------------------------
		   此处可以给出需要的内部辅助工具函数
		   1、函数名不限，建议为 gmw_inner_*
		   2、个数不限
		   3、必须是static函数，确保只在本源文件中使用
	  -------------------------------------------------- */
	  /***************************************************************************
		函数名称：
		功    能：计算框架的尺寸
		输入参数：CONSOLE_GRAPHICS_INFO* const pCGI：整体结构指针
		返 回 值：无
		说    明：根据框架的色块尺寸和分隔符设置计算框架的总宽度和总高度。
	  ***************************************************************************/
static void gmw_inner_calculate_frame_size(CONSOLE_GRAPHICS_INFO* const pCGI)
{
	if (pCGI->CFI.separator)
	{
		// 框架总宽度
		pCGI->CFI.bwidth = (pCGI->CFI.block_width + pCGI->CFI.separator * 2) * pCGI->col_num + 2;
		// 框架总高度
		pCGI->CFI.bhigh = (pCGI->CFI.block_high + pCGI->CFI.separator) * pCGI->row_num + 1;
	}
	else
	{
		pCGI->CFI.bwidth = pCGI->CFI.block_width * pCGI->col_num + 4; // 2*2
		pCGI->CFI.bhigh = pCGI->CFI.block_high * pCGI->row_num + 2; // 1*2
	}
}

/***************************************************************************
  函数名称：
  功    能：计算框架的起始位置
  输入参数：CONSOLE_GRAPHICS_INFO* const pCGI：整体结构指针
  返 回 值：无
  说    明：根据外部行列数和状态栏信息计算框架的起始坐标（x, y）。
***************************************************************************/
static void gmw_inner_calculate_start_positions(CONSOLE_GRAPHICS_INFO* const pCGI)
{
	// 框架起始x坐标
	pCGI->start_x = pCGI->extern_left_cols + 2 * pCGI->draw_frame_with_row_no;
	// 框架起始y坐标
	pCGI->start_y = pCGI->extern_up_lines + pCGI->top_status_line + pCGI->draw_frame_with_col_no;
}

/***************************************************************************
  函数名称：
  功    能：计算屏幕的总尺寸
  输入参数：CONSOLE_GRAPHICS_INFO* const pCGI：整体结构指针
  返 回 值：无
  说    明：根据外部行列数、框架尺寸和状态栏信息计算屏幕的总宽度和高度。
***************************************************************************/
static void gmw_inner_calculate_screen_size(CONSOLE_GRAPHICS_INFO* const pCGI)
{
	// 屏幕总高度
	pCGI->lines = pCGI->extern_up_lines + pCGI->top_status_line + pCGI->draw_frame_with_col_no +
		pCGI->CFI.bhigh + pCGI->lower_status_line + pCGI->extern_down_lines + 4;
	// 屏幕总宽度
	pCGI->cols = pCGI->extern_left_cols + 2 * pCGI->draw_frame_with_row_no +
		pCGI->CFI.bwidth + pCGI->extern_right_cols + 1;
}

/***************************************************************************
  函数名称：
  功    能：计算状态栏的起始位置
  输入参数：CONSOLE_GRAPHICS_INFO* const pCGI：整体结构指针
  返 回 值：无
  说    明：根据外部行列数和状态栏信息计算上下状态栏的起始坐标（x, y）。
***************************************************************************/
static void gmw_inner_calculate_status_line_positions(CONSOLE_GRAPHICS_INFO* const pCGI)
{
	// 上状态栏起始x坐标
	pCGI->SLI.top_start_x = pCGI->extern_left_cols;
	// 上状态栏起始y坐标
	pCGI->SLI.top_start_y = pCGI->extern_up_lines;
	// 下状态栏起始x坐标
	pCGI->SLI.lower_start_x = pCGI->extern_left_cols;
	// 下状态栏起始y坐标
	pCGI->SLI.lower_start_y = pCGI->extern_up_lines + pCGI->top_status_line + pCGI->draw_frame_with_col_no + pCGI->CFI.bhigh;
}

/***************************************************************************
  函数名称：
  功    能：计算所有相关参数
  输入参数：CONSOLE_GRAPHICS_INFO* const pCGI：整体结构指针
  返 回 值：无
  说    明：调用各个计算函数，计算框架尺寸、起始位置、屏幕尺寸和状态栏位置等。
***************************************************************************/
static void gmw_inner_calculate_all(CONSOLE_GRAPHICS_INFO* const pCGI)
{
	gmw_inner_calculate_frame_size(pCGI);
	gmw_inner_calculate_start_positions(pCGI);
	gmw_inner_calculate_screen_size(pCGI);
	gmw_inner_calculate_status_line_positions(pCGI);
}

/***************************************************************************
  函数名称：
  功能：处理字符串末尾可能存在的中文字符截断问题
  输入参数：char* s - 输入字符串指针
  返回值：无
  说明：如果字符串的最后一个字符是中文字符的前半部分，则将其截断，
		以避免乱码。
***************************************************************************/
static void gmw_inner_dealwith_chinese_char(char* s)
{
	char* last = s;
	// 遍历找到字符串的末尾
	while (*last != 0) last++;
	last = last - 1; // 指向最后一个字符

	// 如果最后一个字符是ASCII字符，无需处理
	if (*last > 0) return;

	char* ps = s;
	// 检查字符串中的每个字符
	while (ps < last)
	{
		// 如果是ASCII字符，移动到下一个字符
		if (*ps > 0) ps++;
		// 如果是中文字符，跳过两个字节
		else if (*ps < 0) ps += 2;
	}

	// 如果指针已超出最后字符，说明无截断
	if (ps > last) return;

	// 将最后一个字符设置为结束符，截断字符串
	*last = 0;
}


/***************************************************************************
  函数名称：
  功    能：将字符串s2复制到s1中,覆盖s1中原内容,复制时包含\0
  输入参数：
  返 回 值：新的s1
  说    明：
***************************************************************************/
static char* gmw_inner_strcpy(char* s1, const char* s2)
{
	/* 注意：函数内不允许定义任何形式的数组（包括静态数组） */
	if (s1 == NULL)
		return s1;

	char* s = s1;

	if (s2 == NULL)
		*s = '\0';
	else
	{
		for (; *s2 != '\0'; s++, s2++)
			*s = *s2;
		*s = '\0';
	}

	return s1;
}

/***************************************************************************
  函数名称：
  功    能：比较字符串s1和s2的大小,英文字母要区分大小写
  输入参数：
  返 回 值：相等为0,不等则为第1个不相等字符的ASCII差值
  说    明：
***************************************************************************/
static int gmw_inner_strcmp(const char* s1, const char* s2)
{
	/* 注意：函数内不允许定义任何形式的数组（包括静态数组） */
	if (s1 == NULL || s2 == NULL)
	{
		int t = (s1 != NULL) - (s2 != NULL);
		return t;
	}

	while (*s1 && (*s1 == *s2))
	{
		s1++;
		s2++;
	}

	return *s1 - *s2;
}
/***************************************************************************
  函数名称：
  功    能：将字符串s2的前1en个字符复制到s1中,复制时不含\0,若1en比s2的长度大,复制s2长度个字符即可(不含\0)
  输入参数：
  返 回 值：新的s1
  说    明：
***************************************************************************/
static char* gmw_inner_strncpy(char* s1, const char* s2, const int len)
{
	/* 注意：函数内不允许定义任何形式的数组（包括静态数组） */
	if (s1 == NULL || s2 == NULL)
	{
		return s1;
	}

	char* s_1 = s1;
	const char* s_2 = s2 + len;
	if (size_t(len) > strlen(s2) + 1)
	{
		while (*s2 != '\0')
		{
			*s_1 = *s2;
			s_1++;
			s2++;
		}
	}
	else
	{
		while (s2 < s_2)
		{
			*s_1 = *s2;
			s_1++;
			s2++;
		}
	}
	return s1;
}

/***************************************************************************
  函数名称：
  功    能：设置状态栏的显示状态
  输入参数：CONSOLE_GRAPHICS_INFO *const pCGI	：整体结构指针
			const int type						：状态栏类型（上/下）
			const bool on_off					：true - 需要，false - 不需要
  返 回 值：0 - 成功，-1 - 失败
***************************************************************************/
static int gmw_inner_set_status_line(CONSOLE_GRAPHICS_INFO* const pCGI, const int type, const bool on_off)
{
	if (type == TOP_STATUS_LINE)
	{
		pCGI->SLI.is_top_status_line = on_off;
		pCGI->top_status_line = on_off;
	}
	else if (type == LOWER_STATUS_LINE)
	{
		pCGI->SLI.is_lower_status_line = on_off;
		pCGI->lower_status_line = on_off;
	}
	else
		return -1; // 无效的状态栏类型
	return 0; // 成功
}
/***************************************************************************
  函数名称：
  功    能：设置状态栏颜色（正常背景色）
  输入参数：int* color_ptr		：指向要设置的颜色变量
			const int color		：颜色值
			const int default_color：默认颜色值
***************************************************************************/
static void gmw_inner_set_normal_bg_color(int* color_ptr, const int color, const int default_color)
{
	if (color == -1)
		*color_ptr = default_color;
	else
		*color_ptr = color;
}

/***************************************************************************
  函数名称：
  功    能：设置状态栏颜色（正常前景色）
  输入参数：int* color_ptr		：指向要设置的颜色变量
			const int color		：颜色值
			const int default_color：默认颜色值
***************************************************************************/
static void gmw_inner_set_normal_fg_color(int* color_ptr, const int color, const int default_color)
{
	if (color == -1)
		*color_ptr = default_color;
	else
		*color_ptr = color;
}

/***************************************************************************
  函数名称：
  功    能：设置整体颜色和字体
  输入参数：CONSOLE_GRAPHICS_INFO *const pCGI：整体结构指针
		   const int bgcolor				：整个窗口背景色
		   const int fgcolor				：整个窗口前景色
  返 回 值：
  说    明：设置颜色和字体的封装
***************************************************************************/
static void gmw_inner_set_color_and_font(CONSOLE_GRAPHICS_INFO* const pCGI, const int bgcolor, const int fgcolor)
{
	gmw_set_color(pCGI, bgcolor, fgcolor);
	gmw_set_font(pCGI);
	gmw_set_ext_rowcol(pCGI);
}

/***************************************************************************
  函数名称：
  功    能：设置主框架的参数
  输入参数：CONSOLE_GRAPHICS_INFO *const pCGI：整体结构指针
  返 回 值：
  说    明：设置主框架的线型、风格和颜色等
***************************************************************************/
static void gmw_inner_set_frame_parameters(CONSOLE_GRAPHICS_INFO* const pCGI)
{
	gmw_set_frame_default_linetype(pCGI, 1);
	gmw_set_frame_style(pCGI);
	gmw_set_frame_color(pCGI);
	gmw_set_block_default_linetype(pCGI, 1);
	gmw_set_block_border_switch(pCGI);
	gmw_set_delay(pCGI, DELAY_OF_DRAW_FRAME, 0);
	gmw_set_delay(pCGI, DELAY_OF_DRAW_BLOCK, 0);
	gmw_set_delay(pCGI, DELAY_OF_BLOCK_MOVED, BLOCK_MOVED_DELAY_MS);
}

/***************************************************************************
  函数名称：
  功    能：设置状态栏的参数
  输入参数：CONSOLE_GRAPHICS_INFO *const pCGI：整体结构指针
  返 回 值：
  说    明：设置状态栏的显示状态和颜色
***************************************************************************/
static void gmw_inner_set_status_line_parameters(CONSOLE_GRAPHICS_INFO* const pCGI)
{
	gmw_set_status_line_switch(pCGI, TOP_STATUS_LINE, true);
	gmw_set_status_line_switch(pCGI, LOWER_STATUS_LINE, true);
	gmw_set_status_line_color(pCGI, TOP_STATUS_LINE);
	gmw_set_status_line_color(pCGI, LOWER_STATUS_LINE);
}

/***************************************************************************
  函数名称：
  功    能：设置行列号显示
  输入参数：CONSOLE_GRAPHICS_INFO *const pCGI：整体结构指针
  返 回 值：
  说    明：设置行号和列号的显示状态
***************************************************************************/
static void gmw_inner_set_row_col_display(CONSOLE_GRAPHICS_INFO* const pCGI)
{
	gmw_set_rowno_switch(pCGI);
	gmw_set_colno_switch(pCGI);
}

/***************************************************************************
  函数名称：
  功    能：绘制列号
  输入参数：CONSOLE_GRAPHICS_INFO *const pCGI：整体结构指针
  返 回 值：
  说    明：
***************************************************************************/
static void gmw_inner_draw_column_numbers(const CONSOLE_GRAPHICS_INFO* const pCGI)
{
	cct_gotoxy(pCGI->start_x + 1 + pCGI->CFI.block_width / 2, pCGI->start_y - 1);
	for (int i = 0; i < pCGI->col_num; i++)
	{
		if (i < 100)
			cout << setiosflags(ios::left)
			<< setw(2 * pCGI->CFI.separator + pCGI->CFI.block_width) << i
			<< resetiosflags(ios::left);
		else
			cout << setiosflags(ios::left)
			<< setw(2 * pCGI->CFI.separator + pCGI->CFI.block_width) << "**"
			<< resetiosflags(ios::left);
		Sleep(pCGI->delay_of_draw_frame);
	}
}

/***************************************************************************
  函数名称：
  功    能：绘制行号
  输入参数：CONSOLE_GRAPHICS_INFO *const pCGI：整体结构指针
  返 回 值：
  说    明：
***************************************************************************/
static void gmw_inner_draw_row_numbers(const CONSOLE_GRAPHICS_INFO* const pCGI)
{
	for (int i = 0; i < pCGI->row_num; i++)
	{
		cct_gotoxy(pCGI->extern_left_cols, pCGI->start_y + pCGI->CFI.separator +
			pCGI->CFI.block_high / 2 + i * (1 * pCGI->CFI.separator + pCGI->CFI.block_high));
		if (i < 26)
			cout << char(i + 'A') << ' ';
		else if (i < 52)
			cout << char(i - 26 + 'a') << ' ';
		else
			cout << '*' << ' ';
		Sleep(pCGI->delay_of_draw_frame);
	}
}

/***************************************************************************
  函数名称：
  功    能：绘制首行的框架元素
  输入参数：const CONSOLE_GRAPHICS_INFO *const pCGI：整体结构指针
			int j：当前列索引
  返 回 值：无
***************************************************************************/
static void gmw_inner_draw_top_line(const CONSOLE_GRAPHICS_INFO* const pCGI, int j)
{
	if (j == 0)  // 左上角
		cout << pCGI->CFI.top_left << " ";
	else if (j == pCGI->CFI.bwidth / 2 - 1)  // 右上角
		cout << pCGI->CFI.top_right << " ";
	else if (j % (pCGI->CFI.block_width / 2 + 1) == 0) // 上分界
		cout << pCGI->CFI.h_top_separator << " ";
	else  // 水平线
		cout << pCGI->CFI.h_normal << " ";
}

/***************************************************************************
  函数名称：
  功    能：绘制末行的框架元素
  输入参数：const CONSOLE_GRAPHICS_INFO *const pCGI：整体结构指针
			int j：当前列索引
  返 回 值：无
***************************************************************************/
static void gmw_inner_draw_bottom_line(const CONSOLE_GRAPHICS_INFO* const pCGI, int j)
{
	if (j == 0)  // 左下角
		cout << pCGI->CFI.lower_left << " ";
	else if (j == pCGI->CFI.bwidth / 2 - 1)  // 右下角
		cout << pCGI->CFI.lower_right << " ";
	else if (j % (pCGI->CFI.block_width / 2 + 1) == 0) // 下分界
		cout << pCGI->CFI.h_lower_separator << " ";
	else  // 水平线
		cout << pCGI->CFI.h_normal << " ";
}

/***************************************************************************
  函数名称：
  功    能：绘制中间横行的框架元素
  输入参数：const CONSOLE_GRAPHICS_INFO *const pCGI：整体结构指针
			int j：当前列索引
  返 回 值：无
***************************************************************************/
static void gmw_inner_draw_middle_line(const CONSOLE_GRAPHICS_INFO* const pCGI, int j)
{
	if (j == 0)  // 左分界
		cout << pCGI->CFI.v_left_separator << " ";
	else if (j == pCGI->CFI.bwidth / 2 - 1)  // 右分界
		cout << pCGI->CFI.v_right_separator << " ";
	else if (j % (pCGI->CFI.block_width / 2 + 1) == 0) // 中分界
		cout << pCGI->CFI.mid_separator << " ";
	else  // 水平线
		cout << pCGI->CFI.h_normal << " ";
}


/***************************************************************************
  函数名称：
  功    能：绘制带分割线的框架
  输入参数：CONSOLE_GRAPHICS_INFO *const pCGI：指向整体结构的指针
  返 回 值：无
  说    明：根据设定绘制带有分割线的框架，包括行和列的分界。
***************************************************************************/
static void gmw_inner_draw_frame_with_separator(const CONSOLE_GRAPHICS_INFO* const pCGI)
{
	for (int i = 0; i < pCGI->CFI.bhigh; i++)
	{
		cct_gotoxy(pCGI->start_x, pCGI->start_y + i);
		for (int j = 0; j < pCGI->CFI.bwidth / 2; j++)
		{
			if (i == 0)
				gmw_inner_draw_top_line(pCGI, j); // 调用绘制首行的函数
			else if (i == pCGI->CFI.bhigh - 1)
				gmw_inner_draw_bottom_line(pCGI, j); // 调用绘制末行的函数
			else if (i % (pCGI->CFI.block_high + 1) == 0)
				gmw_inner_draw_middle_line(pCGI, j); // 调用绘制中间横行的函数
			else //中间格子
			{
				if (j % (pCGI->CFI.block_width / 2 + 1) == 0)
					cout << pCGI->CFI.v_normal << " ";
				else
					cout << "  ";
			}
			Sleep(pCGI->delay_of_draw_frame);
		}
	}
}

/***************************************************************************
  函数名称：
  功    能：绘制无分割线的框架
  输入参数：CONSOLE_GRAPHICS_INFO *const pCGI：指向整体结构的指针
  返 回 值：无
  说    明：根据设定绘制不带分割线的框架。
***************************************************************************/
static void gmw_inner_draw_frame_without_separator(const CONSOLE_GRAPHICS_INFO* const pCGI)
{
	for (int i = 0; i < pCGI->CFI.bhigh; i++)
	{
		cct_gotoxy(pCGI->start_x, pCGI->start_y + i);
		for (int j = 0; j < pCGI->CFI.bwidth / 2; j++)
		{
			if (i == 0 && j == 0) // 左上角
				cout << pCGI->CFI.top_left << " ";
			else if (i == pCGI->CFI.bhigh - 1 && j == 0) // 左下角
				cout << pCGI->CFI.lower_left << " ";
			else if (i == 0 && j == pCGI->CFI.bwidth / 2 - 1) // 右上角
				cout << pCGI->CFI.top_right << " ";
			else if (i == pCGI->CFI.bhigh - 1 && j == pCGI->CFI.bwidth / 2 - 1) // 右下角
				cout << pCGI->CFI.lower_right << " ";
			else if (i == 0 || i == pCGI->CFI.bhigh - 1) // 水平线
				cout << pCGI->CFI.h_normal << " ";
			else if (j == 0 || j == pCGI->CFI.bwidth / 2 - 1) // 竖直线
				cout << pCGI->CFI.v_normal << " ";
			else
				cout << "  "; // 中间空格
			Sleep(pCGI->delay_of_draw_frame);
		}
	}
}

/***************************************************************************
  函数名称：
  功    能：在状态栏渲染显示信息
  输入参数：const CONSOLE_GRAPHICS_INFO* const pCGI  ：整体结构指针
			const int type                          ：状态栏类型（上/下）
			const char* catchy_line                 ：需要特别标注的消息
			const char* line                        ：正常消息
			int wide_border                          ：输出宽度限制
  返 回 值：无
  说    明：根据不同类型的状态栏设置光标位置和颜色，并输出消息
***************************************************************************/
static void gmw_inner_render_status_line(const CONSOLE_GRAPHICS_INFO* const pCGI, const int type, const char* catchy_line, const char* line, int wide_border)
{
	// 根据状态栏类型设置光标位置和背景色
	if (type == TOP_STATUS_LINE)
	{
		cct_gotoxy(pCGI->SLI.top_start_x, pCGI->SLI.top_start_y);
		cct_setcolor(pCGI->SLI.top_catchy_bgcolor, pCGI->SLI.top_catchy_fgcolor);
	}
	else if (type == LOWER_STATUS_LINE)
	{
		cct_gotoxy(pCGI->SLI.lower_start_x, pCGI->SLI.lower_start_y);
		cct_setcolor(pCGI->SLI.lower_catchy_bgcolor, pCGI->SLI.lower_catchy_fgcolor);
	}

	// 输出需要特别标注的消息
	cout << catchy_line;

	// 根据状态栏类型设置正常消息的背景色
	if (type == TOP_STATUS_LINE)
		cct_setcolor(pCGI->SLI.top_normal_bgcolor, pCGI->SLI.top_normal_fgcolor);
	else if (type == LOWER_STATUS_LINE)
		cct_setcolor(pCGI->SLI.lower_normal_bgcolor, pCGI->SLI.lower_normal_fgcolor);

	// 输出正常消息
	cout << line;

	// 如果正常消息和特别标注的消息长度小于限制宽度，则填充空格
	if (static_cast<size_t>(strlen(line) + strlen(catchy_line)) < static_cast<size_t>(wide_border))
		cout << setw(wide_border - strlen(line) - strlen(catchy_line)) << " ";
}

/***************************************************************************
  函数名称：
  功    能：准备状态栏消息行
  输入参数：const char* msg                        ：正常消息
			const char* catchy_msg                 ：需要特别标注的消息
			int wide_border                        ：输出宽度限制
			char* line                             ：存储正常消息的字符串
			char* catchy_line                      ：存储特别标注消息的字符串
  返 回 值：无
  说    明：处理消息长度，确保输出不会超过宽度限制，并处理中文截断
***************************************************************************/
static void prepare_status_melineage(const char* msg, const char* catchy_msg, int wide_border, char* line, char* catchy_line)
{
	int len;
	if (msg == NULL)
		len = 0; // 如果正常消息为空，长度为0
	else
		len = strlen(msg); // 否则获取正常消息的长度

	int catchy_len;
	if (catchy_msg == NULL)
		catchy_len = 0; // 如果特别标注消息为空，长度为0
	else
		catchy_len = strlen(catchy_msg); // 否则获取特别标注消息的长度

	if (len != 0) // 如果正常消息不为空
	{
		if (catchy_len == 0) // 如果特别标注消息为空
		{
			gmw_inner_strncpy(line, msg, wide_border); // 复制正常消息
			gmw_inner_dealwith_chinese_char(line); // 处理可能的中文截断
		}
		else
		{
			if (catchy_len >= wide_border) // 如果特别标注消息超出限制
			{
				gmw_inner_strncpy(catchy_line, catchy_msg, wide_border); // 只复制特别标注消息
				gmw_inner_dealwith_chinese_char(catchy_line); // 处理可能的中文截断
			}
			else
			{
				int wide_border2 = wide_border - catchy_len; // 计算剩余宽度
				gmw_inner_strcpy(catchy_line, catchy_msg); // 复制特别标注消息
				gmw_inner_strncpy(line, msg, wide_border2); // 复制正常消息
				gmw_inner_dealwith_chinese_char(line); // 处理可能的中文截断
			}
		}
	}
	else  // 如果正常消息为空
	{
		line[0] = '\0'; // 确保正常消息为空串
		catchy_line[0] = '\0'; // 确保特别标注消息为空串
	}
}

/***************************************************************************
  函数名称：
  功    能：将整数转换为字符数组（字符串）。
  输入参数：int num：待转换的整数。
			char* buffer：用于存放转换结果的字符数组。
			size_t buffer_size：字符数组的大小，确保不发生溢出。
  返 回 值：无
  说    明：此函数将整数转换为字符串格式，并处理负数情况。转换后的字符串以 '\0' 结束。
***************************************************************************/
static void gmw_inner_int_to_char_array(int num, char* buffer, int buffer_size)
{
	int len = 0; // 字符串的实际长度
	bool is_negative = false; // 标记是否为负数

	// 检查是否为负数
	if (num < 0)
	{
		is_negative = true; // 设置负数标记
		num = -num; // 将负数转换为正数以便处理
	}

	// 将数字转换为字符数组
	do
	{
		if (len < buffer_size - 1) // 确保有空间放终止符
			buffer[len++] = (num % 10) + '0'; // 取出最低位数字并转换为字符
		num /= 10; // 移除最低位数字
	} while (num > 0); // 直到所有数字都处理完

	// 如果是负数，添加负号
	if (is_negative)
		if (len < buffer_size - 1)
			buffer[len++] = '-'; // 添加负号

	buffer[len] = '\0'; // 添加字符串结束符

	// 反转字符数组，得到正确的数字顺序
	for (int i = 0; i < len / 2; ++i)
	{
		char temp = buffer[i];
		buffer[i] = buffer[len - i - 1]; // 交换字符
		buffer[len - i - 1] = temp; // 交换字符
	}
}


/***************************************************************************
  函数名称：
  功    能：根据提供的值填充块中的字符（数字或内容）。
  输入参数：const CONSOLE_GRAPHICS_INFO* const pCGI：控制台图形信息结构体的指针。
			const BLOCK_DISPLAY_INFO* pBDI：显示信息结构体的指针。
			int start_direction_x：块的起始 x 坐标。
			int start_direction_y：块的起始 y 坐标。
			int bdi_value：需要显示的值
   返 回 值：
   说    明：
***************************************************************************/
static void gmw_inner_fill_character(const CONSOLE_GRAPHICS_INFO* const pCGI, const BLOCK_DISPLAY_INFO* pBDI, int start_direction_x, int start_direction_y, int bdi_value)
{
	int char_start_x, char_start_y;

	// 如果没有内容且需要显示数字
	if (pBDI->content == NULL)
	{
		if (bdi_value != 0) // 假设 BDI_VALUE_BLANK 为 0
		{
			char_start_x = start_direction_x + 2 * pCGI->CBI.block_border;
			char_start_y = start_direction_y + (pCGI->CFI.block_high - 1) / 2;

			// 创建字符数组以存储数字
			char value[12]; // 足够存储整数的字符串
			gmw_inner_int_to_char_array(bdi_value, value, sizeof(value)); // 转换数字为字符串

			// 计算字符串长度
			int value_len = 0;
			while (value[value_len] != '\0')
				value_len++; // 计算字符串长度

			// 计算空格长度以居中显示
			int blank_len = (pCGI->CFI.block_width - 2 * (pCGI->CBI.block_border + 1) - value_len) / 2;

			// 确保空格长度不为负
			if (blank_len < 0)
				blank_len = 0;

			// 移动到填充位置
			cct_gotoxy(char_start_x, char_start_y);
			for (int i = 0; i < blank_len; i++)
				cout << ' '; // 输出空格
			cout << value; // 输出数字
		}
	}
	// 如果有内容，直接输出
	else
	{
		char_start_x = start_direction_x + (pCGI->CFI.block_width - 1) / 2;
		char_start_y = start_direction_y + (pCGI->CFI.block_high - 1) / 2;

		cct_gotoxy(char_start_x, char_start_y); // 移动到填充位置
		cout << pBDI->content; // 输出内容
	}
}


/***************************************************************************
  函数名称：
  功    能：绘制填充色块，包含边框或不包含边框。
  输入参数：const CONSOLE_GRAPHICS_INFO* const pCGI：控制台图形信息结构体的指针。
			int start_direction_x：块的起始 x 坐标。
			int start_direction_y：块的起始 y 坐标。
			bool need_delay：是否需要延迟绘制。
			int bdi_value：需要显示的值。
  返 回 值：无
  说    明：根据是否有边框绘制色块，若有边框则绘制边框和内部填充。
***************************************************************************/
static void gmw_inner_fill_block(const CONSOLE_GRAPHICS_INFO* const pCGI, int start_direction_x, int start_direction_y, bool need_delay, int bdi_value)
{
	// 根据是否有边框进行处理
	bool has_border = pCGI->CBI.block_border && bdi_value != 0;

	// 遍历每一行
	for (int i = 0; i < pCGI->CFI.block_high; i++)
	{
		cct_gotoxy(start_direction_x, start_direction_y + i); // 移动到当前行的起始位置
		// 遍历每一列
		for (int j = 0; j < pCGI->CFI.block_width / 2; j++)
		{
			if (has_border)
			{
				// 首行
				if (i == 0)
				{
					if (j == 0)
						cout << pCGI->CBI.top_left << " "; // 左上角
					else if (j == pCGI->CFI.block_width / 2 - 1)
						cout << pCGI->CBI.top_right << " "; // 右上角
					else
						cout << pCGI->CBI.h_normal << " "; // 中间部分
				}
				// 末行
				else if (i == pCGI->CFI.block_high - 1)
				{
					if (j == 0)
						cout << pCGI->CBI.lower_left << " "; // 左下角
					else if (j == pCGI->CFI.block_width / 2 - 1)
						cout << pCGI->CBI.lower_right << " "; // 右下角
					else
						cout << pCGI->CBI.h_normal << " "; // 中间部分
				}
				// 普通行
				else
				{
					if (j == 0 || j == pCGI->CFI.block_width / 2 - 1)
						cout << pCGI->CBI.v_normal << " "; // 竖边
					else
						cout << "  "; // 空格
				}
			}
			else
				cout << "  "; // 无边框时填充空格
			if (need_delay)
				Sleep(pCGI->delay_of_draw_block); // 延迟
		}
	}
}

/***************************************************************************
  函数名称：
  功    能：在指定坐标绘制色块并填充字符。
  输入参数：const CONSOLE_GRAPHICS_INFO* const pCGI：控制台图形信息结构体的指针。
			const int start_direction_x：块的起始 x 坐标。
			const int start_direction_y：块的起始 y 坐标。
			const int bdi_value：需要显示的值。
			const BLOCK_DISPLAY_INFO* const bdi：存放该值对应的显示信息的结构体数组。
			bool need_delay：是否需要延迟绘制，默认为 true。
  返 回 值：无
  说    明：根据 bdi_value 从 bdi 中获取显示信息，并设置颜色后绘制块和填充字符。
***************************************************************************/
static void gmw_inner_draw_block_direction(const CONSOLE_GRAPHICS_INFO* const pCGI, const int start_direction_x, const int start_direction_y, const int bdi_value, const BLOCK_DISPLAY_INFO* const bdi, bool need_delay = true)
{
	// 设置色块信息
	const BLOCK_DISPLAY_INFO* pBDI = bdi;
	while (pBDI->value != bdi_value && pBDI->value != -1)
		pBDI++;

	// 填充颜色
	int block_bg_color;
	if (pBDI->bgcolor == -1)
		block_bg_color = pCGI->CFI.bgcolor; // 使用默认背景色
	else
		block_bg_color = pBDI->bgcolor; // 使用自定义背景色

	int block_fg_color;
	if (pBDI->fgcolor == -1)
		block_fg_color = pCGI->CFI.fgcolor; // 使用默认前景色
	else
		block_fg_color = pBDI->fgcolor; // 使用自定义前景色

	cct_setcolor(block_bg_color, block_fg_color); // 设置颜色

	gmw_inner_fill_block(pCGI, start_direction_x, start_direction_y, need_delay, bdi_value); // 填充色块
	gmw_inner_fill_character(pCGI, pBDI, start_direction_x, start_direction_y, bdi_value);  // 填充字符
}

/***************************************************************************
  函数名称：
  功    能：在垂直方向上移动指定的色块
  输入参数：
	const CONSOLE_GRAPHICS_INFO *const pCGI	：控制台图形信息结构体指针
	const int start_direction_x					：块的起始横坐标
	const int start_direction_y					：块的起始纵坐标
	const int distance						：移动距离（从1开始，人为保证正确性，程序不检查）
	const int bdi_value						：需要显示的值
	const BLOCK_DISPLAY_INFO *const bdi		：块显示信息的结构体指针
	const int direction						：移动方向，-1表示向上，1表示向下
  返 回 值：无
  说    明：根据给定的方向和距离，更新块的位置并显示移动效果
***************************************************************************/
static void gmw_inner_move_block_vertical(const CONSOLE_GRAPHICS_INFO* pCGI, int start_direction_x, int start_direction_y, int distance, int bdi_value, const BLOCK_DISPLAY_INFO* bdi, int direction)
{
	int end_direction_y = start_direction_y + direction * distance * (pCGI->CFI.block_high + 1 * pCGI->CFI.separator);

	if (direction == -1) // 向上移动
	{
		for (int y = start_direction_y - 1; y >= end_direction_y; y--)
		{
			gmw_inner_draw_block_direction(pCGI, start_direction_x, y, bdi_value, bdi, false);
			cct_gotoxy(start_direction_x, y + pCGI->CFI.block_high); // 留下的空行的位置
			cct_setcolor(pCGI->CFI.bgcolor, pCGI->CFI.fgcolor);
			for (int i = 0; i < pCGI->CFI.block_width / 2; i++) {
				if ((start_direction_y - y) % (pCGI->CFI.block_high + 1 * pCGI->CFI.separator) == 0)
					cout << pCGI->CFI.h_normal << " "; // 画横条分界线
				else
					cout << "  "; // 画空白
			}
			Sleep(pCGI->delay_of_block_moved);
		}
	}
	else if (direction == 1) // 向下移动
	{
		for (int y = start_direction_y + 1; y <= end_direction_y; y++)
		{
			gmw_inner_draw_block_direction(pCGI, start_direction_x, y, bdi_value, bdi, false);
			cct_gotoxy(start_direction_x, y - 1); // 留下的空行的位置
			cct_setcolor(pCGI->CFI.bgcolor, pCGI->CFI.fgcolor);
			for (int i = 0; i < pCGI->CFI.block_width / 2; i++)
			{
				if ((y - start_direction_y) % (pCGI->CFI.block_high + 1 * pCGI->CFI.separator) == 0)
					cout << pCGI->CFI.h_normal << " "; // 画横条分界线
				else
					cout << "  "; // 画空白
			}
			Sleep(pCGI->delay_of_block_moved);
		}
	}
}

/***************************************************************************
  函数名称：
  功    能：在水平方向上移动指定的色块
  输入参数：
	const CONSOLE_GRAPHICS_INFO *const pCGI	：控制台图形信息结构体指针
	const int start_direction_x					：块的起始横坐标
	const int start_direction_y					：块的起始纵坐标
	const int col_no							：列号（从0开始，人为保证正确性，程序不检查）
	const int distance						：移动距离（从1开始，人为保证正确性，程序不检查）
	const int bdi_value						：需要显示的值
	const BLOCK_DISPLAY_INFO *const bdi		：块显示信息的结构体指针
	const int direction						：移动方向，-1表示向左，1表示向右
  返 回 值：无
  说    明：根据给定的方向和距离，更新块的位置并显示移动效果
***************************************************************************/
static void gmw_inner_move_block_horizontal(const CONSOLE_GRAPHICS_INFO* pCGI, int start_direction_x, int start_direction_y, int col_no, int distance, int bdi_value, const BLOCK_DISPLAY_INFO* bdi, int direction)
{
	int end_direction_x = start_direction_x + direction * distance * (pCGI->CFI.block_width + 2 * pCGI->CFI.separator);

	if (direction == -1)  // 向左移动
	{
		for (int x = start_direction_x - 2; x >= end_direction_x; x -= 2)
		{
			gmw_inner_draw_block_direction(pCGI, x, start_direction_y, bdi_value, bdi, false);
			for (int i = 0; i < pCGI->CFI.block_high; i++)
			{
				cct_gotoxy(x + pCGI->CFI.block_width, start_direction_y + i); // 留下的空行的位置
				cct_setcolor(pCGI->CFI.bgcolor, pCGI->CFI.fgcolor);
				if (((start_direction_x - x) / 2) % (pCGI->CFI.block_width / 2 + 1 * pCGI->CFI.separator) == 0)
					cout << pCGI->CFI.v_normal << " "; // 画竖条分界线
				else
					cout << "  "; // 画空白
			}
			Sleep(pCGI->delay_of_block_moved);
		}
	}
	else if (direction == 1)  // 向右移动
	{
		for (int x = start_direction_x + 2; x <= end_direction_x; x += 2)
		{
			gmw_inner_draw_block_direction(pCGI, x, start_direction_y, bdi_value, bdi, false);
			for (int i = 0; i < pCGI->CFI.block_high; i++) {
				cct_gotoxy(x - 2, start_direction_y + i); // 留下的空行的位置
				cct_setcolor(pCGI->CFI.bgcolor, pCGI->CFI.fgcolor);
				if (((x - start_direction_x) / 2) % (pCGI->CFI.block_width / 2 + 1 * pCGI->CFI.separator) == 0)
					cout << pCGI->CFI.v_normal << " "; // 画竖条分界线
				else
					cout << "  "; // 画空白
			}
			Sleep(pCGI->delay_of_block_moved);
		}
	}
}

/***************************************************************************
  函数名称：
  功    能：在垂直方向上移动指定的色块（无边框情况）
  输入参数：
	const CONSOLE_GRAPHICS_INFO *const pCGI	：控制台图形信息结构体指针
	const int start_direction_x					：块的起始横坐标
	const int block_start_direction_y0					：块的初始纵坐标
	const int row_no							：行号（从0开始，人为保证正确性，程序不检查）
	const int distance						：移动距离（从1开始，人为保证正确性，程序不检查）
	const int bdi_value						：需要显示的值
	const BLOCK_DISPLAY_INFO *const bdi		：块显示信息的结构体指针
	const int direction						：移动方向，-1表示向上，1表示向下
  返 回 值：无
  说    明：根据给定的方向和距离，更新块的位置并显示移动效果，且不绘制边框
***************************************************************************/
static void gmw_inner_move_block_vertical_no_border(const CONSOLE_GRAPHICS_INFO* pCGI, int start_direction_x, int block_start_direction_y0, int row_no, int distance, int bdi_value, const BLOCK_DISPLAY_INFO* bdi, int direction)
{
	int end_direction_x = start_direction_x;
	int end_direction_y = block_start_direction_y0 + (row_no + direction * distance) * (pCGI->CFI.block_high + pCGI->CFI.separator);
	int start_direction_y = block_start_direction_y0 + row_no * (pCGI->CFI.block_high + 1 * pCGI->CFI.separator);

	if (direction == -1)  // 向上移动
	{
		for (int y = start_direction_y - 1; y >= end_direction_y; y--)
		{
			gmw_inner_draw_block_direction(pCGI, start_direction_x, y, bdi_value, bdi, false);
			cct_gotoxy(start_direction_x, y + pCGI->CFI.block_high); // 留下的空行的位置
			cct_setcolor(pCGI->CFI.bgcolor, pCGI->CFI.fgcolor);
			for (int i = 0; i < pCGI->CFI.block_width / 2; i++)
				cout << "  "; // 画空白
			Sleep(pCGI->delay_of_block_moved);
		}
	}
	else if (direction == 1)  // 向下移动
	{
		for (int y = start_direction_y + 1; y <= end_direction_y; y++)
		{
			gmw_inner_draw_block_direction(pCGI, start_direction_x, y, bdi_value, bdi, false);
			cct_gotoxy(start_direction_x, y - 1); // 留下的空行的位置
			cct_setcolor(pCGI->CFI.bgcolor, pCGI->CFI.fgcolor);
			for (int i = 0; i < pCGI->CFI.block_width / 2; i++)
				cout << "  "; // 画空白
			Sleep(pCGI->delay_of_block_moved);
		}
	}
}

/***************************************************************************
  函数名称：
  功    能：在水平方向上移动指定的色块（无边框情况）
  输入参数：
	const CONSOLE_GRAPHICS_INFO *const pCGI	：控制台图形信息结构体指针
	const int block_start_direction_x0					：块的初始横坐标
	const int start_direction_x					：块的起始横坐标
	const int start_direction_y					：块的起始纵坐标
	const int col_no							：列号（从0开始，人为保证正确性，程序不检查）
	const int distance						：移动距离（从1开始，人为保证正确性，程序不检查）
	const int bdi_value						：需要显示的值
	const BLOCK_DISPLAY_INFO *const bdi		：块显示信息的结构体指针
	const int direction						：移动方向，-1表示向左，1表示向右
  返 回 值：无
  说    明：根据给定的方向和距离，更新块的位置并显示移动效果，且不绘制边框
***************************************************************************/
static void gmw_inner_move_block_horizontal_no_border(const CONSOLE_GRAPHICS_INFO* pCGI, int block_start_direction_x0, int start_direction_x, int start_direction_y, int col_no, int distance, int bdi_value, const BLOCK_DISPLAY_INFO* bdi, int direction)
{
	int end_direction_x = block_start_direction_x0 + (col_no + direction * distance) * (pCGI->CFI.block_width + 2 * pCGI->CFI.separator);
	int end_direction_y = start_direction_y;

	if (direction == -1) // 向左移动
	{
		for (int x = start_direction_x - 2; x >= end_direction_x; x -= 2)
		{
			gmw_inner_draw_block_direction(pCGI, x, start_direction_y, bdi_value, bdi, false);
			for (int i = 0; i < pCGI->CFI.block_high; i++)
			{
				cct_gotoxy(x + pCGI->CFI.block_width, start_direction_y + i); // 留下的空行的位置
				cct_setcolor(pCGI->CFI.bgcolor, pCGI->CFI.fgcolor);
				cout << "  "; // 画空白
			}
			Sleep(pCGI->delay_of_block_moved);
		}
	}
	else if (direction == 1)  // 向右移动
	{
		for (int x = start_direction_x + 2; x <= end_direction_x; x += 2)
		{
			gmw_inner_draw_block_direction(pCGI, x, start_direction_y, bdi_value, bdi, false);
			for (int i = 0; i < pCGI->CFI.block_high; i++)
			{
				cct_gotoxy(x - 2, start_direction_y + i); // 留下的空行的位置
				cct_setcolor(pCGI->CFI.bgcolor, pCGI->CFI.fgcolor);
				cout << "  "; // 画空白
			}
			Sleep(pCGI->delay_of_block_moved);
		}
	}
}

/***************************************************************************
  函数名称：gmw_inner_get_mouse_position
  功能：根据鼠标坐标确定其在游戏区域的合法位置
  输入参数：
	const CONSOLE_GRAPHICS_INFO* const pCGI	：整体结构指针，包含游戏区域的位置信息和块的配置
	int X										：鼠标的当前X坐标
	int Y										：鼠标的当前Y坐标
	int& MRow									：输出参数，用于返回鼠标所处行号（从0开始）
	int& MCol									：输出参数，用于返回鼠标所处列号（从0开始）
  返回值：
	bool：如果鼠标坐标在合法区域内返回true，否则返回false
***************************************************************************/
static bool gmw_inner_get_mouse_position(const CONSOLE_GRAPHICS_INFO* const pCGI, int X, int Y, int& MRow, int& MCol)
{
	int block_start_direction_x0 = pCGI->start_x + 2;
	int block_start_direction_y0 = pCGI->start_y + 1;
	int start_direction_x, start_direction_y;
	MRow = MCol = -1;

	for (int i = 0; i < pCGI->row_num; i++)
	{
		for (int j = 0; j < pCGI->col_num; j++)
		{
			start_direction_y = block_start_direction_y0 + i * (pCGI->CFI.block_high + 1 * pCGI->CFI.separator);
			start_direction_x = block_start_direction_x0 + j * (pCGI->CFI.block_width + 2 * pCGI->CFI.separator);
			if (start_direction_x <= X && X < start_direction_x + pCGI->CFI.block_width && start_direction_y <= Y && Y < start_direction_y + pCGI->CFI.block_high)
			{
				MRow = i;
				MCol = j;
				return true; // 位置合法
			}
		}
	}
	return false; // 位置非法
}

/***************************************************************************
  函数名称：gmw_inner_handle_mouse_event
  功能：处理鼠标事件，更新行列号并显示状态信息
  输入参数：
	const CONSOLE_GRAPHICS_INFO* const pCGI	：整体结构指针，包含游戏区域的位置信息和块的配置
	int X										：鼠标的当前X坐标
	int Y										：鼠标的当前Y坐标
	int& MRow									：输出参数，用于返回鼠标所处行号（从0开始）
	int& MCol									：输出参数，用于返回鼠标所处列号（从0开始）
	int& MAction								：输入参数，表示鼠标事件的类型
	int& MRow_last								：输入参数，前一次鼠标位置的行号
	int& MCol_last								：输入参数，前一次鼠标位置的列号
	const bool update_lower_status_line		：布尔值，指示是否在状态行中更新信息
  返回值：
	bool：如果事件处理有效返回true，否则返回false
***************************************************************************/
static bool gmw_inner_handle_mouse_event(const CONSOLE_GRAPHICS_INFO* const pCGI, int X, int Y, int& MRow, int& MCol, int& MAction, int& MRow_last, int& MCol_last, const bool update_lower_status_line)
{
	if (MAction == MOUSE_ONLY_MOVED)
	{
		if (gmw_inner_get_mouse_position(pCGI, X, Y, MRow, MCol))
		{
			if (!(MRow_last == MRow && MCol_last == MCol) && update_lower_status_line)
			{
				char display[30] = { 0 };
				sprintf(display, "[当前光标] %c行%d列", MRow + 'A', MCol);
				gmw_status_line(pCGI, LOWER_STATUS_LINE, display);
			}
			return true; // 有效的鼠标移动
		}
		else
			if (update_lower_status_line)
				gmw_status_line(pCGI, LOWER_STATUS_LINE, "[当前光标] 位置非法");
	}
	else if (MAction == MOUSE_LEFT_BUTTON_CLICK || MAction == MOUSE_RIGHT_BUTTON_CLICK)
	{
		if (gmw_inner_get_mouse_position(pCGI, X, Y, MRow, MCol))
			return true; // 合法点击
		else
			if (update_lower_status_line)
				gmw_status_line(pCGI, LOWER_STATUS_LINE, "[当前光标] 位置非法");
	}

	return false; // 无效事件
}


/* -----------------------------------------------
		实现下面给出的函数（函数声明不准动）
   ----------------------------------------------- */
   /***************************************************************************
	 函数名称：
	 功    能：设置游戏主框架的行列数
	 输入参数：CONSOLE_GRAPHICS_INFO *const pCGI	：整体结构指针
			   const int row						：行数(错误则为0，不设上限，人为保证正确性)
			   const int col						：列数(错误则为0，不设上限，人为保证正确性)
	 返 回 值：
	 说    明：1、指消除类游戏的矩形区域的行列值
			   2、行列的变化会导致CONSOLE_GRAPHICS_INFO结构体中其它成员值的变化，要处理
   ***************************************************************************/
int gmw_set_rowcol(CONSOLE_GRAPHICS_INFO* const pCGI, const int row, const int col)
{
	/* 防止在未调用 gmw_init 前调用其它函数 */
	if (pCGI->inited != CGI_INITED)
		return -1;

	if (row < 0 || col < 0)
	{
		if (row < 0) pCGI->row_num = 0;
		if (col < 0) pCGI->col_num = 0;
		return 0; // 无需进一步处理
	}

	pCGI->row_num = row;
	pCGI->col_num = col;
	gmw_inner_calculate_all(pCGI);
	return 0; // 成功设置行列数
}

/***************************************************************************
  函数名称：
  功    能：设置整个窗口（含游戏区、附加区在内的整个cmd窗口）的颜色
  输入参数：CONSOLE_GRAPHICS_INFO *const pCGI	：整体结构指针
		   const int bg_color					：前景色（缺省COLOR_BLACK）
		   const int fg_color					：背景色（缺省COLOR_WHITE）
		   const bool cascade					：是否级联（缺省为true-级联）
  返 回 值：
  说    明：1、cascade = true时
				同步修改游戏主区域的颜色
				同步修改上下状态栏的正常文本的背景色和前景色，醒目文本的背景色（前景色不变）
			2、不检查颜色值错误及冲突，需要人为保证
				例：颜色非0-15
					前景色背景色的值一致导致无法看到内容
					前景色正好是状态栏醒目前景色，导致无法看到醒目提示
					...
***************************************************************************/
int gmw_set_color(CONSOLE_GRAPHICS_INFO* const pCGI, const int bgcolor, const int fgcolor, const bool cascade)
{
	/* 防止在未调用 gmw_init 前调用其它函数 */
	if (pCGI->inited != CGI_INITED)
		return -1;

	// 设置区域颜色
	pCGI->area_bgcolor = bgcolor;
	pCGI->area_fgcolor = fgcolor;

	if (cascade)
	{
		// 修改框架
		pCGI->CFI.bgcolor = bgcolor;
		pCGI->CFI.fgcolor = fgcolor;

		// 修改上状态栏
		pCGI->SLI.top_normal_bgcolor = bgcolor;
		pCGI->SLI.top_normal_fgcolor = fgcolor;
		pCGI->SLI.top_catchy_bgcolor = bgcolor;

		// 修改下状态栏
		pCGI->SLI.lower_normal_bgcolor = bgcolor;
		pCGI->SLI.lower_normal_fgcolor = fgcolor;
		pCGI->SLI.lower_catchy_bgcolor = bgcolor;
	}

	return 0; // 成功设置颜色
}

/***************************************************************************
  函数名称：
  功    能：设置窗口的字体
  输入参数：CONSOLE_GRAPHICS_INFO *const pCGI	：整体结构指针
		   const char *fontname					：字体名称（只能是"Terminal"和"新宋体"两种，错误则返回-1，不改变字体）
		   const int fs_high					：字体高度（缺省及错误为16，不设其它限制，人为保证）
		   const int fs_width					：字体高度（缺省及错误为8，不设其它限制，人为保证）
  返 回 值：
  说    明：1、与cmd_console_tools中的setfontsize相似，目前只支持“点阵字体”和“新宋体”
			2、若设置其它字体则直接返回，保持原字体设置不变
***************************************************************************/
int gmw_set_font(CONSOLE_GRAPHICS_INFO* const pCGI, const char* fontname, const int fs_high, const int fs_width)
{
	/* 防止在未调用 gmw_init 前调用其它函数 */
	if (pCGI->inited != CGI_INITED)
		return -1;

	// 检查字体名称
	if (gmw_inner_strcmp(fontname, "新宋体") != 0 && gmw_inner_strcmp(fontname, "Terminal") != 0)
		return -1; // 字体不支持

	// 设置字体类型
	gmw_inner_strcpy(pCGI->CFT.font_type, fontname);

	// 设置字体大小
	if (fs_high <= 0)
		pCGI->CFT.font_size_high = 16; // 默认值
	else
		pCGI->CFT.font_size_high = fs_high;

	if (fs_width <= 0)
		pCGI->CFT.font_size_width = 8; // 默认值
	else
		pCGI->CFT.font_size_width = fs_width;

	return 0; // 成功设置字体
}

/***************************************************************************
  函数名称：
  功    能：设置延时
  输入参数：CONSOLE_GRAPHICS_INFO *const pCGI	：整体结构指针
		   const int type						：延时的类型（目前为3种）
		   const int delay_ms					：以ms为单位的延时
			   画边框的延时：0 ~ 不设上限，人为保证正确（<0则置0）
			   画色块的延时：0 ~ 不设上限，人为保证正确（<0则置0）
			   色块移动的延时：BLOCK_MOVED_DELAY_MS ~ 不设上限，人为保证正确（ <BLOCK_MOVED_DELAY_MS 则置 BLOCK_MOVED_DELAY_MS）
  返 回 值：
  说    明：
***************************************************************************/
int gmw_set_delay(CONSOLE_GRAPHICS_INFO* const pCGI, const int type, const int delay_ms)
{
	/* 防止在未调用 gmw_init 前调用其它函数 */
	if (pCGI->inited != CGI_INITED)
		return -1;

	// 检查延时类型的有效性
	if (type < DELAY_OF_DRAW_FRAME || type > DELAY_OF_BLOCK_MOVED)
		return -1; // 类型无效

	// 设置延时
	if (type == DELAY_OF_DRAW_FRAME)
	{
		if (delay_ms < 0)
			pCGI->delay_of_draw_frame = 0;
		else
			pCGI->delay_of_draw_frame = delay_ms;
	}
	else if (type == DELAY_OF_DRAW_BLOCK)
	{
		if (delay_ms < 0)
			pCGI->delay_of_draw_block = 0;
		else
			pCGI->delay_of_draw_block = delay_ms;
	}
	else if (type == DELAY_OF_BLOCK_MOVED)
	{
		if (delay_ms < BLOCK_MOVED_DELAY_MS)
			pCGI->delay_of_block_moved = BLOCK_MOVED_DELAY_MS;
		else
			pCGI->delay_of_block_moved = delay_ms;
	}

	return 0; // 成功设置延时
}

/***************************************************************************
  函数名称：
  输入参数：设置游戏主框架结构之外需要保留的额外区域
  功    能：CONSOLE_GRAPHICS_INFO *const pCGI	：
		   const int up_lines					：上部额外的行（缺省及错误为0，不设上限，人为保证）
		   const int down_lines				：下部额外的行（缺省及错误为0，不设上限，人为保证）
		   const int left_cols					：左边额外的列（缺省及错误为0，不设上限，人为保证）
		   const int right_cols				：右边额外的列（缺省及错误为0，不设上限，人为保证）
  返 回 值：
  说    明：额外行列的变化会导致CONSOLE_GRAPHICS_INFO结构体中其它成员值的变化，要处理
***************************************************************************/
int gmw_set_ext_rowcol(CONSOLE_GRAPHICS_INFO* const pCGI, const int up_lines, const int down_lines, const int left_cols, const int right_cols)
{
	/* 防止在未调用 gmw_init 前调用其它函数 */
	if (pCGI->inited != CGI_INITED)
		return -1;

	// 设置额外行列，避免使用条件表达式
	if (up_lines < 0)
		pCGI->extern_up_lines = 0;
	else
		pCGI->extern_up_lines = up_lines;

	if (down_lines < 0)
		pCGI->extern_down_lines = 0;
	else
		pCGI->extern_down_lines = down_lines;

	if (left_cols < 0)
		pCGI->extern_left_cols = 0;
	else
		pCGI->extern_left_cols = left_cols;

	if (right_cols < 0)
		pCGI->extern_right_cols = 0;
	else
		pCGI->extern_right_cols = right_cols;


	gmw_inner_calculate_all(pCGI);
	return 0; // 成功设置额外行列
}

/***************************************************************************
  函数名称：
  功    能：填充 CONSOLE_FRAME_TYPE 结构中的11种线型（缺省4种）
  输入参数：CONSOLE_GRAPHICS_INFO *const pCGI	：整体结构指针
			const int type						：1 - 全线 2 - 全单线 3 - 横双竖单 4 - 横单竖双
  返 回 值：
  说    明：
***************************************************************************/
int gmw_set_frame_default_linetype(CONSOLE_GRAPHICS_INFO* const pCGI, const int type)
{
	/* 防止在未调用 gmw_init 前调用其它函数 */
	if (pCGI == NULL || pCGI->inited != CGI_INITED) return -1;

	const char* lineChars[5][11] = {
		{ NULL },
		{ "╔", "╚", "╗", "╝", "═", "║", "╦", "╩", "╠", "╣", "╬" },
		{ "┌", "└", "┐", "┘", "─", "│", "┬", "┴", "├", "┤", "┼" },
		{ "╒", "╘", "╕", "╛", "═", "│", "╤", "╧", "╞", "╡", "╪" },
		{ "╓", "╙", "╖", "╜", "─", "║", "╥", "╨", "╟", "╢", "╫" }
	};

	if (type < 1 || type > 4) return -1;

	for (int i = 0; i < 11; i++)
		gmw_inner_strcpy(((char*)&pCGI->CFI) + (i * sizeof(pCGI->CFI.top_left)), lineChars[type][i]);

	return 0;
}

/***************************************************************************
  函数名称：
  功    能：填充 CONSOLE_FRAME_TYPE 结构中的11种线型
  输入参数：CONSOLE_GRAPHICS_INFO *const pCGI	：整体结构指针
			const char *...						：共11种，具体见.h，此处略
  返 回 值：
  说    明：约定为一个中文制表符，可以使用其它内容，人为保证2字节
			1、超过2字节则只取前2字节
			2、如果给NULL，用两个空格替代
			3、如果给1字节，则补一个空格，如果因此而导致显示乱，不算错
***************************************************************************/
int gmw_set_frame_linetype(CONSOLE_GRAPHICS_INFO* const pCGI, const char* top_left, const char* lower_left, const char* top_right,
	const char* lower_right, const char* h_normal, const char* v_normal, const char* h_top_separator,
	const char* h_lower_separator, const char* v_left_separator, const char* v_right_separator, const char* mid_separator)
{
	/* 防止在未调用 gmw_init 前调用其它函数 */
	if (pCGI == NULL || pCGI->inited != CGI_INITED) return -1;

	const char* lineChars[11] = { top_left, lower_left, top_right, lower_right, h_normal,
								  v_normal, h_top_separator, h_lower_separator,
								  v_left_separator, v_right_separator, mid_separator };

	for (int i = 0; i < 11; i++)
		gmw_inner_strcpy(((char*)&pCGI->CFI) + (i * sizeof(pCGI->CFI.top_left)), lineChars[i]);

	return 0; // 成功
}

/***************************************************************************
  函数名称：
  功    能：填充 CONSOLE_FRAME_TYPE 结构中的色块数量大小、是否需要分隔线等
  输入参数：输入参数：CONSOLE_GRAPHICS_INFO *const pCGI	：整体结构指针
			const int block_width						：宽度（错误及缺省2，因为约定表格线为中文制表符，如果给出奇数，要+1）
			const int block_high						：高度（错误及缺省1）
			const bool separator						：是否需要分隔线（缺省为true，需要分隔线）
  返 回 值：
  说    明：框架大小/是否需要分隔线等的变化会导致CONSOLE_GRAPHICS_INFO结构体中其它成员值的变化，要处理
***************************************************************************/
int gmw_set_frame_style(CONSOLE_GRAPHICS_INFO* const pCGI, const int block_width, const int block_high, const bool separator)
{
	/* 防止在未调用 gmw_init 前调用其它函数 */
	if (pCGI->inited != CGI_INITED)
		return -1;

	// 设置块宽度
	if (block_width < 0)
		pCGI->CFI.block_width = 2;
	else
	{
		if (block_width % 2 == 1)
			pCGI->CFI.block_width = block_width + 1;
		else
			pCGI->CFI.block_width = block_width;
	}

	// 设置块高度
	if (block_high < 0)
		pCGI->CFI.block_high = 1;
	else
		pCGI->CFI.block_high = block_high;

	// 设置分隔符
	pCGI->CFI.separator = separator;
	gmw_inner_calculate_all(pCGI); // 计算内部参数
	return 0; // 返回成功
}

/***************************************************************************
  函数名称：
  功    能：填充 CONSOLE_BORDER_TYPE 结构中的颜色
  输入参数：CONSOLE_GRAPHICS_INFO *const pCGI	：整体结构指针
			const int bg_color					：背景色（缺省 -1表示用窗口背景色）
			const int fg_color					：前景色（缺省 -1表示用窗口前景色）
  返 回 值：
  说    明：不检查颜色值错误及冲突，需要人为保证
				例：颜色非0-15，前景色背景色的值一致导致无法看到内容等
***************************************************************************/
int gmw_set_frame_color(CONSOLE_GRAPHICS_INFO* const pCGI, const int bgcolor, const int fgcolor)
{
	/* 防止在未调用 gmw_init 前调用其它函数 */
	if (pCGI->inited != CGI_INITED)
		return -1;

	// 设置背景色
	if (bgcolor == -1)
		pCGI->CFI.bgcolor = pCGI->area_bgcolor; // 使用窗口背景色
	else
		pCGI->CFI.bgcolor = bgcolor; // 使用提供的背景色

	// 设置前景色
	if (fgcolor == -1)
		pCGI->CFI.fgcolor = pCGI->area_fgcolor; // 使用窗口前景色
	else
		pCGI->CFI.fgcolor = fgcolor; // 使用提供的前景色

	return 0; // 返回成功
}

/***************************************************************************
  函数名称：
  功    能：填充 CONSOLE_BLOCK_INFO 结构中的6种线型（缺省4种）
  输入参数：CONSOLE_GRAPHICS_INFO *const pCGI	：整体结构指针
			const int type						：1 - 全双线 2 - 全单线 3 - 横双竖单 4 - 横单竖双
  返 回 值：
  说    明：
***************************************************************************/
int gmw_set_block_default_linetype(CONSOLE_GRAPHICS_INFO* const pCGI, const int type)
{
	/* 防止在未调用 gmw_init 前调用其它函数 */
	if (pCGI->inited != CGI_INITED)
		return -1;

	// 定义线型字符
	const char* lineChars[5][11] = {
		{ NULL },
		{ "╔", "╚", "╗", "╝", "═", "║", "╦", "╩", "╠", "╣", "╬" },
		{ "┌", "└", "┐", "┘", "─", "│", "┬", "┴", "├", "┤", "┼" },
		{ "╒", "╘", "╕", "╛", "═", "│", "╤", "╧", "╞", "╡", "╪" },
		{ "╓", "╙", "╖", "╜", "─", "║", "╥", "╨", "╟", "╢", "╫" }
	};

	// 检查类型有效性
	if (type < 1 || type > 4)
		return -1;

	// 填充线型字符
	for (int i = 0; i < 11; i++) {
		gmw_inner_strcpy(((char*)&pCGI->CBI) + (i * sizeof(pCGI->CBI.top_left)), lineChars[type][i]);
	}

	return 0; // 返回成功
}

/***************************************************************************
  函数名称：
  功    能：填充 CONSOLE_BLOCK_INFO 结构中的6种线型
  输入参数：CONSOLE_GRAPHICS_INFO *const pCGI	：整体结构指针
		   const char *...					：共6种，具体见.h，此处略
  返 回 值：
  说    明：约定为一个中文制表符，可以使用其它内容，人为保证2字节
			1、超过2字节则只取前2字节
			2、如果给NULL，用两个空格替代
			3、如果给1字节，则补一个空格，如果因此而导致显示乱，不算错
***************************************************************************/
int gmw_set_block_linetype(CONSOLE_GRAPHICS_INFO* const pCGI, const char* top_left, const char* lower_left, const char* top_right, const char* lower_right, const char* h_normal, const char* v_normal)
{
	/* 防止在未调用 gmw_init 前调用其它函数 */
	if (pCGI->inited != CGI_INITED)
		return -1;

	const char* lineChars[6] = {
		top_left, lower_left, top_right, lower_right, h_normal, v_normal
	};

	char restore[CFI_LEN] = { 0 }; // 存储临时字符

	for (int i = 0; i < 6; i++)
	{
		const char* src = lineChars[i];
		if (src == NULL)
			gmw_inner_strcpy(((char*)&pCGI->CBI) + (i * sizeof(pCGI->CBI.top_left)), "  "); // NULL时返回两个空格
		else if (strlen(src) == 2)
			gmw_inner_strcpy(((char*)&pCGI->CBI) + (i * sizeof(pCGI->CBI.top_left)), src); // 正常返回2字节字符
		else if (strlen(src) == 1)
		{
			restore[0] = src[0];
			restore[1] = ' ';
			restore[2] = '\0';
			gmw_inner_strcpy(((char*)&pCGI->CBI) + (i * sizeof(pCGI->CBI.top_left)), restore); // 1字节字符补空格
		}
		else
		{
			gmw_inner_strncpy(restore, src, 2);
			restore[2] = '\0';
			gmw_inner_strcpy(((char*)&pCGI->CBI) + (i * sizeof(pCGI->CBI.top_left)), restore); // 超过2字节，截取前2字节
		}
	}

	return 0; // 返回成功
}

/***************************************************************************
  函数名称：
  功    能：设置每个游戏色块(彩球)是否需要小边框
  输入参数：CONSOLE_GRAPHICS_INFO *const pCGI	：整体结构指针
		   const bool on_off					：true - 需要 flase - 不需要（缺省false）
  返 回 值：
  说    明：边框约定为中文制表符，双线
***************************************************************************/
int gmw_set_block_border_switch(CONSOLE_GRAPHICS_INFO* const pCGI, const bool on_off)
{
	/* 防止在未调用 gmw_init 前调用其它函数 */
	if (pCGI->inited != CGI_INITED)
		return -1;
	pCGI->CBI.block_border = on_off;
	return 0; //此句可根据需要修改
}

/***************************************************************************
  函数名称：
  功    能：设置是否显示上下状态栏
  输入参数：CONSOLE_GRAPHICS_INFO *const pCGI	：整体结构指针
			const int type						：状态栏类型（上/下）
			const bool on_off					：true - 需要 flase - 不需要（缺省true）
  返 回 值：
  说    明：1、状态栏的相关约定如下：
			   1.1、上状态栏只能一行，在主区域最上方框线/列标的上面，为主区域的最开始一行（主区域的左上角坐标就是上状态栏的坐标）
			   1.2、下状态栏只能一行，在主区域最下方框线的下面
			   1.3、状态栏的宽度为主区域宽度，如果信息过长则截断
		   2、行列的变化会导致CONSOLE_GRAPHICS_INFO结构体中其它成员值的变化，要处理
***************************************************************************/
int gmw_set_status_line_switch(CONSOLE_GRAPHICS_INFO* const pCGI, const int type, const bool on_off)
{
	/* 防止在未调用 gmw_init 前调用其它函数 */
	if (pCGI->inited != CGI_INITED)
		return -1; // 检查初始化状态

	gmw_inner_set_status_line(pCGI, type, on_off); // 调用封装函数设置状态栏
	gmw_inner_calculate_all(pCGI); // 更新相关参数
	return 0; // 返回成功
}

/***************************************************************************
  函数名称：
  功    能：设置上下状态栏的颜色
  输入参数：CONSOLE_GRAPHICS_INFO *const pCGI	：整体结构指针
			const int type						：状态栏类型（上/下）
			const int normal_bgcolor			：正常文本背景色（缺省 -1表示使用窗口背景色）
			const int normal_fgcolor			：正常文本前景色（缺省 -1表示使用窗口前景色）
			const int catchy_bgcolor			：醒目文本背景色（缺省 -1表示使用窗口背景色）
			const int catchy_fgcolor			：醒目文本前景色（缺省 -1表示使用亮黄色）
  输入参数：
  返 回 值：
  说    明：不检查颜色值错误及冲突，需要人为保证
				例：颜色非0-15，前景色背景色的值一致导致无法看到内容等
***************************************************************************/
int gmw_set_status_line_color(CONSOLE_GRAPHICS_INFO* const pCGI, const int type, const int normal_bgcolor, const int normal_fgcolor, const int catchy_bgcolor, const int catchy_fgcolor)
{
	/* 防止在未调用 gmw_init 前调用其它函数 */
	if (pCGI->inited != CGI_INITED)
		return -1;
	int* normal_bg;
	int* normal_fg;
	int* catchy_bg;
	int* catchy_fg;

	if (type == TOP_STATUS_LINE)
	{
		normal_bg = &pCGI->SLI.top_normal_bgcolor;
		normal_fg = &pCGI->SLI.top_normal_fgcolor;
		catchy_bg = &pCGI->SLI.top_catchy_bgcolor;
		catchy_fg = &pCGI->SLI.top_catchy_fgcolor;
	}
	else
	{
		normal_bg = &pCGI->SLI.lower_normal_bgcolor;
		normal_fg = &pCGI->SLI.lower_normal_fgcolor;
		catchy_bg = &pCGI->SLI.lower_catchy_bgcolor;
		catchy_fg = &pCGI->SLI.lower_catchy_fgcolor;
	}
	// 设置颜色
	gmw_inner_set_normal_bg_color(normal_bg, normal_bgcolor, pCGI->area_bgcolor);
	gmw_inner_set_normal_fg_color(normal_fg, normal_fgcolor, pCGI->area_fgcolor);
	gmw_inner_set_normal_bg_color(catchy_bg, catchy_bgcolor, pCGI->area_bgcolor);
	gmw_inner_set_normal_fg_color(catchy_fg, catchy_fgcolor, COLOR_HYELLOW);
	return 0; //此句可根据需要修改
}

/***************************************************************************
  函数名称：
  功    能：设置是否显示行号
  输入参数：CONSOLE_GRAPHICS_INFO *const pCGI	：整体结构指针
			const bool on_off					：true - 显示 flase - 不显示（缺省false）
  返 回 值：
  说    明：1、行号约定为字母A开始连续排列（如果超过26，则从a开始，超过52的统一为*，实际应用不可能）
			2、是否显示行号的变化会导致CONSOLE_GRAPHICS_INFO结构体中其它成员值的变化，要处理
***************************************************************************/
int gmw_set_rowno_switch(CONSOLE_GRAPHICS_INFO* const pCGI, const bool on_off)
{
	/* 防止在未调用 gmw_init 前调用其它函数 */
	if (pCGI->inited != CGI_INITED)
		return -1;
	pCGI->draw_frame_with_row_no = on_off;
	gmw_inner_calculate_all(pCGI);
	return 0; //此句可根据需要修改
}

/***************************************************************************
  函数名称：
  功    能：设置是否显示列标
  输入参数：CONSOLE_GRAPHICS_INFO *const pCGI	：整体结构指针
			const bool on_off					：true - 显示 flase - 不显示（缺省false）
  返 回 值：
  说    明：1、列标约定为数字0开始连续排列（数字0-99，超过99统一为**，实际应用不可能）
			2、是否显示列标的变化会导致CONSOLE_GRAPHICS_INFO结构体中其它成员值的变化，要处理
***************************************************************************/
int gmw_set_colno_switch(CONSOLE_GRAPHICS_INFO* const pCGI, const bool on_off)
{
	/* 防止在未调用 gmw_init 前调用其它函数 */
	if (pCGI->inited != CGI_INITED)
		return -1;
	pCGI->draw_frame_with_col_no = on_off;
	gmw_inner_calculate_all(pCGI);
	return 0; //此句可根据需要修改
}

/***************************************************************************
  函数名称：
  功    能：打印 CONSOLE_GRAPHICS_INFO 结构体中的各成员值
  输入参数：
  返 回 值：
  说    明：1、仅供调试用，打印格式自定义
			2、本函数测试用例中未调用过，可以不实现
***************************************************************************/
int gmw_print(const CONSOLE_GRAPHICS_INFO* const pCGI)
{
	/* 防止在未调用 gmw_init 前调用其它函数 */
	if (pCGI->inited != CGI_INITED)
		return -1;
	// 打印结构体成员
	cout << "CONSOLE_GRAPHICS_INFO:" << endl;
	cout << "  初始化标记: " << pCGI->inited << endl;
	cout << "  区域背景色: " << pCGI->area_bgcolor << endl;
	cout << "  区域前景色: " << pCGI->area_fgcolor << endl;
	cout << "  上状态栏: " << (pCGI->SLI.is_top_status_line ? "启用" : "禁用") << endl;
	cout << "  下状态栏: " << (pCGI->SLI.is_lower_status_line ? "启用" : "禁用") << endl;
	cout << "  行数: " << pCGI->row_num << endl;
	cout << "  列数: " << pCGI->col_num << endl;
	cout << "  起始坐标 (X, Y): (" << pCGI->start_x << ", " << pCGI->start_y << ")" << endl;
	cout << "  窗口行数: " << pCGI->lines << ", 窗口列数: " << pCGI->cols << endl;

	// 可以根据需要添加更多打印内容

	return 0; // 成功
}

/***************************************************************************
  函数名称：
  功    能：将 CONSOLE_GRAPHICS_INFO 结构体用缺省值进行初始化
  输入参数：CONSOLE_GRAPHICS_INFO *const pCGI：整体结构指针
		   const int row					：游戏区域色块行数（缺省10）
		   const int col					：游戏区域色块列数（缺省10）
		   const int bgcolor				：整个窗口背景色（缺省 COLOR_BLACK）
		   const int fgcolor				：整个窗口背景色（缺省 COLOR_WHITE）
  返 回 值：
  说    明：窗口背景黑/前景白，点阵16*8，上下左右无额外行列，上下状态栏均有，无行号/列标，框架线型为双线，色块宽度2/高度1/无小边框，颜色略
***************************************************************************/
int gmw_init(CONSOLE_GRAPHICS_INFO* const pCGI, const int row, const int col, const int bgcolor, const int fgcolor)
{
	/* 首先置标记 */
	pCGI->inited = CGI_INITED;
	/*整体参数设置*/
	gmw_set_rowcol(pCGI, row, col);
	gmw_inner_set_color_and_font(pCGI, bgcolor, fgcolor);
	gmw_inner_set_frame_parameters(pCGI);
	gmw_inner_set_status_line_parameters(pCGI);
	gmw_inner_set_row_col_display(pCGI);
	gmw_inner_calculate_all(pCGI);
	/*填充计算参数*/
	gmw_inner_calculate_all(pCGI);
	return 0;  // 成功
}

/***************************************************************************
  函数名称：
  功    能：画主游戏框架
  输入参数：const CONSOLE_GRAPHICS_INFO *const pCGI	：整体结构指针
  返 回 值：
  说    明：具体可参考demo的效果
***************************************************************************/
int gmw_draw_frame(const CONSOLE_GRAPHICS_INFO* const pCGI)
{
	/* 防止在未调用 gmw_init 前调用其它函数 */
	if (pCGI->inited != CGI_INITED)
		return -1;
	cct_setcolor(pCGI->area_bgcolor, pCGI->area_fgcolor);
	cct_setfontsize(pCGI->CFT.font_type, pCGI->CFT.font_size_high, 0);
	cct_cls();

	cct_setconsoleborder(pCGI->cols, pCGI->lines);
	cct_setcolor(pCGI->area_bgcolor, pCGI->area_fgcolor);
	// 绘制列号
	if (pCGI->draw_frame_with_col_no)
		gmw_inner_draw_column_numbers(pCGI);

	// 绘制行号
	if (pCGI->draw_frame_with_row_no)
		gmw_inner_draw_row_numbers(pCGI);

	//主框架
	cct_setcolor(pCGI->CFI.bgcolor, pCGI->CFI.fgcolor);

	if (pCGI->CFI.separator) //分有无分割线两种情况绘制
		gmw_inner_draw_frame_with_separator(pCGI);
	else
		gmw_inner_draw_frame_without_separator(pCGI);
	return 0; //此句可根据需要修改
}

/***************************************************************************
  函数名称：
  功    能：在状态栏上显示信息
  输入参数：const CONSOLE_GRAPHICS_INFO *const pCGI	：整体结构指针
		   const int type							：指定是上/下状态栏
		   const char *msg						：正常信息
		   const char *catchy_msg					：需要特别标注的信息（在正常信息前显示）
  返 回 值：
  说    明：1、输出宽度限定为主框架的宽度（含行号列标位置），超出则截去
			2、如果最后一个字符是某汉字的前半个，会导致后面乱码，要处理
***************************************************************************/
int gmw_status_line(const CONSOLE_GRAPHICS_INFO* const pCGI, const int type, const char* msg, const char* catchy_msg)
{
	/* 防止在未调用 gmw_init 前调用其它函数 */
	if (pCGI->inited != CGI_INITED)
		return -1;

	if (type == TOP_STATUS_LINE && !pCGI->SLI.is_top_status_line)
		return 0;
	if (type == LOWER_STATUS_LINE && !pCGI->SLI.is_lower_status_line)
		return 0;

	cct_setfontsize(pCGI->CFT.font_type, pCGI->CFT.font_size_high, 0);
	int wide_border = 2 * pCGI->draw_frame_with_row_no + pCGI->CFI.bwidth; // 宽度限制
	char* line = new char[wide_border + 1]();
	char* catchy_line = new char[wide_border + 1]();
	if (line == NULL || catchy_line == NULL) return -1;

	prepare_status_melineage(msg, catchy_msg, wide_border, line, catchy_line);
	gmw_inner_render_status_line(pCGI, type, catchy_line, line, wide_border);

	delete[] line;
	delete[] catchy_line;
	return 0; // 可根据需要修改
}

/***************************************************************************
  函数名称：
  功    能：显示某一个色块(内容为字符串，坐标为row/col)
  输入参数：const CONSOLE_GRAPHICS_INFO *const pCGI	：整体结构指针
		   const int row_no						：行号（从0开始，人为保证正确性，程序不检查）
		   const int col_no						：列号（从0开始，人为保证正确性，程序不检查）
		   const int bdi_value						：需要显示的值
		   const BLOCK_DISPLAY_INFO *const bdi		：存放该值对应的显示信息的结构体数组
  返 回 值：
  说    明：1、BLOCK_DISPLAY_INFO 的含义见头文件，用法参考测试样例
			2、bdi_value为 BDI_VALUE_BLANK 表示空白块，要特殊处理
***************************************************************************/
int gmw_draw_block(const CONSOLE_GRAPHICS_INFO* const pCGI, const int row_no, const int col_no, const int bdi_value, const BLOCK_DISPLAY_INFO* const bdi)
{
	/* 防止在未调用 gmw_init 前调用其它函数 */
	if (pCGI->inited != CGI_INITED)
		return -1;
	//位置
	int block_start_direction_x0 = pCGI->start_x + 2;
	int block_start_direction_y0 = pCGI->start_y + 1;
	int start_direction_x = block_start_direction_x0 + col_no * (pCGI->CFI.block_width + 2 * pCGI->CFI.separator);
	int start_direction_y = block_start_direction_y0 + row_no * (pCGI->CFI.block_high + 1 * pCGI->CFI.separator);
	gmw_inner_draw_block_direction(pCGI, start_direction_x, start_direction_y, bdi_value, bdi);
	return 0; //此句可根据需要修改
}

/***************************************************************************
  函数名称：
  功    能：移动某一个色块
  输入参数：const CONSOLE_GRAPHICS_INFO *const pCGI	：整体结构指针
		   const int row_no						：行号（从0开始，人为保证正确性，程序不检查）
		   const int col_no						：列号（从0开始，人为保证正确性，程序不检查）
		   const int bdi_value						：需要显示的值
		   const int blank_bdi_value				：移动过程中用于动画效果显示时用于表示空白的值（一般为0，此处做为参数代入，是考虑到可能出现的特殊情况）
		   const BLOCK_DISPLAY_INFO *const bdi		：存放显示值/空白值对应的显示信息的结构体数组
		   const int direction						：移动方向，一共四种，具体见cmd_gmw_tools.h
		   const int distance						：移动距离（从1开始，人为保证正确性，程序不检查）
  返 回 值：
  说    明：
***************************************************************************/
int gmw_move_block(const CONSOLE_GRAPHICS_INFO* const pCGI, const int row_no, const int col_no, const int bdi_value, const int blank_bdi_value, const BLOCK_DISPLAY_INFO* const bdi, const int direction, const int distance)
{
	/* 防止在未调用 gmw_init 前调用其它函数 */
	if (pCGI->inited != CGI_INITED)
		return -1;
	//位置
	int block_start_direction_x0 = pCGI->start_x + 2;
	int block_start_direction_y0 = pCGI->start_y + 1;//有无分界线都是一样
	int start_direction_x = block_start_direction_x0 + col_no * (pCGI->CFI.block_width + 2 * pCGI->CFI.separator);//给定行列(row_no,col_no)位置的色块起始坐标
	int start_direction_y = block_start_direction_y0 + row_no * (pCGI->CFI.block_high + 1 * pCGI->CFI.separator);
	//有分割线
	if (pCGI->CFI.separator)
	{
		switch (direction)
		{

			case DOWN_TO_UP:
				gmw_inner_move_block_vertical(pCGI, start_direction_x, start_direction_y, distance, bdi_value, bdi, -1);
				break;

			case UP_TO_DOWN:
				gmw_inner_move_block_vertical(pCGI, start_direction_x, start_direction_y, distance, bdi_value, bdi, 1);
				break;

			case RIGHT_TO_LEFT:
				gmw_inner_move_block_horizontal(pCGI, start_direction_x, start_direction_y, col_no, distance, bdi_value, bdi, -1);
				break;

			case LEFT_TO_RIGHT:
				gmw_inner_move_block_horizontal(pCGI, start_direction_x, start_direction_y, col_no, distance, bdi_value, bdi, 1);
				break;
		}
	}

	//无分割线
	else
	{
		switch (direction)
		{
			case DOWN_TO_UP:
				gmw_inner_move_block_vertical_no_border(pCGI, start_direction_x, block_start_direction_y0, row_no, distance, bdi_value, bdi, -1);
				break;

			case UP_TO_DOWN:
				gmw_inner_move_block_vertical_no_border(pCGI, start_direction_x, block_start_direction_y0, row_no, distance, bdi_value, bdi, 1);
				break;

			case RIGHT_TO_LEFT:
				gmw_inner_move_block_horizontal_no_border(pCGI, block_start_direction_x0, start_direction_x, start_direction_y, col_no, distance, bdi_value, bdi, -1);
				break;

			case LEFT_TO_RIGHT:
				gmw_inner_move_block_horizontal_no_border(pCGI, block_start_direction_x0, start_direction_x, start_direction_y, col_no, distance, bdi_value, bdi, 1);
				break;
		}

	}
	return 0; //此句可根据需要修改
}

/***************************************************************************
  函数名称：
  功    能：读键盘或鼠标
  输入参数：const CONSOLE_GRAPHICS_INFO *const pCGI	：整体结构指针
		   int &MAction							：如果返回 CCT_MOUSE_EVENT，则此值有效，为 MOUSE_ONLY_MOVED/MOUSE_LEFT_BUTTON_CLICK/MOUSE_RIGHT_BUTTON_CLICK 三者之一
													   如果返回 CCT_KEYBOARD_EVENT，则此值无效
		   int &MRow								：如果返回 CCT_MOUSE_EVENT 且 MAction = MOUSE_ONLY_MOVED/MOUSE_LEFT_BUTTON_CLICK，则此值有效，表示左键选择的游戏区域的行号（从0开始）
												   其余情况此值无效（如果访问无效值导致错误，不是本函数的错!!!）
		   int &MCol								：如果返回 CCT_MOUSE_EVENT 且 MAction = MOUSE_ONLY_MOVED/MOUSE_LEFT_BUTTON_CLICK，则此值有效，表示左键选择的游戏区域的列号（从0开始）
												   其余情况此值无效（如果访问无效值导致错误，不是本函数的错!!!）
		   int &KeyCode1							：如果返回 CCT_KEYBOARD_EVENT，则此值有效，为读到的键码（如果双键码，则为第一个）
												   其余情况无效（如果访问无效值导致错误，不是本函数的错!!!）
		   int &KeyCode2							：如果返回 CCT_KEYBOARD_EVENT，则此值有效，为读到的键码（如果双键码，则为第二个，如果是单键码，则为0）
												   其余情况无效（如果访问无效值导致错误，不是本函数的错!!!）
		   const bool update_lower_status_line		：鼠标移动时，是否要在本函数中显示"[当前光标] *行*列/位置非法"的信息（true=显示，false=不显示，缺省为true）
  返 回 值：函数返回约定
		   1、如果是鼠标移动，得到的MRow/MCol与传入的相同(鼠标指针微小的移动)，则不返回，继续读
							  得到行列非法位置，则不返回，根据 update_lower_status_line 的设置在下状态栏显示"[当前光标] 位置非法"
							  得到的MRow/MCol与传入的不同(行列至少一个变化)，根据 update_lower_status_line 的设置在下状态栏显示"[当前光标] *行*列"，再返回MOUSE_ONLY_MOVED（有些游戏返回后要处理色块的不同颜色显示）
		   2、如果是按下鼠标左键，且当前鼠标指针停留在主游戏区域的*行*列上，则返回 CCT_MOUSE_EVENT ，MAction 为 MOUSE_LEFT_BUTTON_CLICK, MRow 为行号，MCol 为列标
								  且当前鼠标指针停留在非法区域（非游戏区域，游戏区域中的分隔线），则不返回，根据 update_lower_status_line 的设置在下状态栏显示"[当前光标] 位置非法"
		   3、如果是按下鼠标右键，则不判断鼠标指针停留区域是否合法，直接返回 CCT_MOUSE_EVENT ，MAction 为 MOUSE_LEFT_BUTTON_CLICK, MRow、MCol不可信
		   4、如果按下键盘上的某键（含双键码按键），则直接返回 CCT_KEYBOARD_EVENT，KeyCode1/KeyCode2中为对应的键码值
 说    明：通过调用 cmd_console_tools.cpp 中的 read_keyboard_and_mouse 函数实现
***************************************************************************/
int gmw_read_keyboard_and_mouse(const CONSOLE_GRAPHICS_INFO* const pCGI, int& MAction, int& MRow, int& MCol, int& KeyCode1, int& KeyCode2, const bool update_lower_status_line)
{
	/* 防止在未调用 gmw_init 前调用其它函数 */
	if (pCGI->inited != CGI_INITED)
		return -1;

	int X, Y, MRow_last, MCol_last;
	int ret;
	bool loop = true;
	while (loop) // 或者根据实际需要设置条件退出
	{
		MRow_last = MRow;
		MCol_last = MCol;
		cct_enable_mouse();
		ret = cct_read_keyboard_and_mouse(X, Y, MAction, KeyCode1, KeyCode2);

		if (ret == CCT_MOUSE_EVENT)
		{
			if (gmw_inner_handle_mouse_event(pCGI, X, Y, MRow, MCol, MAction, MRow_last, MCol_last, update_lower_status_line))
				return CCT_MOUSE_EVENT; // 有效的鼠标事件
		}
		else if (ret == CCT_KEYBOARD_EVENT)
				return CCT_KEYBOARD_EVENT; // 返回键盘事件
		// 可以考虑添加超时机制或特定条件退出循环
	}

	return 0; // 或者适当的默认返回值
}