/* 2352018 信06 刘彦 */
#include <iostream>
using namespace std;

int max(int a, int b)
{
	return a > b ? a : b;
}

int max(int a, int b, int c)
{
	int t;
	t = a > b ? a : b;
	return t > c ? t : c;
}

int max(int a, int b, int c, int d)
{
	int t1, t2;
	t1 = a > b ? a : b;
	t2 = c > d ? c : d;
	return t1 > t2 ? t1 : t2;
}

int main()
{
	int num, m;
	int a, b, c, d;
	while (1)
	{
		cout << "请输入个数num及num个正整数：" << endl;
		cin >> num;

		switch (num)
		{
			case 2:
				cin >> a >> b;
				if (!cin.good() || a <= 0 || b <= 0)
				{
					cin.clear();
					cin.ignore(65536, '\n');
					continue;
				}

				m = max(a, b);
				cout << "max=" << m << endl;
				break;
			case 3:
				cin >> a >> b >> c;
				if (!cin.good() || a <= 0 || b <= 0)
				{
					cin.clear();
					cin.ignore(65536, '\n');
					continue;
				}

				m = max(a, b, c);
				cout << "max=" << m << endl;
				break;
			case 4:
				cin >> a >> b >> c >> d;
				if (!cin.good() || a <= 0 || b <= 0 || c <= 0 || d <= 0)
				{
					cin.clear();
					cin.ignore(65536, '\n');
					continue;
				}

				m = max(a, b, c, d);
				cout << "max=" << m << endl;
				break;
			default:
				if (!cin.good())
				{
					cin.clear();
					cin.ignore(65536, '\n');
					continue;
				}
				else
				{
					cout << "个数输入错误" << endl;
					break;
				}
		}
		break;
	}
	return 0;
}