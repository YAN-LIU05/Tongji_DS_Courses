/* 2352018 信06 刘彦 */

/* 允许按需加入系统的宏定义、需要的头文件等 */
#include <iostream>
#include "read_stulist.h"
#include <iomanip>
#include <fstream>
using namespace std;

#define MAX_FILENAME_LEN		512	//定义文件名的最大长度
#define LENGTH 60
#define MAX_STUDENT_NUM 10000

/* stu_metge 类存放每个学生的信息，包括学号、姓名、其它需要的私有信息，已有内容不准动，可加入符合限制要求的新内容 */
class stu_list;
class stu_merge {
private:
	int  stu_no;					//学号 
	char stu_name[MAX_NAME_LEN];  //姓名
	int statue;
	friend stu_list;
	/* 允许按需加入private数据成员、成员函数以及其它需要的内容 */

public:
	//本类不允许定义任何的公有数据成员及成员函数
};

/* stu_list 类整个选课信息，已有内容不准动，可加入符合限制要求的新内容 */
class stu_list {
private:
	student list_round_1[MAX_STU_NUM];	//第一轮选课的学生名单（不排序、不去重）
	int list_num_1;						//第一轮选课的学生人数

	student list_round_2[MAX_STU_NUM];	//第二轮选课的学生名单（不排序、不去重）
	int list_num_2;						//第二轮选课的学生人数

	stu_merge list_merge[MAX_STU_NUM];	//合并后的学生名单（去重，按升序排列）
	int list_merge_num;					//合并后的学生人数（目前不打印，但可用于内部管理，如果不需要，也不要删除）

	/* 允许按需加入private数据成员和成员函数
	   注意，不允许加入array / set / map / vector等STL容器 */

public:
	stu_list();										//构造函数，按需完成初始化功能，如果不需要，保留空函数即可
	int read(const char* filename, const int round);	//从文件中读入选课信息，round为1/2，表示选课轮次
	int print(const char* prompt = NULL);				//打印最终的选课名单

	void handle_data(int choice);
	void handle_check();
	void handle_order();
	void handle_change1(stu_merge* a1, stu_merge* a2);
	void handle_change2(stu_merge* a1, stu_merge* a2);
	void bubbleSort(student list[], int count);
	void remove_repeat(student list[], int& count);

	char* tj_strcpy(char* s1, const char* s2)
	{
		if (s1 == NULL)
		{
			return s1;
		}

		char* s = s1;

		if (s2 == NULL)
		{
			*s = '\0';
		}
		else
		{
			for (; *s2 != '\0'; s++, s2++)
			{
				*s = *s2;
			}
			*s = '\0';
		}

		return s1;
	}
	int tj_strlen(const char* str)
	{
		/* 注意：函数内不允许定义任何形式的数组（包括静态数组） */
		int length = 0;
		if (str == NULL)
		{
			return 0;
		}

		while (*str != '\0')
		{
			length++;
			str++;
		}

		return length;
	}


	
	/* 允许按需加入其它public成员函数（提示：合并、去重、排序等）
	   不允许定义公有的数据成员
	   不允许在成员函数中使用array / set / map / vector等STL容器 */

};


// 冒泡排序函数
void stu_list::bubbleSort(student list[], int count)
{
	for (int i = 0; i < count - 1; i++) 
	{
		for (int j = 0; j < count - i - 1; j++) 
		{
			if (list[j].no > list[j + 1].no) 
			{
				int tempNo = list[j].no;
				char tempName[MAX_NAME_LEN];
				tj_strcpy(tempName, list[j].name);

				list[j].no = list[j + 1].no;
				tj_strcpy(list[j].name, list[j + 1].name);

				list[j + 1].no = tempNo;
				tj_strcpy(list[j + 1].name, tempName);
			}
		}
	}
}

// 去重函数
void stu_list::remove_repeat(student list[], int& count) 
{
	for (int i = 0; i < count - 1;) 
	{
		if (list[i].no == list[i + 1].no) 
		{
			// 移动覆盖重复项
			for (int k = i + 1; k < count - 1; k++) 
			{
				list[k] = list[k + 1];
			}
			count--; // 更新计数
		}
		else 
		{
			i++;
		}
	}
}

void stu_list::handle_data(int choice)
{

	// 根据 choice 执行不同的排序操作
	if (choice == 1)
	{
		bubbleSort(list_round_1, list_num_1);
	}
	else if (choice == 2)
	{
		bubbleSort(list_round_2, list_num_2);
	}

	// 根据 choice 执行不同的去重操作
	if (choice == 1)
	{
		remove_repeat(list_round_1, list_num_1);
	}
	else if (choice == 2)
	{
		remove_repeat(list_round_2, list_num_2);
	}
}

void stu_list::handle_change1(stu_merge* a1, stu_merge* a2)
{
	int temp = a1->stu_no;
	a1->stu_no = a2->stu_no;
	a2->stu_no = temp;;
}

void stu_list::handle_change2(stu_merge* a1, stu_merge* a2)
{
	int temp = a1->statue;
	a1->statue = a2->statue;
	a2->statue = temp;;
}

