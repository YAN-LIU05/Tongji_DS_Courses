/* 2352018 ĞÅ06 ÁõÑå */
#define _CRT_SECURE_NO_WARNINGS
#include<stdio.h>
#include<math.h>
#include <stdbool.h>

int main()
{
	int a, b, c, d, e, f, g, h, i, j, m, n;
	double x, y;
	printf("ÇëÊäÈë[0-100ÒÚ)Ö®¼äµÄÊı×Ö:\n");
	scanf("%lf", &x);

	x += 0.0001;
	j = (int)(x / 1000000000);
	i = (int)(x / 100000000 - j * 10);
	h = (int)(x / 10000000 - j * 100 - i * 10);
	g = (int)(x / 1000000 - j * 1000 - i * 100 - h * 10);
	f = (int)(x / 100000 - j * 10000 - i * 1000 - h * 100 - g * 10);
	e = (int)(x / 10000 - j * 100000 - i * 10000 - h * 1000 - g * 100 - f * 10);
	d = (int)(x / 1000 - j * 1000000 - i * 100000 - h * 10000 - g * 1000 - f * 100 - e * 10);
	c = (int)(x / 100 - j * 10000000 - i * 1000000 - h * 100000 - g * 10000 - f * 1000 - e * 100 - d * 10);
	b = (int)(x / 10 - j * 100000000 - i * 10000000 - h * 1000000 - g * 100000 - f * 10000 - e * 1000 - d * 100 - c * 10);
	a = (int)((x / 10.0 - floor(x / 10)) * 10);
	y = floor(x);
	m = (int)((x - y) * 10);
	n = (int)((x - y) * 100 - 10 * m);

	printf("´óĞ´½á¹ûÊÇ:\n");

	switch (j) {
		case 1:
			printf("Ò¼Ê°");
			break;
		case 2:
			printf("·¡Ê°");
			break;
		case 3:
			printf("ÈşÊ°");
			break;
		case 4:
			printf("ËÁÊ°");
			break;
		case 5:
			printf("ÎéÊ°");
			break;
		case 6:
			printf("Â½Ê°");
			break;
		case 7:
			printf("ÆâÊ°");
			break;
		case 8:
			printf("°ÆÊ°");
			break;
		case 9:
			printf("¾ÁÊ°");
			break;
		default:
			printf("");
			break;
	}

	switch (i) {
		case 1:
			printf("Ò¼ÒÚ");
			break;
		case 2:
			printf("·¡ÒÚ");
			break;
		case 3:
			printf("ÈşÒÚ");
			break;
		case 4:
			printf("ËÁÒÚ");
			break;
		case 5:
			printf("ÎéÒÚ");
			break;
		case 6:
			printf("Â½ÒÚ");
			break;
		case 7:
			printf("ÆâÒÚ");
			break;
		case 8:
			printf("°ÆÒÚ");
			break;
		case 9:
			printf("¾ÁÒÚ");
			break;
		default:
			if (j == 0) {
				printf("");
			}
			else {
				printf("ÒÚ");
			}
			break;
	}

	switch (h) {
		case 1:
			printf("Ò¼Çª");
			break;
		case 2:
			printf("·¡Çª");
			break;
		case 3:
			printf("ÈşÇª");
			break;
		case 4:
			printf("ËÁÇª");
			break;
		case 5:
			printf("ÎéÇª");
			break;
		case 6:
			printf("Â½Çª");
			break;
		case 7:
			printf("ÆâÇª");
			break;
		case 8:
			printf("°ÆÇª");
			break;
		case 9:
			printf("¾ÁÇª");
			break;
		default:
			if ((!i && !j) || (!g)) {
				printf("");
			}
			else {
				printf("Áã");
			}
			break;
	}

	switch (g) {
		case 1:
			printf("Ò¼°Û");
			break;
		case 2:
			printf("·¡°Û");
			break;
		case 3:
			printf("Èş°Û");
			break;
		case 4:
			printf("ËÁ°Û");
			break;
		case 5:
			printf("Îé°Û");
			break;
		case 6:
			printf("Â½°Û");
			break;
		case 7:
			printf("Æâ°Û");
			break;
		case 8:
			printf("°Æ°Û");
			break;
		case 9:
			printf("¾Á°Û");
			break;
		default:
			if ((!h && !i && !j) || !f) {
				printf("");
			}
			else {
				printf("Áã");
			}
			break;
	}

	switch (f) {
		case 1:
			printf("Ò¼Ê°");
			break;
		case 2:
			printf("·¡Ê°");
			break;
		case 3:
			printf("ÈşÊ°");
			break;
		case 4:
			printf("ËÁÊ°");
			break;
		case 5:
			printf("ÎéÊ°");
			break;
		case 6:
			printf("Â½Ê°");
			break;
		case 7:
			printf("ÆâÊ°");
			break;
		case 8:
			printf("°ÆÊ°");
			break;
		case 9:
			printf("¾ÁÊ°");
			break;
		default:
			if (!g && !h && !i && !j) {
				printf("");
			}
			else if (e) {
				printf("Áã");
			}
			break;
	}

	switch (e) {
		case 1:
			printf("Ò¼Íò");
			break;
		case 2:
			printf("·¡Íò");
			break;
		case 3:
			printf("ÈşÍò");
			break;
		case 4:
			printf("ËÁÍò");
			break;
		case 5:
			printf("ÎéÍò");
			break;
		case 6:
			printf("Â½Íò");
			break;
		case 7:
			printf("ÆâÍò");
			break;
		case 8:
			printf("°ÆÍò");
			break;
		case 9:
			printf("¾ÁÍò");
			break;
		default:
			if (f || g || h) {
				printf("Íò");
			}
			break;
	}

	switch (d) {
		case 1:
			printf("Ò¼Çª");
			break;
		case 2:
			printf("·¡Çª");
			break;
		case 3:
			printf("ÈşÇª");
			break;
		case 4:
			printf("ËÁÇª");
			break;
		case 5:
			printf("ÎéÇª");
			break;
		case 6:
			printf("Â½Çª");
			break;
		case 7:
			printf("ÆâÇª");
			break;
		case 8:
			printf("°ÆÇª");
			break;
		case 9:
			printf("¾ÁÇª");
			break;
		default:
			if ((!e && !f && !g && !h && !i && !j) || !c) {
				printf("");
			}
			else {
				printf("Áã");
			}
			break;
	}

	switch (c) {
		case 1:
			printf("Ò¼°Û");
			break;
		case 2:
			printf("·¡°Û");
			break;
		case 3:
			printf("Èş°Û");
			break;
		case 4:
			printf("ËÁ°Û");
			break;
		case 5:
			printf("Îé°Û");
			break;
		case 6:
			printf("Â½°Û");
			break;
		case 7:
			printf("Æâ°Û");
			break;
		case 8:
			printf("°Æ°Û");
			break;
		case 9:
			printf("¾Á°Û");
			break;
		default:
			if ((!d && !e && !f && !g && !h && !i && !j) || !b) {
				printf("");
			}
			else {
				printf("Áã");
			}
			break;
	}

	bool u, v;
	u = c || d || e || f || g || h || i || j;
	v = a;
	switch (b) {
		case 1:
			printf("Ò¼Ê°");
			break;
		case 2:
			printf("·¡Ê°");
			break;
		case 3:
			printf("ÈşÊ°");
			break;
		case 4:
			printf("ËÁÊ°");
			break;
		case 5:
			printf("ÎéÊ°");
			break;
		case 6:
			printf("Â½Ê°");
			break;
		case 7:
			printf("ÆâÊ°");
			break;
		case 8:
			printf("°ÆÊ°");
			break;
		case 9:
			printf("¾ÁÊ°");
			break;
		default:
			switch (u) {
				case 0:
					printf("");
					break;
				case 1:
					switch (v) {
						case 1:
							printf("Áã");
							break;
						default:
							printf("");
							break;
					}
			}
			break;
	}

	bool p, q;
	p = b || c || d || e || f || g || h || i || j || m || n;
	q = b || c || d || e || f || g || h || i || j;
	switch (a) {
		case 1:
			printf("Ò¼Ô²");
			break;
		case 2:
			printf("·¡Ô²");
			break;
		case 3:
			printf("ÈşÔ²");
			break;
		case 4:
			printf("ËÁÔ²");
			break;
		case 5:
			printf("ÎéÔ²");
			break;
		case 6:
			printf("Â½Ô²");
			break;
		case 7:
			printf("ÆâÔ²");
			break;
		case 8:
			printf("°ÆÔ²");
			break;
		case 9:
			printf("¾ÁÔ²");
			break;
		default:
			switch (p) {
				case 0:
					printf("ÁãÔ²");
					break;
				case 1:
					switch (q) {
						case 1:
							printf("Ô²");
							break;
						default:
							printf("");
							break;
					}
			}
			break;
	}

	bool w;
	w = !a && !b && !c && !d && !e && !f && !g && !h && !i && !j;
	switch (m) {
		case 1:
			printf("Ò¼½Ç");
			break;
		case 2:
			printf("·¡½Ç");
			break;
		case 3:
			printf("Èş½Ç");
			break;
		case 4:
			printf("ËÁ½Ç");
			break;
		case 5:
			printf("Îé½Ç");
			break;
		case 6:
			printf("Â½½Ç");
			break;
		case 7:
			printf("Æâ½Ç");
			break;
		case 8:
			printf("°Æ½Ç");
			break;
		case 9:
			printf("¾Á½Ç");
			break;
		default:
			switch (w) {
				case 1:
					break;
				case 0:
					switch (n) {
						case 0:
							break;
						default:
							printf("Áã");
					}
			}
	}

	switch (n) {
		case 1:
			printf("Ò¼·Ö");
			break;
		case 2:
			printf("·¡·Ö");
			break;
		case 3:
			printf("Èş·Ö");
			break;
		case 4:
			printf("ËÁ·Ö");
			break;
		case 5:
			printf("Îé·Ö");
			break;
		case 6:
			printf("Â½·Ö");
			break;
		case 7:
			printf("Æâ·Ö");
			break;
		case 8:
			printf("°Æ·Ö");
			break;
		case 9:
			printf("¾Á·Ö");
			break;
		default:
			printf("Õû");
			break;
	}

	printf("\n");

	return 0;
}