/* 2352018 信06 刘彦 */
#include <iostream>
#include <iomanip>
#include <limits>
using namespace std;

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

void calender(int year, int month)
{
	int x, x0, i;
	int width;

	cout << year << "年" << month << "月" << endl;
	/* 头部分隔线，不算打表 */
	cout << "======================================================" << endl;
	cout << "星期日  星期一  星期二  星期三  星期四  星期五  星期六" << endl;
	cout << "======================================================" << endl;

	x = zeller(year, month, 1);
	x0 = x;
	width = (1 + 2 * x) * 4;
	if ((year % 4 != 0) || (year % 100 == 0) && (year % 400 != 0))
	{
		if (month == 1 || month == 3 || month == 5 || month == 7 || month == 8 || month == 10 || month == 12)
		{
			for (i = 1; i <= 31; i++)
			{
				if (i == 1)
				{
					cout << setw(width) << i;
				}
				else if (x0 != 0)
				{
					cout << setw(8) << i;
				}
				else
				{
					cout << setw(4) << i;
				}
				x0++;
				if (x0 == 7)
				{
					if (i == 31)
					{
						cout << "    ";
					}
					else
					{
						cout << "    " << endl;
						x0 = 0;
					}
				}
				if (x0 != 7 && i == 31)
				{
					cout << "    ";
				}
			}
			cout << endl;
		}
		else if (month == 2)
		{
			for (i = 1; i <= 28; i++)
			{
				if (i == 1) {
					cout << setw(width) << i;
				}
				else if (x0 == 0) {
					cout << setw(4) << i;
				}
				else {
					cout << setw(8) << i;
				}
				x0++;
				if (x0 == 7)
				{
					if (i == 28)
					{
						cout << "    ";
					}
					else
					{
						cout << "    " << endl;
						x0 = 0;
					}
				}
				if (x0 != 7 && i == 28)
				{
					cout << "    ";
				}
			}
			cout << endl;
		}
		else
		{
			for (i = 1; i <= 30; i++)
			{
				if (i == 1)
				{
					cout << setw(width) << i;
				}
				else if (x0 == 0)
				{
					cout << setw(4) << i;
				}
				else {
					cout << setw(8) << i;
				}
				x0++;
				if (x0 == 7)
				{
					if (i == 30)
					{
						cout << "    ";
					}
					else
					{
						cout << "    " << endl;
						x0 = 0;
					}
				}
				if (x0 != 7 && i == 30)
				{
					cout << "    ";
				}
			}
			cout << endl;
		}
	}
	else
	{
		if (month == 1 || month == 3 || month == 5 || month == 7 || month == 8 || month == 10 || month == 12)
		{
			for (i = 1; i <= 31; i++)
			{
				if (i == 1)
				{
					cout << setw(width) << i;
				}
				else if (x0 != 0)
				{
					cout << setw(8) << i;
				}
				else
				{
					cout << setw(4) << i;
				}
				x0++;
				if (x0 == 7)
				{
					if (i == 31)
					{
						cout << "    ";
					}
					else
					{
						cout << "    " << endl;
						x0 = 0;
					}
				}
				if (x0 != 7 && i == 31)
				{
					cout << "    ";
				}
			}
			cout << endl;
		}
		else if (month == 2)
		{
			for (i = 1; i <= 29; i++)
			{
				if (i == 1) {
					cout << setw(width) << i;
				}
				else if (x0 == 0) {
					cout << setw(4) << i;
				}
				else {
					cout << setw(8) << i;
				}
				x0++;
				if (x0 == 7)
				{
					if (i == 29)
					{
						cout << "    ";
					}
					else
					{
						cout << "    " << endl;
						x0 = 0;
					}
				}
				if (x0 != 7 && i == 29)
				{
					cout << "    ";
				}
			}
			cout << endl;
		}
		else
		{
			for (i = 1; i <= 30; i++)
			{
				if (i == 1)
				{
					cout << setw(width) << i;
				}
				else if (x0 == 0)
				{
					cout << setw(4) << i;
				}
				else {
					cout << setw(8) << i;
				}
				x0++;
				if (x0 == 7)
				{
					if (i == 30)
					{
						cout << "    ";
					}
					else
					{
						cout << "    " << endl;
						x0 = 0;
					}
				}
				if (x0 != 7 && i == 30)
				{
					cout << "    ";
				}
			}
			cout << endl;
		}
	}

	/* 尾部分隔线，不算打表 */
	cout << "======================================================" << endl;
}

int main()
{
	int nian, yue;
	while (1)
	{
		cout << "请输入年[1900-2100]、月" << endl;
		cin >> nian >> yue;

		if (cin.good())
		{
			if ((nian % 4 != 0) || (nian % 100 == 0) && (nian % 400 != 0))
			{
				if (nian >= 1900 && nian <= 2100)
				{
					if (yue >= 1 && yue <= 12)
						break;
					else
					{
						cin.clear();
						cin.ignore(INT_MAX, '\n');
						cout << "月份不正确，请重新输入" << endl;
						continue;
					}
				}
				else
				{
					cin.clear();
					cin.ignore(INT_MAX, '\n');
					cout << "年份不正确，请重新输入" << endl;
					continue;
				}
			}
			else
			{
				if (nian >= 1900 && nian <= 2100)
				{
					if (yue >= 1 && yue <= 12)
						break;
					else
					{
						cin.clear();
						cin.ignore(INT_MAX, '\n');
						cout << "月份不正确，请重新输入" << endl;
						continue;
					}
				}
				else
				{
					cin.clear();
					cin.ignore(INT_MAX, '\n');
					cout << "年份不正确，请重新输入" << endl;
					continue;
				}
			}
		}
		else
		{
			cin.clear();
			cin.ignore(INT_MAX, '\n');
			cout << "输入错误，请重新输入" << endl;
		}

	}
	cout << endl;

	calender(nian, yue);

	return 0;
}