#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
int main()
{
    int n, m, i, a=0;
    scanf("%d %d", &n, &m);
    for(i=2;i<=n;i++)
        {
            a=(a+m)%i;
        }
    printf ("%d", a);
    return 0;
}
