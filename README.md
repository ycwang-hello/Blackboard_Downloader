# Blackboard_Downloader
 A script to download files from the Blackboard platform. Currently supported universities are: BNU ("BB平台") and PKU ("教学网"; only partial support).

**注意：You use at your own risk. MIT license中写道：**

> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## 简介

部分课程的资料上传到了Blackboard (BB) 平台上，而且目录结构很复杂。平时经常需要将平台上的课程资料向本地同步，但是平台上并没有类似于打包下载的功能。这个脚本通过操控Chrome，实现自动下载功能（保留平台上的目录结构，且可以选择使用平台上显示的资料名称或者文件本身的名称），不再需要手动点击多次鼠标。

程序运行时将会产生数据文件“BBDown.names”，它可帮助程序更好地识别以前已经下载过的文件，避免重复下载。

如果需要关于Python或该脚本使用的帮助，或者在运行脚本时出现问题，可在Issue页反馈。

## 依赖

必须有这些程序才能运行此脚本：

- Python 3.x with `numpy`,`selenium`, `requests`, `beautifulsoup4`;
- `webdriver_manager` (not necessary);
- Chrome;
- 与Chrome版本一致的[chromedriver](http://chromedriver.chromium.org/downloads)（可在Chrome中查看版本；如无法下载可以搜索其他镜像网站下载）, 下载后应放在脚本所在的目录下。

## 用法

这是Windows中的用法梗概，具体按照程序中的提示操作。

- 在cmd等命令行中输入文件所在盘符（如`E:`）。
- 进入脚本、chromedriver所在的目录下（这一目录下的temp文件夹，如果有的话，最好为空）：`cd your/own/path/to/script`
- 执行`python BBDown.py`
- 选择你的学校（暂时仅支持BNU、PKU）
- 在弹出的Chrome中输入用户名密码，登录，然后回到cmd。
- 输入要下载的课程编号。
- 核对要下载的目录和文件，可以选择只下载一部分，也可以智能识别并排除可能已经下载好的文件。由用户确认下载。
- 下载设置：
  - BB上的资料名称和实际对应的下载下来的文件名称常常不同，选择最终保存的文件使用BB上写的名称还是下载的文件名称；
  - 当目录中已经存在同名文件时，总是覆盖/总是跳过/总是提问是否覆盖。
- 下载过程中可能需要用户的情况：
  - 发现文件已经存在，询问覆盖或跳过；
  - BB上写的文件名和实际下载的文件名不一致，需要用户指出哪个文件和当前下载的文件对应（也可能只是文件还没下载好，可尝试输入r刷新）；
  - 找不到下载链接或没能下载：可以手动下载并告诉程序是哪个文件，或者跳过这一文件（或许这根本就不是一个文件）。
- 输出Congratulations说明程序正常退出。

## 原理

用Python操控Chrome，模拟鼠标点击浏览和下载的过程。主要分为3步：

1. 登录BB（目前只能手动登录）、选择课程、找到课程文档；
2. 检查课程文档目录结构；
3. 下载所选的文件。

## 局限

说到局限那真是说半天也说不完，这些局限主要是因为作者水平太低或者比较懒，没有搞。

- 这个脚本是通过控制Chrome实现下载的，不能直接实现文件下载；
- 可能在非Windows中的运行和预想的不一样（其实只是\和/的区别，但是作者懒得改）；
- 需要手动登录；
- 下载不能并行，只能一个接着一个下载；
- 下载过程中经常需要用户提供帮助，不能识别下载的文件名是什么，不能智能识别临时文件夹中哪个文件是想要的文件；
- 部分语句没有实现智能等待网页加载，如在设定的等待时间内网页未加载完成则程序会出错，在网速慢的环境会出现问题；
- 没有做完整的错误输入处理，用户输入错误可能导致程序需要重来；
- 程序中的指引不够详细，用户只看程序输出的说明可能不知道如何正确操作；
- ......

## 更新记录

2021-3-7

BB换了新的系统，网页有些变化，而且变聪明了，这导致原来的脚本用不了了。所以更新了脚本来适配新的BB平台。

增加功能：保存文件可以使用文件本身的名称而不是BB上显示的资料名称。

2022-9-30

增加对PKU“教学网”的部分支持。
