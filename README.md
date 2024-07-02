## 初始化PA

`. <PA_DIR>/pa.init`


## 工作流程flow

<filter> --> <apply> --无冲突--> done(万事大吉)
                     --有冲突--> [查看rej文件] -- 需要应用 --> 解决冲突 --> <goahead>
                                               --不需要应用 -> <drop>
                                               ---- 未知 ----> <reserve>


#### filter用法

这里假设SDK_patchdir为: patches.sdk12.2402-2405

`./filter <SDK_patchdir>`

经过filter之后会分为两部分. patches.todo是需要我们处理的patch, patches.drop是不需要的patch.


#### apply命令用法

`./apply [patch_path]`
将patch_path指向的patch文件应用到当前git tree上.

`./apply`
遍历patches.todo文件夹, 一个一个应用到当前git tree上. 遇到冲突显示git status和patch文件信息

`./apply <num>`
将patches.todo文件夹中的前num个patch应用到当前git tree上, 有冲突会退出, 不会记录进度.

