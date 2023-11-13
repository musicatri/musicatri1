<h1>musicatri——open source discord music bot</h1><br>

[website](https://musicatri.github.io/) <br>
<a href="readme-cn.md">Chinese中文</a><br>
Support netease cloud music, bilibili, youtube, niconico douga <br>
Supports adding playlists and searching NetEase Cloud Music songs.<br>
A web client is avaliable to add songs and adjust the order of the queue list<br>
There are other small features and easter eggs like vocabulary tests<br>

<h3>How to Configure:</h3><br>
0. <code>git clone https://github.com/musicatri/musicatri1.git</code><br>
1. Run setup.bat/setup.sh.<br>
2. For Windows, ensure that Chrome/Chromium and ffmpeg are installed, and place the corresponding chromedriver in the musicatri directory to enable Netease Cloud Music search functionality.<br>
Note: setup.sh will only automatically install ffmpeg and chromium on systems that use apt (e.g., Debian/Ubuntu). For other systems, please install them manually (e.g., Arch/Fedora).<br>

<h3>TODO:</h3><br>
add language selection and English support☑️<br>
add support for searching youtube<br>
c̶r̶e̶a̶t̶e̶ ̶a̶ ̶n̶e̶w̶ ̶c̶h̶r̶o̶m̶e̶ ̶i̶n̶s̶t̶a̶n̶c̶e̶ ̶f̶o̶r̶ ̶e̶a̶c̶h̶ ̶a̶c̶t̶i̶v̶e̶ ̶g̶u̶i̶l̶d̶ ̶f̶o̶r̶ ̶s̶o̶n̶g̶ ̶s̶e̶a̶r̶c̶h̶i̶n̶g̶,̶ ̶o̶r̶ ̶c̶r̶e̶a̶t̶e̶ ̶a̶ ̶q̶u̶e̶u̶e̶ ̶f̶o̶r̶ ̶s̶o̶n̶g̶ ̶s̶e̶a̶r̶c̶h̶ ̶r̶e̶q̶u̶e̶s̶t̶s̶☑️ Fixed with using NeteaseCloudMusicApi<br>
use a list instead of a dictonary for queue list<br>
use something other than a pull request every 2 second to update song information for the website<br>
