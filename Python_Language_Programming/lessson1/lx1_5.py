import datetime

def cw():
    td = datetime.date.today()
    print(str(td))
    wd = td.weekday()
    print(str(wd))

    print(str(td.year)+'年'+str(td.month)+'月'+str(td.day)+'日')
    print('星期'+num_to_cn(td.weekday()))

def num_to_cn(n):
    if n == 6:
        return '天'
    elif n == 0:
        return '一'
    elif n == 1:
        return '二'
    elif n == 2:
        return '三'
    elif n == 3:
        return '四'
    elif n == 4:
        return '五'
    elif n == 5:
        return '六'

if __name__ == '__main__':
    cw()