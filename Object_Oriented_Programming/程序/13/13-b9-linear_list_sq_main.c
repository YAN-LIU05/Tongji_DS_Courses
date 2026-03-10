/* 2352018 大数据 刘彦 */
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <math.h>
#include <string.h>
#include <stdlib.h>
#include "13-b9-linear_list_sq.h"

#define INSERT_NUM		115		//初始插入表中的元素数量
#define TEST_NUM		6		

#ifdef ELEMTYPE_IS_DOUBLE
#define MAX_NUM_PER_LINE 	5		//每行最多输出的元素个数
#elif defined (ELEMTYPE_IS_CHAR_ARRAY) || defined (ELEMTYPE_IS_CHAR_P)
#define MAX_NUM_PER_LINE 	5		//每行最多输出的元素个数
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT) || defined (ELEMTYPE_IS_STRUCT_STUDENT_P)
#define MAX_NUM_PER_LINE 	1		//每行最多输出的元素个数
#else	//缺省当做int处理
#define MAX_NUM_PER_LINE 	10		//每行最多输出的元素个数
#endif

int line_count = 0;   //打印链表时的计数器

/* 用于比较两个值是否相等的具体函数，与LocateElem中的函数指针定义相同，调用时代入
   int LocateElem(sqlist L, ElemType e, Status (*compare)(ElemType e1, ElemType e2)) */
Status MyCompare(ElemType e1, ElemType e2)
{
#ifdef ELEMTYPE_IS_DOUBLE
    if (fabs(e1 - e2) < 1e-6)
#elif defined (ELEMTYPE_IS_CHAR_ARRAY) || defined (ELEMTYPE_IS_CHAR_P)
    if (strcmp(e1, e2) == 0)
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT)
    if (e1.num == e2.num)
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT_P)
    if (e1->num == e2->num)
#else	//缺省当做int处理
    if (e1 == e2)
#endif
        return TRUE;
    else
        return FALSE;
}

/* 用于访问某个元素的值的具体函数，与ListTraverse中的函数指针定义相同，调用时代入
   Status ListTraverse(sqlist L, Status (*visit)(ElemType e)) */
Status MyVisit(ElemType e)
{
#ifdef ELEMTYPE_IS_DOUBLE
    printf("%5.1f->", e);
#elif defined (ELEMTYPE_IS_CHAR_ARRAY) || defined (ELEMTYPE_IS_CHAR_P)
    printf("%s->", e);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT)
    printf("%d-%s-%c-%f-%s->", e.num, e.name, e.sex, e.score, e.addr);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT_P)
    printf("%d-%s-%c-%f-%s->", e->num, e->name, e->sex, e->score, e->addr);
#else	//缺省当做int处理
    printf("%3d->", e);
#endif

    /* 每输出MAX_NUM_PER_LINE个，打印一个换行 */
    if ((++line_count) % MAX_NUM_PER_LINE == 0)
        printf("\n");

    return OK;
}

int main()
{
#if defined (ELEMTYPE_IS_STRUCT_STUDENT)
    /* 这两种数据类型需要预置数据 */
    ElemType e[] = { {1001, "张三", 'M', 76.5, "上海市杨浦区"},
          {1002, "李四", 'F', 87, "上海市普陀区"},
          {1003, "王五", 'M', 80, "浙江省杭州市"},
          {1004, "赵六", 'M', 54, "浙江省绍兴市"},
          {1005, "牛七", 'F', 85, "江苏省南京市"},
          {1006, "马八", 'M', 60, "江苏省苏州市"} };
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT_P)
    /* 这两种数据类型需要预置数据 */
    ET       e[] = { {1001, "张三", 'M', 76.5, "上海市杨浦区"},
          {1002, "李四", 'F', 87, "上海市普陀区"},
          {1003, "王五", 'M', 80, "浙江省杭州市"},
          {1004, "赵六", 'M', 54, "浙江省绍兴市"},
          {1005, "牛七", 'F', 85, "江苏省南京市"},
          {1006, "马八", 'M', 60, "江苏省苏州市"} };