void stu_list::handle_order()
{
	int i, j;
	char temp_name[MAX_NAME_LEN];

	for (i = 0; i < list_merge_num - 1; i++)
	{
		for (j = 0; j < list_merge_num - i - 1; j++)
		{
			if (list_merge[j].stu_no > list_merge[j + 1].stu_no)
			{
				// 交换学号
				stu_list::handle_change1(&list_merge[j], &list_merge[j + 1]);

				// 交换姓名
				tj_strcpy(temp_name, list_merge[j + 1].stu_name);
				tj_strcpy(list_merge[j + 1].stu_name, list_merge[j].stu_name);
				tj_strcpy(list_merge[j].stu_name, temp_name);
				// 交换状态
				stu_list::handle_change2(&list_merge[j], &list_merge[j + 1]);
			}
		}
	}
}


void stu_list::handle_check()
{
	int i, j;
	for (i = 0; i < list_num_1; i++)
	{
		list_merge[i].stu_no = list_round_1[i].no;
		list_merge[i].statue = 0;
		for (j = 0; j < tj_strlen(list_round_1[i].name) + 1; j++) 
		{
			list_merge[i].stu_name[j] = list_round_1[i].name[j];
		}
	}
	list_merge_num = list_num_1;


	for (i = 0; i < list_num_2; i++)
	{
		int round_num = 0;
		for (j = 0; j < list_num_1; j++)
		{
			if (list_merge[j].stu_no == list_round_2[i].no)
			{
				round_num = 1;
				list_merge[j].statue = 1;
				break;
			}
		}
		if (round_num == 0)
		{
			if (list_merge_num < MAX_STUDENT_NUM) 
			{
				list_merge[list_merge_num].stu_no = list_round_2[i].no;
				list_merge[list_merge_num].statue = 2;
				for (j = 0; list_round_2[i].name[j] != '\0'; j++)
				{
					list_merge[list_merge_num].stu_name[j] = list_round_2[i].name[j];
				}
				list_merge[list_merge_num].stu_name[j] = '\0'; // 确保字符串以 '\0' 结尾
				list_merge_num++;
			}
		}
	}
}

/***************************************************************************
  函数名称：
  功    能：从文件中读入选课信息，round为1/2，表示选课轮次
  输入参数：
  返 回 值：
  说    明：构造函数，按需完成初始化功能，如果不需要，保留空函数即可
***************************************************************************/
stu_list::stu_list()
{
	for (int i = 0; i < MAX_STU_NUM; i++)
	{
		list_merge[i].stu_no = 0;
		list_merge[i].statue = 0;
		list_round_1[i].no = 0;
		list_round_2[i].no = 0;
	}
	list_num_1 = 0;
	list_num_2 = 0;
	list_merge_num = 0;
}




/***************************************************************************
  函数名称：
  功    能：演示静态链接库的使用，本函数中调用静态链接库中的预置函数
  输入参数：
  返 回 值：
  说    明：本函数不需要修改
***************************************************************************/
int stu_list::read(const char* filename, const int round)
{
	int ret = 0;
	/* 读取第1/2轮的选课名单并打印 */
	switch (round) {
		case 1:
			this->list_num_1 = read_stulist(filename, this->list_round_1, MAX_STU_NUM);
			if (this->list_num_1 > 0)
				print_stulist("第一轮选课名单：", this->list_round_1, this->list_num_1);
			else
				ret = -1;
			break;
		case 2:
			this->list_num_2 = read_stulist(filename, this->list_round_2, MAX_STU_NUM);
			if (this->list_num_2 > 0)
				print_stulist("第二轮选课名单：", this->list_round_2, this->list_num_2);
			else
				ret = -1;
			break;
		default:
			ret = -1;
			break;
	}
	return ret;
}


/***************************************************************************
  函数名称：
  功    能：
  输入参数：
  返 回 值：
  说    明：打印最终的选课名单
***************************************************************************/
int stu_list::print(const char* t)
{
	cout << t << endl;
		for (int i = 0; i < LENGTH; i++)
			cout << "=";
		cout << endl;
		cout << "序号 学号     姓名";
		for (int i = 0; i < 28; i++)
			cout << " ";
		cout << "第一轮 第二轮" << endl;
		for (int i = 0; i < LENGTH; i++)
			cout << "=";
		cout << endl;
		for (int i = 0; list_merge[i].stu_no > 0; i++)
		{
			cout << setiosflags(ios::left);
			cout << setw(4) << i + 1; // 序号
			if (list_merge[i].stu_no == '\0')
			{ 
				cout << " " << "  "; 
			}
			else {
				cout << " " << list_merge[i].stu_no;
			}
			cout << "  " << setw(32) << list_merge[i].stu_name; 
	
			switch (list_merge[i].statue)
			{
				case 1:
					cout << "Y      Y";
					break;
				case 0:
					cout << "Y      退课";
					break;
				default:
					cout << "/      补选";
			}
			
			cout << endl;
	
		}
		for (int i = 0; i < LENGTH; i++)
			cout << "=";
		cout << endl;
		return 0;
}

/***************************************************************************
  函数名称：
  功    能：
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
int main(int argc, char** argv)
{
	char file1[MAX_FILENAME_LEN], file2[MAX_FILENAME_LEN];

	cout << "请输入前一轮选课的数据文件 : ";
	gets_s(file1); //cin不能读有空格的文件

	cout << "请输入后一轮选课的数据文件 : ";
	gets_s(file2);

	stu_list list;

	/* 读入数据 */
	if (list.read(file1, 1) < 0)
		return -1;
	if (list.read(file2, 2) < 0)
		return -1;

	/* 处理数据 */
	// 合并第一\二轮名单
	list.handle_data(1);
	list.handle_data(2);

	// 检查轮次
	list.handle_check();

	//列表排序
	list.handle_order();

	/* 打印 */
	list.print("最终选课名单");

	return 0;
}

