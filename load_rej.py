#!/usr/bin/python
# -*- coding: UTF-8 -*-

import re
import sys
import os
import utils
import getfunc
import config
#import gitpython

# 利用正则表达式将lines分段
def seg_split(buf_lines, reobj):
    segs=[]
    start=0
    index=0
    for l in buf_lines:
        #matchObj = re.match( r'diff a/(.*) b/(.*)\(rejected hunks\)', l, re.M|re.I)
        matchObj = reobj.match(l)
        if matchObj:
            #pc("debug","index={}".format(index))
            if start != index:
                segs.append(buf_lines[start:index])
            start = index
            #pc("debug","matchObj.group()  :{}".format(matchObj.group()))
            #pc("debug","matchObj.group(1) :{}".format(matchObj.group(1)))
            #pc("debug","matchObj.group(2) :{}".format(matchObj.group(2)))
        else:
            # print("No match!!")
            pass
        index += 1
    segs.append(buf_lines[start:])

    if len(segs) == 1:
        return -1, segs

    return 0, segs


# 提取hunk旧的部分
def split_old_context(hunk):
    oldlist = []
    for l in hunk:
        #print(l[0])
        if l[0] != '+':
            oldlist.append(l)
    #pc("info","oldlist={}".format(oldlist))
    return oldlist


# 提取hunk新的部分
def split_new_context(hunk):
    newlist = []
    for l in hunk:
        #print(l[0])
        if l[0] != '-':
            newlist.append(l)
    #pc("info","newlist={}".format(newlist))
    return newlist


class func:
    name = ""

class struct:
    name = ""

class define:
    name = ""

def get_line_abs(line):
    matchObj = re.search(r"#define\s+(.*)\s+(.*)", line, re.M)
    if matchObj:
        #utils.pc("info", "It's a #define")
        #utils.pc("debug","matchObj.group()  :{}".format(matchObj.group()))
        #utils.pc("debug","matchObj.group(1) :{}".format(matchObj.group(1)))
        #utils.pc("debug","matchObj.group(2) :{}".format(matchObj.group(2)))
        obj = define()
        define.name = matchObj.group(1)
        return obj
    else:
        # utils.pc("warn","No match!!")
        pass

    matchObj = re.search(r"#if\s+(.*)\s+(.*)", line, re.M)
    if matchObj:
        #utils.pc("info", "It's a #if")
        #utils.pc("debug","matchObj.group()  :{}".format(matchObj.group()))
        #utils.pc("debug","matchObj.group(1) :{}".format(matchObj.group(1)))
        #utils.pc("debug","matchObj.group(2) :{}".format(matchObj.group(2)))
        obj = define()
        define.name = matchObj.group(1)
        return obj
    else:
        # utils.pc("warn","No match!!")
        pass

    # function
    # matchObj = re.search(r"(\w+\s)+(\w+)\(", line, re.M)
    matchObj = re.match(r"(static\s*){0,1}(\w{1,})\s{1,}(\w{1,})\s*\([\s\w\*,]*\)?", line, re.M)
    if matchObj:
        utils.pc("info", "It's a func")
        utils.pc("debug","matchObj.group()  :{}".format(matchObj.group()))
        utils.pc("debug","matchObj.group(1) :{}".format(matchObj.group(1)))
        utils.pc("debug","matchObj.group(2) :{}".format(matchObj.group(2)))
        utils.pc("debug","matchObj.group(3) :{}".format(matchObj.group(3)))
        obj = func()
        obj.name = matchObj.group(3)
        return obj
    else:
        utils.pc("warn","Can't match one function!!")
        pass

    # struct
    matchObj = re.search(r"struct\s*(\w+)\s*{\s*", line, re.M)
    if matchObj:
        #utils.pc("info", "It's a struct")
        #utils.pc("debug","matchObj.group()  :{}".format(matchObj.group()))
        #utils.pc("debug","matchObj.group(1) :{}".format(matchObj.group(1)))
        obj = struct()
        obj.name = matchObj.group(1)
        return obj
    else:
        # utils.pc("warn","No match!!")
        pass

    # Unknow
    return None


class hunk_state:
    tag_name = ""
    tag_type = ""
    in_on_out = ""