#endif
    sqlist   L;
    ElemType e1, e2;
    int      i, pos;

    InitList(&L);

    printf("空表=%s\n", (ListEmpty(L) == TRUE) ? "TRUE" : "FALSE");
    printf("表长=%d\n\n", ListLength(L));

#ifdef ELEMTYPE_IS_DOUBLE
    printf("插入%d个元素：\n", INSERT_NUM);
    for (i = INSERT_NUM * 2; i > 0; i -= 2)
        ListInsert(&L, 1, (ElemType)i);	//i是整型，严格来说需要转换为double
#elif defined (ELEMTYPE_IS_CHAR_ARRAY)
    printf("插入%d个元素：\n", INSERT_NUM);
    for (i = INSERT_NUM * 2; i > 0; i -= 2) {
        sprintf(e1, "test%03d", i);
        ListInsert(&L, 1, e1);
    }
#elif defined (ELEMTYPE_IS_CHAR_P)
    printf("插入%d个元素：\n", INSERT_NUM);
    e1 = (ElemType)malloc(80 * sizeof(char));	//e1实际是指针，必须先申请相应的空间
    e2 = (ElemType)malloc(80 * sizeof(char));	//e2实际是指针，必须先申请相应的空间
    for (i = INSERT_NUM * 2; i > 0; i -= 2) {
        sprintf(e1, "test%03d", i);
        ListInsert(&L, 1, e1);
    }
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT)
    printf("插入6个元素：\n");
    for (i = 0; i < 6; i++)
        ListInsert(&L, ListLength(L) + 1, *(e + i));
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT_P)
    printf("插入6个元素：\n");
    e1 = (ElemType)malloc(sizeof(ET));
    e2 = (ElemType)malloc(sizeof(ET));

    printf("插入6个元素：\n");
    for (i = 0; i < 6; i++)
        ListInsert(&L, ListLength(L) + 1, (e + i));
#else	//缺省当做int处理
    printf("插入%d个元素：\n", INSERT_NUM);
    for (i = INSERT_NUM * 2; i > 0; i -= 2)
        ListInsert(&L, 1, i);
#endif

    ListTraverse(L, MyVisit);//此处传入MyVisit函数名

    printf("空表=%s\n", (ListEmpty(L) == TRUE) ? "TRUE" : "FALSE");
    printf("表长=%d\n\n", ListLength(L));
    printf("\n");
    /* 分别取第1、最后、以及小于第1、大于最后的4种情况下的的元素值、前驱值、后继值
       最后再加一个任意输入值 */

    printf("下面测试Priorelem和Nextelem\n");

    for (i = 0; i < 5; i++) {
        int pos;
        switch (i) {
            case 0:
                pos = 1;
                break;
            case 1:
                pos = ListLength(L);
                break;
            case 2:
                pos = -1;
                break;
            case 3:
                pos = ListLength(L) + 1;
                break;
            case 4:
                printf("请输入要取元素的位序[1..%d]：", ListLength(L));
                scanf("%d", &pos);
                break;
        }

        /* 取第1个元素以及前驱、后继 */
        if (GetElem(L, pos, &e1) == OK) {
#ifdef ELEMTYPE_IS_DOUBLE
            printf("第%d个元素=%5.lf\n", pos, e1);
#elif defined (ELEMTYPE_IS_CHAR_ARRAY) || defined (ELEMTYPE_IS_CHAR_P)
            printf("第%d个元素=%s\n", pos, e1);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT)
            printf("第%d个元素=\"%d.%s.%c.%f.%s\"\n", pos, e1.num, e1.name, e1.sex, e1.score, e1.addr);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT_P)
            printf("第%d个元素=\"%d.%s.%c.%f.%s\"\n", pos, e1->num, e1->name, e1->sex, e1->score, e1->addr);
