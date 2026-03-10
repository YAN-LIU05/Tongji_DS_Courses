/* 2352018 信06 刘彦 */
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <math.h>

int main()
{
	double a, b, c, d, e, f, g, h, i, j, m, n, x, y;
	printf("请输入[0-100亿)之间的数字\n");
	scanf("%lf", &x);

	x += 0.00001;
	j = (int)(x / 1000000000);
	i = (int)(x / 100000000 - j * 10);
	h = (int)(x / 10000000 - j * 100 - i * 10);
	g = (int)(x / 1000000 - j * 1000 - i * 100 - h * 10);
	f = (int)(x / 100000 - j * 10000 - i * 1000 - h * 100 - g * 10);
	e = (int)(x / 10000 - j * 100000 - i * 10000 - h * 1000 - g * 100 - f * 10);
	d = (int)(x / 1000 - j * 1000000 - i * 100000 - h * 10000 - g * 1000 - f * 100 - e * 10);
	c = (int)(x / 100 - j * 10000000 - i * 1000000 - h * 100000 - g * 10000 - f * 1000 - e * 100 - d * 10);
	b = (int)(x / 10 - j * 100000000 - i * 10000000 - h * 1000000 - g * 100000 - f * 10000 - e * 1000 - d * 100 - c * 10);
	a = (int)(x / 1 - j * 1000000000 - i * 100000000 - h * 10000000 - g * 1000000 - f * 100000 - e * 10000 - d * 1000 - c * 100 - b * 10);
	y = floor(x);
	m = (int)((x - y) * 10);
	n = (int)((x - y) * 100 - 10 * m);

	printf("十亿位 : %.0f\n", j);
	printf("亿位   : %.0f\n", i);
	printf("千万位 : %.0f\n", h);
	printf("百万位 : %.0f\n", g);
	printf("十万位 : %.0f\n", f);
	printf("万位   : %.0f\n", e);
	printf("千位   : %.0f\n", d);
	printf("百位   : %.0f\n", c);
	printf("十位   : %.0f\n", b);
	printf("圆     : %.0f\n", a);
	printf("角     : %.0f\n", m);
	printf("分     : %.0f\n", n);

	return 0;
}