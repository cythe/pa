## 背景介绍

Vender更新SDK的同时会向kernel mainline推一部分patch, 也会从mainline中backport一部分patch.
这就造成了SDK patch中的依赖和冲突, 有的patch不用打, 有的patch只应用了一部分.

在拿patch的时候冲突频繁, 前3/4几乎每个patch都会有大大小小的冲突, 有些明显可以不需要我们比对的冲突我们希望可以通过pa(patch assistant)来解决. 

>  我不知道这个东西对我们具体能提高多少生产力, 可能大家有自己的一套方案, 也可能只有我碰到了这么多冲突...
>  如果有任何建议, 我们多交流.

## 概念和策略

* 源tree: SDK kernel --> marvell/...
		是我们获取patch的地方, 如果第一次做某个bsp, 一般会将该tree作为参考tree.
* 目标tree: 5.15_base --> yocto/v5.15/standard/.../`<bsp>`
		是我们需要打patch的地方.
* 参考tree: 已经打完patch的上一个版本 --> yocto/5.10/standard/.../`<bsp>`
		可能是源tree, 也可能是我们发布的上一个版本, 是hunk分析模块参考的tree.

策略只有一条:
		目标tree中与参考tree高相似度的代码块, 该代码块相关的hunk不需要apply.

当前比较原则: 
		忽略空白符后, 目标tree和参考tree完全一致, 则该部分代码判定为一致. (从严)


## 复习??

#### patch结构

```
    patch {
        head : string		        // patch描述,作者,commitlog, 文件更改情况
        
        body : {
    	    changes {		        // 文件的更改
		        file: string ( oldfile,  newfile )
		        hunks = []	        // 更改某个文件的补丁们
    	    }
        }
        
        tail : string		        // 补丁之后的其他信息.
    }
```

#### 传统patch流程

am --> apply --> deal rej --> add --> am continue/skip (命令敲不少)
`git am *.patch`  (该过程需要all_in_once, 中间出现错误后没有后悔药)

#### hunk做什么?

source文件中改什么呢?
* 函数内  增删改 (一般都是语句更改)
* 结构体  增删改 (成员变量)
* 函数和结构体外  增删改 (全局, 宏, 声明)
* 添加/删除  整个函数/结构体
* 添加/删除  整个文件

#### 功能拟定

1. 流程优化 (flow)
2. 判断增删改的位置
    C语言的代码块使用{}来分割
    函数内/函数外 / 数据结构内/数据结构外
3. 遇见连续增/减函数 连续增/减结构体
    已有/删结构体 已有/删函数 不管
4. hunk是否保留
    还在原状态/状态变了?
5. \* hunk内部分part, a干嘛, b干嘛, c干嘛...

## 程序运行过程(work flow)

* [x] [patch filter]
> 对要打的一堆patch进行filter过滤, 如果提交的commit log相似, 则进一步比较内容是否一致, 这里调用外部应用beyond compare, 也可以用vimdiff/meld... 
> 这个过程要过滤掉那种文本或功能相似度超过95%的patch.

note: 
```
1. 需要人工干预, 有些不同的patch用了相同的commit subject, 需要遍历来处理
2. 后续可以先扫描并保存结果, 等扫描完成后对每个需要进行比较的patch进行统一处理.
3. 如果全自动, 则需要将hunk部分提取出来, 忽略无关信息, 直接得出结果.
PS: 感谢ZhanTao的技术支持, 查询速度提升巨大.
```

* [x] [other flow]: `patch` `rejclean` `update` `drop` `reserve`

	patch: 依次对内核目录中patch进行处理, 如果遇到冲突则停止.
	rej_loader: 对冲突文件执行分析, 用户处理冲突.
	rejclean: 冲突解决完成清除 .rej 文件.
	update/reserve/drop: 将当前patch移动到[over/reserve/drop]文件夹中.

## 冲突处理方案

#### 对rej进行过滤

[] [rej_loader]: apply --reject 之后提取rej中的hunk, 比较参考tree和目标tree的函数内容, 如果一致, 则删除这个hunk

1. 获取所有.rej路径 (当前需手工载入, `./rej_loader <path_to_rej>`)

	* [x] 生成ctags的路径集 --> list
	
	> 获取函数所在目录的路径 (将tags文件数目限制在一定范围, 避免对整个kernel生成tags文件) 
	
2. * [x] 获取要比对的函数名称. --> list

3. * [x] 比对当前源码函数和patch打完后函数差别, 完全一致则无必要更改, 删除该hunk. --> file write back

note: 
1. 理想状态是不需要人工干预, 目前测试发现应该进行人工干预, 避免算法导致的问题.
2. 这一步应该需要生成一个更改注释, 暂时没有想好怎么做.

[patch over]:
1. 对patch的更改进行注释 (自动生成).
2. 执行bisect.sh脚本, 对patches进行编译验证 (目前如果遇到更改Kconfig的patch, 会等待用户进行选择, allyesconfig每次编译量和链接过程比较慢, 所以最后进行这一步的编译验证).

[Todo]

* [ ] 宏定义
* [ ] 全局变量
* [ ] 局部变量
* [x] 需要做个工具只比较hunk内容, 忽略无关信息, 直接得出结果. (check_same.py)
* [ ] [patch applier]: 打patch的过程(am/apply), 调用gitpython.
    		这个模块覆盖当路径不存在或路径改变的时候无法生成.rej文件的情形, 并且将替代原有的flow.
