#!python3
# -*- coding:utf-8 -*-
import sys
import time

import uiautomation as auto


def usage():
    auto.Logger.ColorfullyWrite("""usage
<Color=Cyan>-h</Color>      show命令<Color=Cyan>help</Color>
<Color=Cyan>-t</Color>      延迟<Color=Cyan>时间</Color>, 默认为3秒，在值秒后开始枚举，这必须是一个整数
        您可以延迟几秒钟并使窗口处于活动状态，这样自动化就可以枚举活动窗口
<Color=Cyan>-d</Color>      枚举树 <Color=Cyan>depth</Color>, 这必须是一个整数，如果为null，则枚举整个树
<Color=Cyan>-r</Color>      枚举自 <Color=Cyan>root</Color>:桌面窗口，如果为空，则从前台窗口枚举
<Color=Cyan>-f</Color>      枚举自<Color=Cyan>专注的</Color> 控件，如果为null，则从前台窗口枚举
<Color=Cyan>-c</Color>      枚举控件under <Color=Cyan>光标</Color>, 如果depth＜0，则从其祖先一直枚举到depth
<Color=Cyan>-a</Color>      show <Color=Cyan>祖先</Color>光标下控件的
<Color=Cyan>-n</Color>      显示控件已满 <Color=Cyan>name</Color>, 如果为null，则在控制台中显示控件名称的前30个字符,
        始终在日志文件中显示全名 @AutomationLog.txt
<Color=Cyan>-p</Color>      显示 <Color=Cyan>过程 id</Color> 的控件

if <Color=Red>unicode错误</Color> 或 <Color=Red>查找错误</Color> 打印时发生,
尝试使用更改控制台窗口的活动代码页 <Color=Cyan>chcp</Color>或查看日志文件 <Color=Cyan>@AutomationLog.txt</Color>
chcp，获取当前活动代码页
chcp936，将活动代码页设置为gbk
chcp 65001，将活动代码页设置为utf-8

示例：
automation.py -t3
automation.py -t3 -r -d1 -m -n
automation.py -c -t3

""", writeToFile=False)


def main():
    import getopt
    auto.Logger.Write('UI自动化 {} (Python {}.{}.{}, {} bit)\n'.format(auto.VERSION, sys.version_info.major, sys.version_info.minor, sys.version_info.micro, 64 if sys.maxsize > 0xFFFFFFFF else 32))
    options, args = getopt.getopt(sys.argv[1:], 'hrfcanpd:t:',
                                  ['help', 'root', 'focus', 'cursor', 'ancestor', 'showAllName', 'depth=',
                                   'time='])
    root = False
    focus = False
    cursor = False
    ancestor = False
    foreground = True
    showAllName = False
    depth = 0xFFFFFFFF
    seconds = 3
    showPid = False
    for (o, v) in options:
        if o in ('-h', '-help'):
            usage()
            sys.exit(0)
        elif o in ('-r', '-root'):
            root = True
            foreground = False
        elif o in ('-f', '-focus'):
            focus = True
            foreground = False
        elif o in ('-c', '-cursor'):
            cursor = True
            foreground = False
        elif o in ('-a', '-ancestor'):
            ancestor = True
            foreground = False
        elif o in ('-n', '-showAllName'):
            showAllName = True
        elif o in ('-p', ):
            showPid = True
        elif o in ('-d', '-depth'):
            depth = int(v)
        elif o in ('-t', '-time'):
            seconds = int(v)
    if seconds > 0:
        auto.Logger.Write('请稍候 {0} 秒\n\n'.format(seconds), writeToFile=False)
        time.sleep(seconds)
    auto.Logger.ColorfullyLog('开始，当前光标位置: <Color=Cyan>{}</Color>'.format(auto.GetCursorPos()))
    control = None
    if root:
        control = auto.GetRootControl()
    if focus:
        control = auto.GetFocusedControl()
    if cursor:
        control = auto.ControlFromCursor()
        if depth < 0:
            while depth < 0 and control:
                control = control.GetParentControl()
                depth += 1
            depth = 0xFFFFFFFF
    if ancestor:
        control = auto.ControlFromCursor()
        if control:
            auto.EnumAndLogControlAncestors(control, showAllName, showPid)
        else:
            auto.Logger.Write('IUIAutomation在游标下返回null元素\n', auto.ConsoleColor.Yellow)
    else:
        indent = 0
        if not control:
            control = auto.GetFocusedControl()
            controlList = []
            while control:
                controlList.insert(0, control)
                control = control.GetParentControl()
            if len(controlList) == 1:
                control = controlList[0]
            else:
                control = controlList[1]
                if foreground:
                    indent = 1
                    auto.LogControl(controlList[0], 0, showAllName, showPid)
        auto.EnumAndLogControl(control, depth, showAllName, showPid, startDepth=indent)
    auto.Logger.Log('Ends\n')


if __name__ == '__main__':
    main()