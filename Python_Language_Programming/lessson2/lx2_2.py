import lx2_1

def table_merge(li1, li2):
    for i in range(len(li1)):
        li1[i][0]= str(li1[i][0])
        student_id = str(li1[i][0])
        for j in li2:
            if str(j[0]) == str(student_id):
                li1[i] = j + li1[i][1:]
                break
    return li1

if __name__ == '__main__':
    title1,data1 = lx2_1.read_xls(0)
    title2,data2 = lx2_1.read_xls(1)
    print(table_merge(data1, data2))