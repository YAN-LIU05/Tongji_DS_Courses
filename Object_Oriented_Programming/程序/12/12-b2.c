/* 2352018 大数据 刘彦 */
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <math.h>

// 定义definite_integration函数，用于计算定积分
double definite_integration(double (*func)(double), double low, double high, int n) 
{
    double width = (high - low) / n; // 每个小矩形的宽度
    double integral = 0.0;
    for (int i = 0; i < n; i++) 
    {
        double x = low + i * width + width; // 取右端点的值
        integral += func(x) * width;
    }
    return integral;
}

int main() 
{
    int n;
    double low, high, value;

    // 计算sin(x)dx的积分
    printf("请输入sinxdx的下限、上限及区间划分数量\n");
    scanf("%lf %lf %d", &low, &high, &n);
    value = definite_integration(sin, low, high, n);
    printf("sinxdx[%g~%g/n=%d] : %g\n", low, high, n, value);

    // 计算cos(x)dx的积分
    printf("请输入cosxdx的下限、上限及区间划分数量\n");
    scanf("%lf %lf %d", &low, &high, &n);
    value = definite_integration(cos, low, high, n);
    printf("cosxdx[%g~%g/n=%d] : %g\n", low, high, n, value);

    // 计算e^(x)dx的积分
    printf("请输入e^xdx的下限、上限及区间划分数量\n");
    scanf("%lf %lf %d", &low, &high, &n);
    value = definite_integration(exp, low, high, n);
    printf("e^xdx[%g~%g/n=%d] : %g\n", low, high, n, value);

    return 0;
}