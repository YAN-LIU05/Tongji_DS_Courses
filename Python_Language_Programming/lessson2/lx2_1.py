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

if __name__ == '__main__':
    title, data = read_xls(0)
    print(title)
    print(data)
    title, data = read_xls(1)
    print(title)
    print(data)