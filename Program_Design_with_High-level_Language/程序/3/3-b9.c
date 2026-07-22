/* 0000000 ĞÅ06 ÄäÃû */
#include <stdio.h>
int main()
{
    int a, b;
    for (a = 1; a <= 9; a++)
    {
        for (b = 1; b <= a; b++)
        {
            printf("%dx%d=%d", b, a, b * a);
            if (a * b < 10)
                printf("   ");
            else
                printf("  ");
        }
        printf("\n");
    }
    printf("\n");

    return 0;
}