#else	//缺省当做int处理
            printf("第%d个元素=%d\n", pos, e1);
#endif

            /* 只有取得了某个元素，才能取前驱和后继 */
            if (PriorElem(L, e1, &e2, MyCompare) == OK)
#ifdef ELEMTYPE_IS_DOUBLE
                printf("第%d个元素(%5.1f)的前驱=%5.1f\n", pos, e1, e2);
#elif defined (ELEMTYPE_IS_CHAR_ARRAY) || defined (ELEMTYPE_IS_CHAR_P)
                printf("第%d个元素(%s)的前驱=%s\n", pos, e1, e2);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT)
                printf("第%d个元素\"%d.%s.%c.%f.%s\"的前驱=\"%d.%s.%c.%f.%s\"\n", pos, e1.num, e1.name, e1.sex, e1.score, e1.addr, e2.num, e2.name, e2.sex, e2.score, e2.addr);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT_P)
                printf("第%d个元素\"%d.%s.%c.%f.%s\"的前驱=\"%d.%s.%c.%f.%s\"\n", pos, e1->num, e1->name, e1->sex, e1->score, e1->addr, e2->num, e2->name, e2->sex, e2->score, e2->addr);
#else	//缺省当做int处理
                printf("第%d个元素(%d)的前驱=%d\n", pos, e1, e2);
#endif
            else
#ifdef ELEMTYPE_IS_DOUBLE
                printf("无法取得第%d个元素(%5.1f)的前驱\n", pos, e1);
#elif defined (ELEMTYPE_IS_CHAR_ARRAY) || defined (ELEMTYPE_IS_CHAR_P)
                printf("无法取得第%d个元素(%s)的前驱\n", pos, e1);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT)
                printf("无法取得第%d个元素\"%d.%s.%c.%f.%s\"的前驱\n", pos, e1.num, e1.name, e1.sex, e1.score, e1.addr);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT_P)
                printf("无法取得第%d个元素\"%d.%s.%c.%f.%s\"的前驱\n", pos, e1->num, e1->name, e1->sex, e1->score, e1->addr);
#else	//缺省当做int处理
                printf("无法取得第%d个元素(%d)的前驱\n", pos, e1);
#endif

            if (NextElem(L, e1, &e2, MyCompare) == OK)
#ifdef ELEMTYPE_IS_DOUBLE
                printf("第%d个元素(%5.1f)的后继=%5.1f\n", pos, e1, e2);
#elif defined (ELEMTYPE_IS_CHAR_ARRAY) || defined (ELEMTYPE_IS_CHAR_P)
                printf("第%d个元素(%s)的后继=%s\n", pos, e1, e2);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT)
                printf("第%d个元素\"%d.%s.%c.%f.%s\"的后继=\"%d.%s.%c.%f.%s\"\n", pos, e1.num, e1.name, e1.sex, e1.score, e1.addr, e2.num, e2.name, e2.sex, e2.score, e2.addr);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT_P)
                printf("第%d个元素\"%d.%s.%c.%f.%s\"的后继=\"%d.%s.%c.%f.%s\"\n", pos, e1->num, e1->name, e1->sex, e1->score, e1->addr, e2->num, e2->name, e2->sex, e2->score, e2->addr);
#else	//缺省当做int处理
                printf("第%d个元素(%d)的后继=%d\n", pos, e1, e2);
#endif
            else
#ifdef ELEMTYPE_IS_DOUBLE
                printf("无法取得第%d个元素(%5.1f)的后继\n", pos, e1);
#elif defined (ELEMTYPE_IS_CHAR_ARRAY) || defined (ELEMTYPE_IS_CHAR_P)
                printf("无法取得第%d个元素(%s)的后继\n", pos, e1);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT)
                printf("无法取得第%d个元素\"%d.%s.%c.%f.%s\"的后继\n", pos, e1.num, e1.name, e1.sex, e1.score, e1.addr);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT_P)
                printf("无法取得第%d个元素\"%d.%s.%c.%f.%s\"的后继\n", pos, e1->num, e1->name, e1->sex, e1->score, e1->addr);
