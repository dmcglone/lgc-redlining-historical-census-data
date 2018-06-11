import string


def tract_code_to_fips(tract_code):
    def y(a):
        if len(a) == 0:
            return '0'
        x = (len(a) - 1) * 26
        y = string.ascii_lowercase.index(a.lower()[-1]) + 1
        return str(x + y)

    cc = tract_code.split('-')
    a = '42101'
    b = cc[0].rjust(3, '0')
    c = y(cc[1]).rjust(2, '0').ljust(5, '0')
    return a + b + c
