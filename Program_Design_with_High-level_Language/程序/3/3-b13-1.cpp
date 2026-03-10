/* 2352018 信06 刘彦 */
#include <iostream>
#include <iomanip>
using namespace std;

int main()
{
	int n, y, x, x0;   //年、月、星期

	while (1) {
		cout << "请输入年份(2000-2030)和月份(1-12) : ";
		cin >> n >> y;

		if (cin.good()) {
			if ((n >= 2000 && n <= 2030) && (y >= 1 && y <= 12)) {
				break;
			}
			else {
				cout << "输入非法，请重新输入" << endl;
			}
		}
		else {
			cin.clear();
			while (getchar() != '\n');
			cout << "输入非法，请重新输入" << endl;
		}

	}
	while (1) {
		cout << "请输入" << n << "年" << y << "月1日的星期(0-6表示星期日-星期六) : ";
		cin >> x;

		if (cin.good()) {
			if (x >= 0 && x <= 6) {
				break;
			}
			else {
				cout << "输入非法，请重新输入" << endl;
			}
		}
		else {
			cin.clear();
			while (getchar() != '\n');
			cout << "输入非法，请重新输入" << endl;
		}

	}
	cout << endl;
	cout << n << "年" << y << "月的月历为:" << endl;

	int i;
	for (i = 0; i < 7; i++) {
		switch (i)
		{
			case(0):
				cout << "星期日  ";
				break;
			case(1):
				cout << "星期一  ";
				break;
			case(2):
				cout << "星期二  ";
				break;
			case(3):
				cout << "星期三  ";
				break;
			case(4):
				cout << "星期四  ";
				break;
			case(5):
				cout << "星期五  ";
				break;
			case(6):
				cout << "星期六";
				break;
		}
	}
	cout << endl;
	cout << setiosflags(ios::right);
	x0 = x;

	if ((n % 4 != 0) || (n % 100 == 0) && (n % 400 != 0))
	{
		if (y == 1 || y == 3 || y == 5 || y == 7 || y == 8 || y == 10 || y == 12) 
		{
			for (i = 1; i <= 31; i++)
			{
				if (i == 1) {
					cout << setw((2 * x + 1) * 4) << i;
				}
				else if (x0 == 0) {
					cout << setw(4) << i;
				}
				else {
					cout << setw(8) << i;
				}

				x0++;

				if (x0 == 7) {
					cout << "    " << endl;
					x0 = 0;
				}
				else if (i == 31) {
					cout << "    ";
				}
			}
			cout << endl;
		}
		else if (y == 2) {
			for (i = 1; i <= 28; i++)
			{
				if (i == 1) {
					cout << setw((2 * x + 1) * 4) << i;
				}
				else if (x0 == 0) {
					cout << setw(4) << i;
				}
				else {
					cout << setw(8) << i;
				}

				x0++;

				if (x0 == 7) {
					cout << "    " << endl;
					x0 = 0;
				}
				else if (i == 28) {
					cout << "    ";
				}
			}
			cout << endl;
		}
		else {
			for (i = 1; i <= 30; i++)
			{
				if (i == 1) {
					cout << setw((2 * x + 1) * 4) << i;
				}
				else if (x0 == 0) {
					cout << setw(4) << i;
				}
				else {
					cout << setw(8) << i;
				}

				x0++;

				if (x0 == 7) {
					cout << "    " << endl;
					x0 = 0;
				}
				else if (i == 30) {
					cout << "    ";
				}
			}
			cout << endl;
		}
	}
	else
	{
		if (y == 1 || y == 3 || y == 5 || y == 7 || y == 8 || y == 10 || y == 12) {
			for (i = 1; i < 32; i++)
			{
				if (i == 1) {
					cout << setw((2 * x + 1) * 4) << i;
				}
				else if (x0 == 0) {
					cout << setw(4) << i;
				}
				else {
					cout << setw(8) << i;
				}

				x0++;

				if (x0 == 7) {
					cout << "    " << endl;
					x0 = 0;
				}
				else if (i == 31) {
					cout << "    ";
				}
			}
			cout << endl;
		}
		else if (y == 2) {
			for (i = 1; i < 30; i++)
			{
				if (i == 1) {
					cout << setw((2 * x + 1) * 4) << i;
				}
				else if (x0 == 0) {
					cout << setw(4) << i;
				}
				else {
					cout << setw(8) << i;
				}

				x0++;

				if (x0 == 7) {
					cout << "    " << endl;
					x0 = 0;
				}
				else if (i == 29) {
					cout << "    ";
				}
			}
			cout << endl;
		}
		else {
			for (i = 1; i < 31; i++)
			{
				if (i == 1) {
					cout << setw((2 * x + 1) * 4) << i;
				}
				else if (x0 == 0) {
					cout << setw(4) << i;
				}
				else {
					cout << setw(8) << i;
				}

				x0++;

				if (x0 == 7) {
					cout << "    " << endl;
					x0 = 0;
				}
				else if (i == 30) {
					cout << "    ";
				}
			}
			cout << endl;
		}
	}

	return 0;
}