#else	//缺省当做int处理
                printf("无法取得第%d个元素(%d)的后继\n", pos, e1);
#endif
        }
        else
            printf("无法取得第%d个元素\n\n", pos);
    } // end of for
    printf("\nPriorelem和Nextelem测试结束\n");
    printf("\n");

    printf("下面测试LocateElem\n");

#ifdef ELEMTYPE_IS_DOUBLE
    printf("\n请输入要查找的元素：\n");
    scanf("%lf", &e1);
#elif defined (ELEMTYPE_IS_CHAR_ARRAY) || defined (ELEMTYPE_IS_CHAR_P)
    printf("\n请输入要查找的元素：\n");
    scanf("%s", e1);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT)
    printf("\n请输入要查找的元素的学号：\n");
    scanf("%d", &e1.num);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT_P)
    printf("\n请输入要查找的元素的学号：\n");
    scanf("%d", &e1->num);
#else	//缺省当做int处理
    printf("\n请输入要查找的元素：\n");
    scanf("%d", &e1);
#endif

    if ((pos = LocateElem(L, e1, MyCompare)) > 0)       //此处传入MyCompare函数名
#ifdef ELEMTYPE_IS_DOUBLE
        printf("元素%5.1f的位序=%d\n", e1, pos);
#elif defined (ELEMTYPE_IS_CHAR_ARRAY) || defined (ELEMTYPE_IS_CHAR_P)
        printf("元素%s的位序=%d\n", e1, pos);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT)
        printf("元素\"学号=%d\"的位序=%d\n", e1.num, pos);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT_P)
        printf("元素\"学号=%d\"的位序=%d\n", e1->num, pos);
#else	//缺省当做int处理
        printf("元素%d的位序=%d\n", e1, pos);
#endif
    else
#ifdef ELEMTYPE_IS_DOUBLE
        printf("找不到元素%5.1f\n", e1);
#elif defined (ELEMTYPE_IS_CHAR_ARRAY) || defined (ELEMTYPE_IS_CHAR_P)
        printf("找不到元素%s\n", e1);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT)
        printf("找不到元素\"学号=%d\"\n", e1.num);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT_P)
        printf("找不到元素\"学号=%d\"\n", e1->num);
#else	//缺省当做int处理
        printf("找不到元素%d\n", e1);
#endif
    printf("\nLocateElem测试结束\n");
    printf("\n");


    printf("下面测试ListInsert\n");

#ifdef ELEMTYPE_IS_DOUBLE
    printf("\n请输入要插入元素的值：\n");
    scanf("%lf", &e1);
#elif defined (ELEMTYPE_IS_CHAR_ARRAY) || defined (ELEMTYPE_IS_CHAR_P)
    printf("\n请输入要插入元素的值：\n");
    scanf("%s", e1);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT)
    printf("\n请输入要插入元素的值(学号 姓名 性别 成绩 地址)：\n");
    scanf("%d %s %c %f %s", &e1.num, e1.name, &e1.sex, &e1.score, e1.addr);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT_P)
    printf("\n请输入要插入元素的值(学号 姓名 性别 成绩 地址)：\n");
    scanf("%d %s %c %f %s", &e1->num, e1->name, &e1->sex, &e1->score, e1->addr);
#else	//缺省当做int处理
    printf("\n请输入要插入元素的值：\n");
    scanf("%d", &e1);
