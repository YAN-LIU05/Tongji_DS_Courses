import json
import xlrd

def read_xls(sh):
    workbook = xlrd.open_workbook('score.xls')
    worksheet = workbook.sheets()[sh]
    rows = worksheet.nrows
    title = worksheet.row_values(0)
    data = []
    for i in range(1, rows):
        row = worksheet.row_values(i)
        data.append(row)
    return title, data

def table_merge(li1, li2):
    for i in range(len(li1)):
        li1[i][0]= str(li1[i][0])
        student_id = str(li1[i][0])
        for j in li2:
            if str(j[0]) == str(student_id):
                li1[i] = j + li1[i][1:]
                break
    return li1

title1,data1 = read_xls(0)
title2,data2 = read_xls(1)
# 假设这是上次 table_merge 函数合并后的结果
merged_data = table_merge(data1, data2)



def merge_data_to_dict(merged_data):
    # 创建一个字典来存储合并后的数据
    students_dict = {}
    for entry in merged_data:
        student_id = entry[0].replace(".", "")  # 去掉学号中的小数点
        if student_id not in students_dict:
            students_dict[student_id] = {
                "学号": student_id,
                "姓名": entry[1],
                "英文姓名": entry[2],
                "性别": entry[3],
                "score": []
            }

        # 添加成绩信息，过滤掉空数据
        score_data = {key: value for key, value in zip(["学期", "英语","高程","物理", "高数","摄影"], entry[4:]) if value}
        students_dict[student_id]["score"].append(score_data)

    return list(students_dict.values())


def save_to_json_file(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=3)

if __name__ == '__main__':
    students_data = merge_data_to_dict(merged_data)
    save_to_json_file(students_data, 'course.txt')

