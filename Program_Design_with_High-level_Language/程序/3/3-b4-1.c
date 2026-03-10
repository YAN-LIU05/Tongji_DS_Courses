/* 2352018 信06 刘彦 */
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include<math.h> 

int main()
{
	const double pi = 3.14159;
	int a, b, t;
	float S;
	printf("请输入三角形的两边及其夹角(角度)\n");
	scanf("%d %d %d", &a, &b, &t);

	S = (float)(a * b * sin(t * pi / 180)) / 2;
	printf("三角形面积为 : %.3f\n", S);

	return 0;
}