def get_hunk_state(hunk, tagpath):
    tag_name = ""
    # 提取首行信息
    matchObj = re.search(r"@@ -(\d+),(\d+)\s\+(\d+),(\d+)\s@@\s(.*)", hunk[0], re.M)
    if matchObj:
        content = matchObj.group(5)
    else:
        utils.pc("error","First line is not start for hunk!!")
        return None

    # 第一行是函数
    obj = get_line_abs(content)
    if type(obj) == type(func()):
        tag_name = obj.name
        tag_type = "f"
        print("tag_name={}, tag_type={}".format(tag_name,tag_type))
        out = -1

        # 是否完整
        if hunk[0].strip()[-1] == ')':
            out = 0
        if hunk[0].strip()[0] == '{':
            out = 0
        if hunk[0].strip()[-1] == ';':
            out = 1
        if hunk[0].strip()[-1] == ',':
            out = -1
    else:
        pass

    for current_line in range(1, 4): 
        obj = get_line_abs(hunk[current_line])
        if type(obj) == type(func()):
            print("new function:", obj.name)
            tag_name = obj.name
            tag_type = "f"
            out = -1

            if hunk[current_line].strip()[-1] == ')':
                out = 0
            if hunk[current_line].strip()[-1] == ';':
                out = 1
            if hunk[current_line].strip()[-1] == ',':
                out = -1

        if obj == None:
            if hunk[current_line] == " {\n":
                out = 0
            if hunk[current_line] == " }\n":
                out = 1
            if hunk[current_line] == " ;\n":
                pass
            # if out == -1:
            #    if hunk[current_line].strip()[-1] == ';':
            #        out = 1
            #    out = 1

    # 函数已经匹配但是没有找到可以判定是内外的时候一般都在函数内
    if len(tag_name) and out == -1:
        out = 0
    if len(tag_name) > 0:
        utils.pc("info", "func = {}, out = {}".format(tag_name, out))
    else:
        utils.pc("info", "There is no function tag")

    if len(tag_name) > 0 and out == 0:
        state = hunk_state()
        state.tag_name = tag_name
        state.tag_type = 'f'
        state.in_on_out = out
        return state

        
def get_hunk_info1(hunk, tagpath):
    tag_type = ""
    flag_in_func = False
    func_name = ""
    is_declare = False
    is_define = False
    func_maybe = ""

    state = get_hunk_state(hunk, tagpath)
    if None != state and 0 == state.in_on_out:
        target_func = getfunc.extract_func(config.TARGET_TREE + tagpath, state.tag_name, state.tag_type)
        if target_func != None:
            fp = open(state.tag_name+"_target.txt", "w")
            fp.writelines(target_func)
            fp.close()
        else:
            return True

        patched_func = getfunc.extract_func(config.PATCHED_TREE + tagpath, state.tag_name, state.tag_type)
        if patched_func != None:
            fp = open(state.tag_name+"_refer.txt", "w")
            fp.writelines(patched_func)
            fp.close()
        else:
            return True

        #os.system('bcompare a.txt b.txt &')
        po = os.popen('diff {}_target.txt {}_refer.txt'.format(state.tag_name, state.tag_name))
        ret = po.read().split()
        if 0 == len(ret):
            return False
        else:
            return True

    # 如果没有找到函数, 默认保留该hunk
    return True



# change --> hunks
def hunk_split(buf_lines):
    reobj = re.compile(r'@@ -(\d+),(\d+) \+(\d+),(\d+) @@(.*)', re.M|re.I)
    ret, hunks= seg_split(buf_lines, reobj)

    file = hunks[0]
    # for h in hunks:
    #     pc("info", h)

    return file, hunks[1:]


# 重组patch
def re_construct_rej_file(path, head, body, tail):
    print(os.getcwd())
    print(path)
    print(head)
    print(body)
    print(tail)
    fp = open(path+'.re', "w")
    if None != head:
        for l in head:
            fp.write(l)

    if None != body:
        for l in body:
            fp.write(l)

    if None != tail:
        for l in tail:
            fp.write(l)

def load_rej(path):
    body_temp = []
    fp = open(path, "r")
    rejbuf = fp.readlines()
    fp.close()
    print("=======================")
    file, hunks = hunk_split(rejbuf) 
    print(file)
    matchObj = re.match( r'diff a/(.*)\sb/(.*)\t(.*)', file[0], re.M|re.I)
    if matchObj:
        utils.pc("debug", "old = {}, new = {}".format(matchObj.group(1), matchObj.group(2)))
        file_name = matchObj.group(2)
    if len(hunks) == 0:
        return -1
    body_temp.extend(file)
    print(file)
    for a in hunks:
        print("-----------------------")
        print(a)
        # 如果返回False说明这个hunk不要.
        if True == get_hunk_info1(a, file_name):
            body_temp.extend(a)

    print(body_temp)
    print("++++")
    re_construct_rej_file(os.path.abspath(path), None, body_temp, None)


if __name__ == "__main__":
    ret = os.path.splitext(sys.argv[1])[-1]
    print(ret)
    if ret == ".rej":
        load_rej(sys.argv[1])
