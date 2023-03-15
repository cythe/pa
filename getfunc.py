# -*- coding: utf8 -*-
import re
import os
import utils
import time

def get_one_func(src_buf, s_index):
    func_content = []
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
                        #print(src_buf[s_index:t])
                        func_content.extend(src_buf[s_index:t])
                        return func_content
                else:
                    print("括号匹配失败!")
                    return func_content
        t = t + 1

    print("终于等到你, 这个bug!!!")
    # print(src_buf[s_index:])
    return func_content


def find_tag(target_tag):
    tags_buf = open("tags", "r").read().split('\n')
    print("TARGET_FUNC: {}".format(target_tag))
    tags = []
    for l in tags_buf:
        matchObj = re.search("^{}\s+(.*)".format(target_tag), l, re.M)
        if matchObj:
            #utils.pc("debug","matchObj.group()  :{}".format(matchObj.group()))
            #utils.pc("debug","matchObj.group(1) :{}".format(matchObj.group(1)))
            t = l.split('\t')
            print(l)
            tags.append(t)
        else:
            # utils.pc("warn","No match!!")
            pass
    utils.pc("info", "Found follow tags:")
    for l in tags:
        utils.pc("info", l)
    return tags


def extract_func(file_path, target_tag, tag_type):
    src_tree = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    current_path = os.getcwd()
    os.chdir(src_tree)

    ret = os.popen('rm -f tags').read()
    ret = os.popen('ctags ' + file_name).read()
    time.sleep(1)

    tags = find_tag(target_tag)
    if len(tags) == 0:
        ret = os.popen('rm -f tags').read()
        ret = os.popen('ctags -R .').read()
        time.sleep(1)
        tags = find_tag(target_tag)

    if len(tags) == 0:
        utils.pc("error", "Can't find tag for func <{}>".format(target_tag))
        os.chdir(current_path)
        return None

    if len(tags) > 1:
        for i in range(len(tags)):
            print("{}:{}".format(i+1, tags[i]))
        ch = int(input("Please select a tag index (1 ~ {})".format(len(tags)))) - 1
    elif len(tags) == 1:
        ch = 0
    
    sym = tags[ch][0]
    fn = tags[ch][1]
    how = tags[ch][2]
    symtype = tags[ch][3]
    print(symtype, tag_type)
    if symtype == tag_type:
        searchObj = re.search( r'/\^(.*)\$/;"', how)
        if searchObj:
            #print("searchObj.group() : {}".format(searchObj.group()))
            #print("searchObj.group(1) : {}".format(searchObj.group(1)))
            target_line = searchObj.group(1)
        else:
            # 一般这儿不出错吧...
            utils.pc("error", "Can't find target line for tag <{}>!!".format(target_tag))
            os.chdir(current_path)
            return None
        # 寻找tag所在的位置
        src_buf = open(fn, "r").readlines()
        for j in src_buf:
            if j.strip() == target_line:
                index = src_buf.index(j)
        os.chdir(current_path)
        return get_one_func(src_buf, index)
    else:
        os.chdir(current_path)
        utils.pc("error", "Can't find type [{}] for tag <{}>".format(tag_type,target_tag))
        return None

