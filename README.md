## 工作流程flow

<filter> --> <patch> --无冲突--> done(万事大吉)
                     --有冲突--> [查看rej文件] -- 需要应用 --> 解决冲突 --> <continue>
                                               --不需要应用 -> <drop>
                                               ---- 未知 ----> <reserve>

这里假设SDK_patchdir为: patches.sdk12.2402-2405


#### filter用法

`./filter <SDK_patchdir>`

经过filter之后会分为两部分. patches.todo是需要我们处理的patch, patches.drop是不需要的patch.


#### patch命令用法

`./patch [patch_path]`
将patch_path指向的patch文件应用到当前git tree上.

`./patch`
遍历patches.todo文件夹, 一个一个应用到当前git tree上. 遇到冲突显示git status和patch文件信息

`./patch <num>`
将patches.todo文件夹中的前num个patch应用到当前git tree上, 有冲突会退出, 不会记录进度.