#endif

    printf("请输入要插入元素的位序：\n");
    scanf("%d", &pos);
    if (ListInsert(&L, pos, e1) == OK) {
#ifdef ELEMTYPE_IS_DOUBLE
        printf("在%d前插入元素=%5.1f成功\n", pos, e1);
#elif defined (ELEMTYPE_IS_CHAR_ARRAY) || defined (ELEMTYPE_IS_CHAR_P)
        printf("在%d前插入元素=%s成功\n", pos, e1);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT)
        printf("在%d前插入元素=\"%d.%s.%c.%f.%s\"成功\n", pos, e1.num, e1.name, e1.sex, e1.score, e1.addr);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT_P)
        printf("在%d前插入元素=\"%d.%s.%c.%f.%s\"成功\n", pos, e1->num, e1->name, e1->sex, e1->score, e1->addr);
#else	//缺省当做int处理
        printf("在%d前插入元素=%d成功\n", pos, e1);
#endif
        printf("新表为：\n");
        ListTraverse(L, MyVisit);
    }
    else
#ifdef ELEMTYPE_IS_DOUBLE
        printf("在%d前插入元素=%5.1f失败\n", pos, e1);
#elif defined (ELEMTYPE_IS_CHAR_ARRAY) || defined (ELEMTYPE_IS_CHAR_P)
        printf("在%d前插入元素=%s失败\n", pos, e1);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT)
        printf("在%d前插入元素=\"%d.%s.%c.%f.%s\"失败\n", pos, e1.num, e1.name, e1.sex, e1.score, e1.addr);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT_P)
        printf("在%d前插入元素=\"%d.%s.%c.%f.%s\"失败\n", pos, e1->num, e1->name, e1->sex, e1->score, e1->addr);
#else	//缺省当做int处理
        printf("在%d前插入元素%d失败\n", pos, e1);
#endif
    printf("\nListInsert测试结束\n");
    printf("\n");

    printf("下面测试新函数-ListInsert1\n");
#ifdef ELEMTYPE_IS_DOUBLE
    printf("\n请输入要插入元素的值：\n");
    scanf("%lf", &e1);
#elif defined (ELEMTYPE_IS_CHAR_ARRAY) || defined (ELEMTYPE_IS_CHAR_P)
    printf("\n请输入要插入元素的值：\n");
    scanf("%s", e1);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT)
    printf("\n请输入要插入元素的值(学号 姓名 性别 成绩 地址)：\n");
    scanf("%d %s %c %f %s", &e1.num, e1.name, &e1.sex, &e1.score, e1.addr);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT_P)
    printf("\n请输入要插入元素的值(学号 姓名 性别 成绩 地址)：\n");
    scanf("%d %s %c %f %s", &e1->num, e1->name, &e1->sex, &e1->score, e1->addr);
#else	//缺省当做int处理
    printf("\n请输入要插入元素的值：\n");
    scanf("%d", &e1);
#endif

#ifdef ELEMTYPE_IS_DOUBLE
    printf("\n请输入要插入元素后一个元素的值：\n");
    scanf("%lf", &e2);
#elif defined (ELEMTYPE_IS_CHAR_ARRAY) || defined (ELEMTYPE_IS_CHAR_P)
    printf("\n请输入要插入元素后一个元素的值：\n");
    scanf("%s", e2);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT)
    printf("\n请输入要插入元素后一个元素的学号：\n");
    scanf("%d", &e2.num);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT_P)
    printf("\n请输入要插入元素后一个元素的学号：\n");
    scanf("%d", &e2->num);
#else	//缺省当做int处理
    printf("\n请输入要插入元素后一个元素的值：\n");
    scanf("%d", &e2);
#endif

    if (ListInsert1(&L, e2, e1, MyCompare) == OK) {
#ifdef ELEMTYPE_IS_DOUBLE
        printf("插入元素=%5.1f成功\n", e1);
#elif defined (ELEMTYPE_IS_CHAR_ARRAY) || defined (ELEMTYPE_IS_CHAR_P)
        printf("插入元素=%s成功\n", e1);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT)
        printf("插入元素=\"%d.%s.%c.%f.%s\"成功\n", e1.num, e1.name, e1.sex, e1.score, e1.addr);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT_P)
        printf("插入元素=\"%d.%s.%c.%f.%s\"成功\n", e1->num, e1->name, e1->sex, e1->score, e1->addr);
