/* 2352018 信06 刘彦 */
#define _CRT_SECURE_NO_WARNINGS  
#include <stdio.h>  

int main() {
    int ret, x, c;

    while (1) {
        printf("请输入x的值[0-100] : ");
        ret = scanf("%d", &x);
        if (ret == 1) {
            if (x >= 0 && x <= 100) {
                break;
            }
            else {
                printf("输入有错[ret=%d x=%d],请重新输入\n", ret, x);   // 当输入值超过范围，打印错误消息并重新循环  
            }
        }
        else {
            printf("输入有错[ret=%d x=%d],请重新输入\n", ret, x); //确认一下，ret的值（即scanf的返回值）是什么含义？ 
            while ((c = getchar()) != '\n');   // 清空输入缓冲区，直到遇到换行符 
        }
    }

    printf("ret=%d x=%d\n", ret, x);

    return 0;
}