/* 2352018 –≈06 ¡ı—Â */
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