import re
import os
import sys

same=sys.argv[1]
#source=os.path.splitext(same)[0:-1][0]
source=sys.argv[2]
print("OP: {} and {}".format(source, same))
#same = '0001-hwrng-cn10k-Add-random-number-generator-support.patch.same'

src_hunks = []
same_hunks = []

# 利用正则表达式将lines分段
def seg_split(buf_lines, reobj):
    segs=[]
    start=0
    index=0
    for l in buf_lines:
        matchObj = reobj.match(l)
        if matchObj:
            #pc("debug","index={}".format(index))
            if start != index:
                segs.append(buf_lines[start:index])
            start = index
        index += 1
    segs.append(buf_lines[start:])

    if len(segs) == 1:
        return -1, segs

    return 0, segs


# 掐头
def cut_head(buf_lines):
    head = []
    body = []
    reobj = re.compile(r'diff --git a/(.*)\sb/(.*)', re.M|re.I)
    ret, segs = seg_split(buf_lines, reobj)
    head = segs[0]
    for l in segs[1:]:
        body.extend(l)

    return head, body


# 去尾
def cut_tail(buf_lines):
    reobj = re.compile(r'--\s\n', re.M|re.I)
    ret, segs = seg_split(buf_lines, reobj)
    body = segs[0]
    tail = segs[1]

    return tail, body


# patch --> changes
def change_split(buf_lines):
    reobj = re.compile(r'diff --git a/(.*)\sb/(.*)', re.M|re.I)
    ret, changes = seg_split(buf_lines, reobj)
    return changes


# change --> hunks
def hunk_split(buf_lines):
    reobj = re.compile(r'@@ -(\d+),(\d+) \+(\d+),(\d+) @@(.*)', re.M|re.I)
    ret, hunks= seg_split(buf_lines, reobj)

    file = hunks[0]

    return file, hunks[1:]


def load_hunks_from_patch(path):
    fp = open(path, "r")
    patchbuf = fp.readlines()
    fp.close()
        
    _head, body = cut_head(patchbuf)
    _tail, body = cut_tail(body)
            
    for f in (change_split(body)):
        _file, hunks = hunk_split(f)
        ret = os.path.splitext(path)[-1]
        for h in hunks:
            if ret == '.same':
                same_hunks.append(h)
            else:
                src_hunks.append(h)


def is_same(h1,h2):
    fp = open('h1.txt', 'w')
    for i in range(1, len(h1)):
        fp.write(h1[i])
    fp.close()

    fp = open('h2.txt', 'w')
    for i in range(1, len(h2)):
        fp.write(h2[i])
    fp.close()

    po = os.popen('diff h1.txt h2.txt')
    ret = po.read().split()
    if 0 == len(ret):
        return True
    else:
        return False

    
load_hunks_from_patch(source)
load_hunks_from_patch(same)

if len(same_hunks) != len(src_hunks):
    print("I can't deal with {} because of hunks NUM is not same...".format(source))
    print("same: {} src: {} ".format(len(same_hunks), len(src_hunks)))
    os.system('bcompare {} {}'.format(source, same))
    choice = input("Are these two patches the same?? [y|N]: ")
    if choice == 'y':
        print("Manual: {} == {}".format(source, same))
        exit(0)
    else:
        exit(2)

for i in range(0,len(src_hunks)):
    if not is_same(src_hunks[i], same_hunks[i]):
        print("There are diff hunks in this patch, please check if you delete {} by mistake..".format(source))
        os.system('bcompare h1.txt h2.txt')
        choice = input("Are these two hunks the same?? [y|N]: ")
        if choice == 'y':
            pass
        else:
            exit(1)

print("Auto: {} == {}".format(source, same))
exit(0)
