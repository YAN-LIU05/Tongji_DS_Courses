/* 2352018 信06 刘彦 */
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>

int zeller(int y, int m, int d)
{
	int y0, m0, c, w;
	if (m <= 2)
	{
		m0 = m + 12;
		c = (y - 1) / 100;
		y0 = y - c * 100 - 1;
	}
	else
	{
		m0 = m;
		c = y / 100;
		y0 = y - c * 100;
	}
	w = y0 + (y0 / 4) + (c / 4) - 2 * c + (13 * (m0 + 1) / 5) + d - 1;
	while (w < 0)
	{
		w += 7;
	}
	if (w % 7 != 0)
	{
		w = w % 7;
	}
	else
	{
		w = 0;
	}
	return w;
}

int main()
{
	int year, month, day, ret;
	while (1)
	{
		printf("请输入年[1900-2100]、月、日：\n");
		ret = scanf("%d %d %d", &year, &month, &day);

		if (ret == 3)
		{
			if ((year % 4 != 0) || (year % 100 == 0) && (year % 400 != 0))
			{
				if (year >= 1900 && year <= 2100)
				{
					if (month >= 1 && month <= 12)
					{
						if (month == 1 || month == 3 || month == 5 || month == 7 || month == 8 || month == 10 || month == 12)
						{
							if (day >= 1 && day <= 31)
								break;
							else
							{
								while (getchar() != '\n');
								printf("日不正确，请重新输入\n");
							}
						}
						else if (month == 2)
						{
							if (day >= 1 && day <= 28)
								break;
							else
							{
								while (getchar() != '\n');
								printf("日不正确，请重新输入\n");
							}
						}
						else
						{
							if (day >= 1 && day <= 30)
								break;
							else
							{
								while (getchar() != '\n');
								printf("日不正确，请重新输入\n");
							}
						}
					}
					else
					{
						while (getchar() != '\n');
						printf("月份不正确，请重新输入\n");
					}
				}
				else
				{
					while (getchar() != '\n');
					printf("年份不正确，请重新输入\n");
				}
			}
			else
			{
				if (year >= 1900 && year <= 2100)
				{
					if (month >= 1 && month <= 12)
					{
						if (month == 1 || month == 3 || month == 5 || month == 7 || month == 8 || month == 10 || month == 12)
						{
							if (day >= 1 && day <= 31)
								break;
							else
							{
								while (getchar() != '\n');
								printf("日不正确，请重新输入\n");
							}
						}
						else if (month == 2)
						{
							if (day >= 1 && day <= 29)
								break;
							else
							{
								while (getchar() != '\n');
								printf("日不正确，请重新输入\n");
							}
						}
						else
						{
							if (day >= 1 && day <= 30)
								break;
							else
							{
								while (getchar() != '\n');
								printf("日不正确，请重新输入\n");
							}
						}
					}
					else
					{
						while (getchar() != '\n');
						printf("月份不正确，请重新输入\n");
					}
				}
				else
				{
					while (getchar() != '\n');
					printf("年份不正确，请重新输入\n");
				}
			}
		}
		else
		{
			while (getchar() != '\n');
			printf("输入错误，请重新输入\n");
		}
	}

	int x;
	x = zeller(year, month, day);
	switch (x) {
		case 1:
			printf("星期一\n");
			break;
		case 2:
			printf("星期二\n");
			break;
		case 3:
			printf("星期三\n");
			break;
		case 4:
			printf("星期四\n");
			break;
		case 5:
			printf("星期五\n");
			break;
		case 6:
			printf("星期六\n");
			break;
		case 0:
			printf("星期日\n");
			break;
	}

	return 0;
}