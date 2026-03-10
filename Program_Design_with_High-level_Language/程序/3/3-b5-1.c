/* 2352018 信06 刘彦 */
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>

int main()
{
	int a, b, c, x;
	printf("请输入年，月，日\n");
	scanf("%d %d %d", &a, &b, &c);
	x = 0;

	if ((a % 4 != 0) || (a % 400 != 0) && (a % 100 == 0)) {
		switch (b) {
			case 1:
				if (c <= 31) {
					x = c;
					printf("%d-%d-%d是%d年的第%d天\n", a, b, c, a, x);
				}
				else {
					printf("输入错误-日与月的关系非法\n");
				}
				break;
			case 2:
				if (c <= 28) {
					x = 31 + c;
					printf("%d-%d-%d是%d年的第%d天\n", a, b, c, a, x);
				}
				else {
					printf("输入错误-日与月的关系非法\n");
				}
				break;
			case 3:
				if (c <= 31) {
					x = 31 + 28 + c;
					printf("%d-%d-%d是%d年的第%d天\n", a, b, c, a, x);
				}
				else {
					printf("输入错误-日与月的关系非法\n");
				}
				break;
			case 4:
				if (c <= 30) {
					x = 31 + 28 + 31 + c;
					printf("%d-%d-%d是%d年的第%d天\n", a, b, c, a, x);
				}
				else {
					printf("输入错误-日与月的关系非法\n");
				}
				break;
			case 5:
				if (c <= 31) {
					x = 31 + 28 + 31 + 30 + c;
					printf("%d-%d-%d是%d年的第%d天\n", a, b, c, a, x);
				}
				else {
					printf("输入错误-日与月的关系非法\n");
				}
				break;
			case 6:
				if (c <= 30) {
					x = 31 + 28 + 31 + 30 + 31 + c;
					printf("%d-%d-%d是%d年的第%d天\n", a, b, c, a, x);
				}
				else {
					printf("输入错误-日与月的关系非法\n");
				}
				break;
			case 7:
				if (c <= 31) {
					x = 31 + 28 + 31 + 30 + 31 + 30 + c;
					printf("%d-%d-%d是%d年的第%d天\n", a, b, c, a, x);
				}
				else {
					printf("输入错误-日与月的关系非法\n");
				}
				break;
			case 8:
				if (c <= 31) {
					x = 31 + 28 + 31 + 30 + 31 + 30 + 31 + c;
					printf("%d-%d-%d是%d年的第%d天\n", a, b, c, a, x);
				}
				else {
					printf("输入错误-日与月的关系非法\n");
				}
				break;
			case 9:
				if (c <= 30) {
					x = 31 + 28 + 31 + 30 + 31 + 30 + 31 + 31 + c;
					printf("%d-%d-%d是%d年的第%d天\n", a, b, c, a, x);
				}
				else {
					printf("输入错误-日与月的关系非法\n");
				}
				break;
			case 10:
				if (c <= 31) {
					x = 31 + 28 + 31 + 30 + 31 + 30 + 31 + 31 + 30 + c;
					printf("%d-%d-%d是%d年的第%d天\n", a, b, c, a, x);
				}
				else {
					printf("输入错误-日与月的关系非法\n");
				}
				break;
			case 11:
				if (c <= 30) {
					x = 31 + 28 + 31 + 30 + 31 + 30 + 31 + 31 + 30 + 31 + c;
					printf("%d-%d-%d是%d年的第%d天\n", a, b, c, a, x);
				}
				else {
					printf("输入错误-日与月的关系非法\n");
				}
				break;
			case 12:
				if (c <= 31) {
					x = 31 + 28 + 31 + 30 + 31 + 30 + 31 + 31 + 30 + 31 + 30 + c;
					printf("%d-%d-%d是%d年的第%d天\n", a, b, c, a, x);
				}
				else {
					printf("输入错误-日与月的关系非法\n");
				}
				break;
			default:
				printf("输入错误-月份不正确\n");
				break;
		}
	}
	else {
		switch (b) {
			case 1:
				if (c <= 31) {
					x = c;
					printf("%d-%d-%d是%d年的第%d天\n", a, b, c, a, x);
				}
				else {
					printf("输入错误-日与月的关系非法\n");
				}
				break;
			case 2:
				if (c <= 29) {
					x = 31 + c;
					printf("%d-%d-%d是%d年的第%d天\n", a, b, c, a, x);
				}
				else {
					printf("输入错误-日与月的关系非法\n");
				}
				break;
			case 3:
				if (c <= 31) {
					x = 31 + 29 + c;
					printf("%d-%d-%d是%d年的第%d天\n", a, b, c, a, x);
				}
				else {
					printf("输入错误-日与月的关系非法\n");
				}
				break;
			case 4:
				if (c <= 30) {
					x = 31 + 29 + 31 + c;
					printf("%d-%d-%d是%d年的第%d天\n", a, b, c, a, x);
				}
				else {
					printf("输入错误-日与月的关系非法\n");
				}
				break;
			case 5:
				if (c <= 31) {
					x = 31 + 29 + 31 + 30 + c;
					printf("%d-%d-%d是%d年的第%d天\n", a, b, c, a, x);
				}
				else {
					printf("输入错误-日与月的关系非法\n");
				}
				break;
			case 6:
				if (c <= 30) {
					x = 31 + 29 + 31 + 30 + 31 + c;
					printf("%d-%d-%d是%d年的第%d天\n", a, b, c, a, x);
				}
				else {
					printf("输入错误-日与月的关系非法\n");
				}
				break;
			case 7:
				if (c <= 31) {
					x = 31 + 29 + 31 + 30 + 31 + 30 + c;
					printf("%d-%d-%d是%d年的第%d天\n", a, b, c, a, x);
				}
				else {
					printf("输入错误-日与月的关系非法\n");
				}
				break;
			case 8:
				if (c <= 31) {
					x = 31 + 29 + 31 + 30 + 31 + 30 + 31 + c;
					printf("%d-%d-%d是%d年的第%d天\n", a, b, c, a, x);
				}
				else {
					printf("输入错误-日与月的关系非法\n");
				}
				break;
			case 9:
				if (c <= 30) {
					x = 31 + 29 + 31 + 30 + 31 + 30 + 31 + 31 + c;
					printf("%d-%d-%d是%d年的第%d天\n", a, b, c, a, x);
				}
				else {
					printf("输入错误-日与月的关系非法\n");
				}
				break;
			case 10:
				if (c <= 31) {
					x = 31 + 29 + 31 + 30 + 31 + 30 + 31 + 31 + 30 + c;
					printf("%d-%d-%d是%d年的第%d天\n", a, b, c, a, x);
				}
				else {
					printf("输入错误-日与月的关系非法\n");
				}
				break;
			case 11:
				if (c <= 30) {
					x = 31 + 29 + 31 + 30 + 31 + 30 + 31 + 31 + 30 + 31 + c;
					printf("%d-%d-%d是%d年的第%d天\n", a, b, c, a, x);
				}
				else {
					printf("输入错误-日与月的关系非法\n");
				}
				break;
			case 12:
				if (c <= 31) {
					x = 31 + 29 + 31 + 30 + 31 + 30 + 31 + 31 + 30 + 31 + 30 + c;
					printf("%d-%d-%d是%d年的第%d天\n", a, b, c, a, x);
				}
				else {
					printf("输入错误-日与月的关系非法\n");
				}
				break;
			default:
				printf("输入错误-月份不正确\n");
				break;
		}
	}

	return 0;
}