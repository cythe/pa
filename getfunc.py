# -*- coding: utf8 -*-
import re

def printfunc(src_buf, s_index):
    SYMBOLS = {'}': '{'}
    SYMBOLS_L, SYMBOLS_R = SYMBOLS.values(), SYMBOLS.keys()
    t = s_index + 1
    arr = []
    for l in src_buf[s_index:]:
        for c in l:
            if c in SYMBOLS_L:
                arr.append(c)
            elif c in SYMBOLS_R:
                if arr and arr[-1] == SYMBOLS[c]:
                    arr.pop()
                    # arr 从0 -> n -> 0 表示匹配完成
                    if len(arr) == 0:
                        print(src_buf[s_index:t])
                        return s_index, t;
                else:
                    print("括号匹配失败!")
                    return -1,-1
        t = t + 1

    print("终于等到你, 这个bug!!!")
    print(src_buf[s_index:])
    return -1,-1


tags_buf = open("tags", "r").read().split('\n')
print(tags_buf)
print("-----------")

ret = []
for l in tags_buf:
    if -1 != l.find("add") :
        t = l.split('\t')
        print(t)
        ret.append(t)
print("len(ret) = {}".format(len(ret)))
if len(ret) > 1:
    for i in range(len(ret)):
        print("{}:{}".format(i+1, ret[i]))
    ch = int(input("select your ch (1 ~ {})".format(len(ret)))) - 1
else:
    ch = 0

sym = ret[ch][0]
fn = ret[ch][1] 
how = ret[ch][2]
symtype = ret[ch][3]
#if symtype == 'f':
searchObj = re.search( r'/\^(.*)\$/;"', how)
if searchObj:
    print("searchObj.group() : {}".format(searchObj.group()))
    print("searchObj.group(1) : {}".format(searchObj.group(1)))
else:
    print("Nothing found!!")
src_buf = open(fn, "r").read().split('\n')
for j in src_buf:
    if j == searchObj.group(1):
        index = src_buf.index(j)
printfunc(src_buf, index)