#else	//缺省当做int处理
        printf("插入元素=%d成功\n", e1);
#endif
        printf("新表为：\n");
        ListTraverse(L, MyVisit);
    }
    else
#ifdef ELEMTYPE_IS_DOUBLE
        printf("插入元素=%5.1f失败\n", e1);
#elif defined (ELEMTYPE_IS_CHAR_ARRAY) || defined (ELEMTYPE_IS_CHAR_P)
        printf("插入元素=%s失败\n", e1);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT)
        printf("插入元素=\"%d.%s.%c.%f.%s\"失败\n", e1.num, e1.name, e1.sex, e1.score, e1.addr);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT_P)
        printf("插入元素=\"%d.%s.%c.%f.%s\"失败\n", e1->num, e1->name, e1->sex, e1->score, e1->addr);
#else	//缺省当做int处理
        printf("插入元素%d失败\n", e1);
#endif
    printf("\n新函数-ListInsert1测试结束\n");
    printf("\n");

    printf("下面测试ListDelete\n");

    printf("\n请输入要删除元素的位序：\n");
    scanf("%d", &pos);
    if (ListDelete(&L, pos, &e1) == OK) {
#ifdef ELEMTYPE_IS_DOUBLE
        printf("删除第%d元素=%5.1f成功\n", pos, e1);
#elif defined (ELEMTYPE_IS_CHAR_ARRAY) || defined (ELEMTYPE_IS_CHAR_P)
        printf("删除第%d元素=%s成功\n", pos, e1);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT)
        printf("删除第%d元素=\"%d.%s.%c.%f.%s\"成功\n", pos, e1.num, e1.name, e1.sex, e1.score, e1.addr);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT_P)
        printf("删除第%d元素=\"%d.%s.%c.%f.%s\"成功\n", pos, e1->num, e1->name, e1->sex, e1->score, e1->addr);
#else	//缺省当做int处理
        printf("删除第%d元素=%d成功\n", pos, e1);
#endif
        printf("新表为：\n");
        ListTraverse(L, MyVisit);
    }
    else
#ifdef ELEMTYPE_IS_DOUBLE
        printf("删除第%d元素=%5.1f失败\n", pos, e1);
#elif defined (ELEMTYPE_IS_CHAR_ARRAY) || defined (ELEMTYPE_IS_CHAR_P)
        printf("删除第%d元素=%s失败\n", pos, e1);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT)
        printf("删除第%d元素=\"%d.%s.%c.%f.%s\"失败\n", pos, e1.num, e1.name, e1.sex, e1.score, e1.addr);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT_P)
        printf("删除第%d元素=\"%d.%s.%c.%f.%s\"失败\n", pos, e1->num, e1->name, e1->sex, e1->score, e1->addr);
#else	//缺省当做int处理
        printf("删除第%d元素=%d失败\n", pos, e1);
#endif
    printf("\nListDelete测试结束\n");
    printf("\n");

    printf("下面测试新函数-ListDelete1\n");

#ifdef ELEMTYPE_IS_DOUBLE
    printf("\n请输入要删除元素的值（仅删除第1个元素）：\n");
    scanf("%lf", &e1);
#elif defined (ELEMTYPE_IS_CHAR_ARRAY) || defined (ELEMTYPE_IS_CHAR_P)
    printf("\n请输入要删除元素的值（仅删除第1个元素）：\n");
    scanf("%s", e1);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT)
    printf("\n请输入要删除元素的学号（仅删除第1个元素）：\n");
    scanf("%d", &e1.num);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT_P)
    printf("\n请输入要删除元素的学号（仅删除第1个元素）：\n");
    scanf("%d", &e1->num);
