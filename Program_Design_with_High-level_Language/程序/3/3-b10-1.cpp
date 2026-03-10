/* 2352018 信06 刘彦 */
#include <iostream>
#include <iomanip>
#include <cstdio>
#include <windows.h> //取系统时间
using namespace std;

int main()
{
	LARGE_INTEGER tick, begin, end;

	QueryPerformanceFrequency(&tick);	//获得计数器频率
	QueryPerformanceCounter(&begin);	//获得初始硬件计数器计数

	int g1, g2, g3, s1, s2, s3, b1, b2, b3;   //个位、十位、百位
	int x, y, z, i;
	i = 0;
	for (b1 = 1; b1 < 10; b1++) 
	{
		for (s1 = 1; s1 < 10; s1++) 
		{
			for (g1 = 1; g1 < 10; g1++) 
			{
				if (b1 != s1 && b1 != g1 && s1 != g1) 
				{
					x = 100 * b1 + 10 * s1 + g1;   
					/*以上为第1个三位数*/
					for (b2 = 1; b2 < 10; b2++) 
					{
						if (b2 != b1 && b2 != s1 && b2 != g1) 
						{
							for (s2 = 1; s2 < 10; s2++) 
							{
								if (s2 != b1 && s2 != b2 && s2 != s1 && s2 != g1) 
								{
									for (g2 = 1; g2 < 10; g2++)
									{
										if (g2 != b1 && g2 != b2 && g2 != s1 && g2 != s2 && g2 != g1)
										{
											y = 100 * b2 + 10 * s2 + g2;
											/*以上为第2个三位数*/
											for (b3 = 1; b3 < 10; b3++)
											{
												if (b3 != b1 && b3 != b2 && b3 != s1 && b3 != s2 && b3 != g1 && b3 != g2)
												{
													for (s3 = 1; s3 < 10; s3++)
													{
														if (s3 != b1 && s3 != b2 && s3 != b3 && s3 != s1 && s3 != s2 && s3 != g1 && s3 != g2)
														{
															for (g3 = 1; g3 < 10; g3++)
															{
																if (g3 != b1 && g3 != b2 && g3 != b3 && g3 != s1 && g3 != s2 && g3 != s3 && g3 != g1 && g3 != g2)
																{
																	z = 100 * b3 + 10 * s3 + g3;
																	/*以上为第3个三位数*/
																	if (x + y + z == 1953)
																	{
																		if (x < y && y < z)
																		{
																			i++;
																			cout << setiosflags(ios::right);
																			cout << "No." << setw(3) << i << " : " << x << "+" << y << "+" << z << "=" << "1953" << endl;
																		}
																	}
																}
															}
														}
													}
												}
											}
										}
									}
								}
							}
						}
					}
				}
			}
		}
	}
	cout << "total=" << i << endl;

	QueryPerformanceCounter(&end);		//获得终止硬件计数器计数

	cout << "计数器频率 : " << tick.QuadPart << "Hz" << endl;
	cout << "计数器计数 : " << end.QuadPart - begin.QuadPart << endl;
	cout << setiosflags(ios::fixed) << setprecision(6) << double(end.QuadPart - begin.QuadPart) / tick.QuadPart << "秒" << endl;

	return 0;
}