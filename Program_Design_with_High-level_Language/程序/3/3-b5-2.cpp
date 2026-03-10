/* 2352018 信06 刘彦 */
#include <iostream>
#include <cmath>
using namespace std;

int main()
{
	int a, b, c, x;
	cout << "请输入年，月，日" << endl;
	cin >> a >> b >> c;
	x = 0;

	if ((a % 4 != 0) || (a % 400 != 0) && (a % 100 == 0)) {
		switch (b) {
			case 1:
				if (c <= 31) {
					x = c;
					cout << a << "-" << b << "-" << c << "是" << a << "年的第" << x << "天" << endl;
				}
				else {
					cout << "输入错误-日与月的关系非法" << endl;
				}
				break;
			case 2:
				if (c <= 28) {
					x = 31 + c;
					cout << a << "-" << b << "-" << c << "是" << a << "年的第" << x << "天" << endl;
				}
				else {
					cout << "输入错误-日与月的关系非法" << endl;
				}
				break;
			case 3:
				if (c <= 31) {
					x = 31 + 28 + c;
					cout << a << "-" << b << "-" << c << "是" << a << "年的第" << x << "天" << endl;
				}
				else {
					cout << "输入错误-日与月的关系非法" << endl;
				}
				break;
			case 4:
				if (c <= 30) {
					x = 31 + 28 + 31 + c;
					cout << a << "-" << b << "-" << c << "是" << a << "年的第" << x << "天" << endl;
				}
				else {
					cout << "输入错误-日与月的关系非法" << endl;
				}
				break;
			case 5:
				if (c <= 31) {
					x = 31 + 28 + 31 + 30 + c;
					cout << a << "-" << b << "-" << c << "是" << a << "年的第" << x << "天" << endl;
				}
				else {
					cout << "输入错误-日与月的关系非法" << endl;
				}
				break;
			case 6:
				if (c <= 30) {
					x = 31 + 28 + 31 + 30 + 31 + c;
					cout << a << "-" << b << "-" << c << "是" << a << "年的第" << x << "天" << endl;
				}
				else {
					cout << "输入错误-日与月的关系非法" << endl;
				}
				break;
			case 7:
				if (c <= 31) {
					x = 31 + 28 + 31 + 30 + 31 + 30 + c;
					cout << a << "-" << b << "-" << c << "是" << a << "年的第" << x << "天" << endl;
				}
				else {
					cout << "输入错误-日与月的关系非法" << endl;
				}
				break;
			case 8:
				if (c <= 31) {
					x = 31 + 28 + 31 + 30 + 31 + 30 + 31 + c;
					cout << a << "-" << b << "-" << c << "是" << a << "年的第" << x << "天" << endl;
				}
				else {
					cout << "输入错误-日与月的关系非法" << endl;
				}
				break;
			case 9:
				if (c <= 30) {
					x = 31 + 28 + 31 + 30 + 31 + 30 + 31 + 31 + c;
					cout << a << "-" << b << "-" << c << "是" << a << "年的第" << x << "天" << endl;
				}
				else {
					cout << "输入错误-日与月的关系非法" << endl;
				}
				break;
			case 10:
				if (c <= 31) {
					x = 31 + 28 + 31 + 30 + 31 + 30 + 31 + 31 + 30 + c;
					cout << a << "-" << b << "-" << c << "是" << a << "年的第" << x << "天" << endl;
				}
				else {
					cout << "输入错误-日与月的关系非法" << endl;
				}
				break;
			case 11:
				if (c <= 30) {
					x = 31 + 28 + 31 + 30 + 31 + 30 + 31 + 31 + 30 + 31 + c;
					cout << a << "-" << b << "-" << c << "是" << a << "年的第" << x << "天" << endl;
				}
				else {
					cout << "输入错误-日与月的关系非法" << endl;
				}
				break;
			case 12:
				if (c <= 31) {
					x = 31 + 28 + 31 + 30 + 31 + 30 + 31 + 31 + 30 + 31 + 30 + c;
					cout << a << "-" << b << "-" << c << "是" << a << "年的第" << x << "天" << endl;
				}
				else {
					cout << "输入错误-日与月的关系非法" << endl;
				}
				break;
			default:
				cout << "输入错误-月份不正确" << endl;
				break;
		}
	}
	else {
		switch (b) {
			case 1:
				if (c <= 31) {
					x = c;
					cout << a << "-" << b << "-" << c << "是" << a << "年的第" << x << "天" << endl;
				}
				else {
					cout << "输入错误-日与月的关系非法" << endl;
				}
				break;
			case 2:
				if (c <= 29) {
					x = 31 + c;
					cout << a << "-" << b << "-" << c << "是" << a << "年的第" << x << "天" << endl;
				}
				else {
					cout << "输入错误-日与月的关系非法" << endl;
				}
				break;
			case 3:
				if (c <= 31) {
					x = 31 + 29 + c;
					cout << a << "-" << b << "-" << c << "是" << a << "年的第" << x << "天" << endl;
				}
				else {
					cout << "输入错误-日与月的关系非法" << endl;
				}
				break;
			case 4:
				if (c <= 30) {
					x = 31 + 29 + 31 + c;
					cout << a << "-" << b << "-" << c << "是" << a << "年的第" << x << "天" << endl;
				}
				else {
					cout << "输入错误-日与月的关系非法" << endl;
				}
				break;
			case 5:
				if (c <= 31) {
					x = 31 + 29 + 31 + 30 + c;
					cout << a << "-" << b << "-" << c << "是" << a << "年的第" << x << "天" << endl;
				}
				else {
					cout << "输入错误-日与月的关系非法" << endl;
				}
				break;
			case 6:
				if (c <= 30) {
					x = 31 + 29 + 31 + 30 + 31 + c;
					cout << a << "-" << b << "-" << c << "是" << a << "年的第" << x << "天" << endl;
				}
				else {
					cout << "输入错误-日与月的关系非法" << endl;
				}
				break;
			case 7:
				if (c <= 31) {
					x = 31 + 29 + 31 + 30 + 31 + 30 + c;
					cout << a << "-" << b << "-" << c << "是" << a << "年的第" << x << "天" << endl;
				}
				else {
					cout << "输入错误-日与月的关系非法" << endl;
				}
				break;
			case 8:
				if (c <= 31) {
					x = 31 + 29 + 31 + 30 + 31 + 30 + 31 + c;
					cout << a << "-" << b << "-" << c << "是" << a << "年的第" << x << "天" << endl;
				}
				else {
					cout << "输入错误-日与月的关系非法" << endl;
				}
				break;
			case 9:
				if (c <= 30) {
					x = 31 + 29 + 31 + 30 + 31 + 30 + 31 + 31 + c;
					cout << a << "-" << b << "-" << c << "是" << a << "年的第" << x << "天" << endl;
				}
				else {
					cout << "输入错误-日与月的关系非法" << endl;
				}
				break;
			case 10:
				if (c <= 31) {
					x = 31 + 29 + 31 + 30 + 31 + 30 + 31 + 31 + 30 + c;
					cout << a << "-" << b << "-" << c << "是" << a << "年的第" << x << "天" << endl;
				}
				else {
					cout << "输入错误-日与月的关系非法" << endl;
				}
				break;
			case 11:
				if (c <= 30) {
					x = 31 + 29 + 31 + 30 + 31 + 30 + 31 + 31 + 30 + 31 + c;
					cout << a << "-" << b << "-" << c << "是" << a << "年的第" << x << "天" << endl;
				}
				else {
					cout << "输入错误-日与月的关系非法" << endl;
				}
				break;
			case 12:
				if (c <= 31) {
					x = 31 + 29 + 31 + 30 + 31 + 30 + 31 + 31 + 30 + 31 + 30 + c;
					cout << a << "-" << b << "-" << c << "是" << a << "年的第" << x << "天" << endl;
				}
				else {
					cout << "输入错误-日与月的关系非法" << endl;
				}
				break;
			default:
				cout << "输入错误-月份不正确" << endl;
				break;
		}
	}

	return 0;
}