#else	//缺省当做int处理
    printf("\n请输入要删除元素的值（仅删除第1个元素）：\n");
    scanf("%d", &e1);
#endif
    if (ListDelete1(&L, e1, &MyCompare) == OK) {
#ifdef ELEMTYPE_IS_DOUBLE
        printf("删除元素=%5.1f成功\n", e1);
#elif defined (ELEMTYPE_IS_CHAR_ARRAY) || defined (ELEMTYPE_IS_CHAR_P)
        printf("删除元素=%s成功\n", e1);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT)
        printf("删除元素=\"%d.%s.%c.%f.%s\"成功\n", e1.num, e1.name, e1.sex, e1.score, e1.addr);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT_P)
        printf("删除元素=\"%d.%s.%c.%f.%s\"成功\n", e1->num, e1->name, e1->sex, e1->score, e1->addr);
#else	//缺省当做int处理
        printf("删除元素=%d成功\n", e1);
#endif
        printf("新表为：\n");
        ListTraverse(L, MyVisit);
    }
    else
#ifdef ELEMTYPE_IS_DOUBLE
        printf("删除元素=%5.1f失败\n", e1);
#elif defined (ELEMTYPE_IS_CHAR_ARRAY) || defined (ELEMTYPE_IS_CHAR_P)
        printf("删除元素=%s失败\n", e1);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT)
        printf("删除元素=\"%d.%s.%c.%f.%s\"失败\n", e1.num, e1.name, e1.sex, e1.score, e1.addr);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT_P)
        printf("删除元素=\"%d.%s.%c.%f.%s\"失败\n", e1->num, e1->name, e1->sex, e1->score, e1->addr);
#else	//缺省当做int处理
        printf("删除元素=%d失败\n", e1);
#endif

    printf("\n新函数-ListDelete1测试结束\n");
    printf("\n");

    printf("下面测试新函数-ListDelete2 按回车键继续\n");
#if defined (ELEMTYPE_IS_STRUCT_STUDENT)
    ElemType e_add[] = { {1001, "张三", 'M', 76.5, "上海市杨浦区"},
      {1001, "张三", 'F', 100, "上海市杨浦区"},
      {1001, "张三", 'M', 83, "上海市杨浦区"},
      {1001, "张三", 'F', 76.5, "浙江省杭州市"},
      {1001, "张三", 'M', 78, "上海市杨浦区"},
      {1002, "李四", 'F', 87, "上海市普陀区"} };
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT_P)
    ET       e_add[] = { {1001, "张三", 'M', 76.5, "上海市杨浦区"},
      {1001, "张三", 'F', 100, "上海市杨浦区"},
      {1001, "张三", 'M', 83, "上海市杨浦区"},
      {1001, "张三", 'F', 76.5, "浙江省杭州市"},
      {1001, "张三", 'M', 78, "上海市杨浦区"},
      {1002, "李四", 'F', 87, "上海市普陀区"} };
#endif
    while (1)
        if (getchar() == '\n')
            break;
#ifdef ELEMTYPE_IS_DOUBLE
    for (i = 0; i < TEST_NUM; i++)
        ListInsert(&L, 1, 2.0);
#elif defined (ELEMTYPE_IS_CHAR_ARRAY)
    for (i = 0; i < TEST_NUM; i++) {
        sprintf(e1, "test%03d", 2);
        ListInsert(&L, 1, e1);
    }
#elif defined (ELEMTYPE_IS_CHAR_P)
    e1 = (ElemType)malloc(80 * sizeof(char));	
    e2 = (ElemType)malloc(80 * sizeof(char));	
    for (i = 0; i < TEST_NUM; i++) {
        sprintf(e1, "test%03d", 2);
        ListInsert(&L, 1, e1);
    }
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT)
    for (i = 0; i < TEST_NUM; i++)
        ListInsert(&L, ListLength(L) + 1, *(e_add + i));
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT_P)
    e1 = (ElemType)malloc(sizeof(ET));
    e2 = (ElemType)malloc(sizeof(ET));

    for (i = 0; i < TEST_NUM; i++)
        ListInsert(&L, ListLength(L) + 1, (e_add + i));
