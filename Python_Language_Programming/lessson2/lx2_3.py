import lx2_1
import lx2_2

def query_by_no(studenet_no):
    title1, data1 = lx2_1.read_xls(0)
    title2, data2 = lx2_1.read_xls(1)
    li = lx2_2.table_merge(data1, data2)
    result = []
    for i in li:
        if i[0] == studenet_no:
            result.append(i)
    title = title2 + title1[1:]
    mydict = dict(zip(title, result[0]))
    return mydict

if __name__ == '__main__':
    print(query_by_no('2352018'))