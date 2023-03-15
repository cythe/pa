#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import sys

fb_code = { "F":"3", "B":"4", }

color_code = {
        "none":"",
        "red":"1",
        "green":"2",
        "yellow":"3",
        "blue":"4",
        "purple":"5",
        "cyan":"6",
        "white":"7",
        "256":"8",
}

format_code = {
        "N":"0", # Normal
        "B":"1", # Bold
        "I":"3", # Italics
        "U":"4", # Underline
        "F":"5", # Flash
        "R":"7", # Revert
}

def get_format(level):
    format_str = "\033["
    format_list = level.split(',')

    control = format_list[0].strip().split('-')
    for c in control:
        t = format_code.get(c, "")
        if t != "":
            format_str += t
            format_str += ";"

    for index in range(1, len(format_list)):
        fc_or_bc = format_list[index].strip().split('-')
        forb = fb_code.get(fc_or_bc[0], "f")
        color = color_code.get(fc_or_bc[1], "")
        if color != "":
            if color == "8":
                format_str += forb
                format_str += color
                format_str += ";5;"
                format_str += fc_or_bc[2]
                format_str += ";"
            else:
                format_str += forb
                format_str += color
                format_str += ";"

    format_str = format_str[:-1]+'m'

    # print("{}test\033[m".format(format_str))
    return format_str


def pc(msg_format, msg, sep=' ', end='\n', file=sys.stdout, flush=False):

    if msg_format == "fatal" or msg_format == "FATAL":
        f = get_format("B-H,B-red")
        print("{}[FATAL]:{}\033[m".format(f, msg),end=end,flush=flush)
        return
    elif msg_format == "error" or msg_format == "ERROR":
        f = get_format("B-H,F-red")
        print("{}[ERROR]:{}\033[m".format(f, msg),end=end,flush=flush)
        return
    elif msg_format == "warn" or msg_format == "WARN":
        f = get_format("B-H,F-yellow")
        print("{}[WARN]:{}\033[m".format(f, msg),end=end,flush=flush)
        return
    elif msg_format == "info" or msg_format == "INFO":
        f = get_format("B-H,F-green")
        print("{}[INFO]:{}\033[m".format(f, msg),end=end,flush=flush)
        return
    elif msg_format == "debug" or msg_format == "DEBUG":
        f = get_format("B-H,F-blue")
        print("{}[DEBUG]:{}\033[m".format(f, msg),end=end,flush=flush)
        return
    else:
        f = get_format(msg_format)
        if f == "":
            print("[NONE]: {}\033[m".format(msg),end=end,flush=flush)
        else:
            print("{}{}\033[m".format(f, msg),end=end,flush=flush)


# # # # # Test code # # # # # Test code # # # # # Test code # # # # #
#def test():
#    pc("","=====================")
#    pc("FATAL", "FATAL")
#    pc("ERROR","ERROR")
#    pc("WARN","WARN")
#    pc("INFO","INFO")
#    pc("DEBUG","DEBUG")
#    pc("","=====================")
#    pc("fatal", "fatal")
#    pc("error","error")
#    pc("warn","warn")
#    pc("info","info")
#    pc("debug","debug")
#    pc("","=====================")
#    pc("","[NONE]")
#    pc("I-U-B, F-256-32, B-256-42", "I-U-B, F-256-32, B-256-42")
#    pc("U-Z, F-256-128, B-256-38", "U-Z, F-256-128, B-256-38")
#    pc("H-I-U-B-R, F-yellow, B-blue", "H-I-U-B-R, F-yellow, B-blue")
#
# test()

def get_ttywidth():
    po = os.popen('stty size')
    ret = po.read().split()
    return int(ret[1])

def strsplit(string, width):
    l=[]
    length = len(string)
    for i in range(0, length, width):
        l.append(string[i:i+width])
    return l

def str_ex_tabs(lst):
    new = []
    for l in lst:
        new.append(l.expandtabs(tabsize=4).replace("\n", " "))
    return new


def p_diff(oldl, newl, tty_width):
    limit = int((tty_width-4)/2)
    index = 0 
    s1 = []
    s2 = []
    old = str_ex_tabs(oldl)
    new = str_ex_tabs(newl)
    # 缺行补全
    lines = max(len(old), len(new)) 
    for i in range(lines):
        if i >= len(old):
            old.append("i>old".center(limit, '-'));
        if i >= len(new):
            new.append("i>new".center(limit, '-'));
        if old[i][0] != '-' and new[i][0] != '+':
            pass
        elif old[i][0] == '-' and new[i][0] == '+':
            pass
        elif old[i][0] != '-' and new[i][0] == '+':
            old.insert(i, "".ljust(len(new[i]), ' ')); 
        elif old[i][0] == '-' and new[i][0] != '+':
            new.insert(i, "".ljust(len(old[i]), ' ')); 
    # 长度限制
    for i in range(lines):
        s1 += strsplit(old[i], limit)
        s2 += strsplit(new[i], limit)
    # 依次打印
    pc("info", " The old context ".center(limit, '=') + "  | " + " The new context ".center(limit, '='))
    lines = max(len(s1), len(s2))
    mines = min(len(s1), len(s2))
    for i in range(lines):
        if s1[i] == s2[i]:
            pc("info2", s1[i].ljust(limit) + "  | " + s2[i].ljust(limit))
        else:
            pc("red", s1[i].ljust(limit) + "  | " + s2[i].ljust(limit))

    pc("info", "  END  ".center(tty_width, '='))