#else	//缺省当做int处理
    for (i = 0; i < TEST_NUM; i++)
        ListInsert(&L, 1, 2);
#endif

    printf("插入后的表为：\n");
    ListTraverse(L, MyVisit);
    printf("空表=%s\n", (ListEmpty(L) == TRUE) ? "TRUE" : "FALSE");
    printf("表长=%d\n", ListLength(L));

#ifdef ELEMTYPE_IS_DOUBLE
    e1 = 2.0;
#elif defined (ELEMTYPE_IS_CHAR_ARRAY) || defined (ELEMTYPE_IS_CHAR_P)
    strcpy(e1, "test002");
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT)
    e1.num = 1001, e1.sex = 'M', e1.score = 76.5;
    strcpy(e1.addr, "上海市杨浦区");
    strcpy(e1.name, "张三");
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT_P)
    e1->num = 1001, e1->sex = 'M', e1->score = 76.5;
    strcpy(e1->addr, "上海市杨浦区");
    strcpy(e1->name, "张三");
#else	//缺省当做int处理
    e1 = 2;
#endif


    printf("\n按回车键删除表中和插入数据相同数据\n");
    while (1)
        if (getchar() == '\n')
            break;
    if (ListDelete2(&L, e1, MyCompare) == OK) {
#ifdef ELEMTYPE_IS_DOUBLE
        printf("删除元素=%5.1f成功\n", e1);
#elif defined (ELEMTYPE_IS_CHAR_ARRAY) || defined (ELEMTYPE_IS_CHAR_P)
        printf("删除元素=%s成功\n", e1);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT)
        printf("删除元素=\"%d.%s.%c.%f.%s\"成功\n", e1.num, e1.name, e1.sex, e1.score, e1.addr);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT_P)
        printf("删除元素=\"%d.%s.%c.%f.%s\"成功\n", e1->num, e1->name, e1->sex, e1->score, e1->addr);
#else	//缺省当做int处理
        printf("删除元素=%d成功\n", e1);
#endif
        printf("执行ListDelete2函数后，新表为：\n");
        ListTraverse(L, MyVisit);
        printf("空表=%s\n", (ListEmpty(L) == TRUE) ? "TRUE" : "FALSE");
        printf("表长=%d\n", ListLength(L));
    }
    else
#ifdef ELEMTYPE_IS_DOUBLE
        printf("删除元素=%5.1f失败\n", e1);
#elif defined (ELEMTYPE_IS_CHAR_ARRAY) || defined (ELEMTYPE_IS_CHAR_P)
        printf("删除元素=%s失败\n", e1);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT)
        printf("删除元素=\"%d.%s.%c.%f.%s\"失败\n", e1.num, e1.name, e1.sex, e1.score, e1.addr);
#elif defined (ELEMTYPE_IS_STRUCT_STUDENT_P)
        printf("删除元素=\"%d.%s.%c.%f.%s\"失败\n", e1->num, e1->name, e1->sex, e1->score, e1->addr);
#else	//缺省当做int处理
        printf("删除元素=%d失败\n", e1);
#endif
    printf("\n新函数-ListInsert2测试结束\n");
    printf("\n");

    printf("下面测试新函数-ClearList1 按回车键继续\n");
    while (1)
    {
        if (getchar() == '\n')
            break;
    }
    printf("\n清空表：\n");
    ClearList1(&L);
    printf("空表=%s\n", (ListEmpty(L) == TRUE) ? "TRUE" : "FALSE");
    printf("表长=%d\n", ListLength(L));
    printf("表分配大小=%d\n", L.listsize);

    printf("\n新函数-ClearList1测试结束\n");
    printf("\n");

    DestroyList(&L);

    return 0;
}