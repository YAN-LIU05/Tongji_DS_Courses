/* 2352018 信06 刘彦 */
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>

int main()
{
	int a, a1, a2, a3, a4, a5;
	printf("请输入一个[1..30000]间的整数:\n");
	scanf("%d", &a);

	a5 = a % 10;
	a4 = (a / 10) % 10;
	a3 = (a / 100) % 10;
	a2 = (a / 1000) % 10;
	a1 = a / 10000;

	printf("万位 : %d\n", a1);
	printf("千位 : %d\n", a2);
	printf("百位 : %d\n", a3);
	printf("十位 : %d\n", a4);
	printf("个位 : %d\n", a5);

	return 0;
}