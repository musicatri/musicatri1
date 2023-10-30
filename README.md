<h1>musicatri——open source discord music bot</h1><br>

[website](https://musicatri.github.io/) <br>
<a href="readme-cn.md">Chinese中文</a><br>
Support netease cloud music, bilibili, youtube, niconico douga <br>
Supports adding playlists and searching NetEase Cloud Music songs.<br>
A web client is avaliable to add songs and adjust the order of the queue list<br>
There are other small features and easter eggs like vocabulary tests<br>

<h3>How to Configure:</h3><br>
0. Clone the repo
1. Depending on your operating system, run setup.bat/setup.sh.<br>
2. For Windows systems, ensure that Chrome/Chromium and ffmpeg are installed, and place the corresponding chromedriver in the musicatri directory to enable Netease Cloud Music search functionality.<br>
Note: setup.sh will only automatically install ffmpeg and chromium on systems that use apt (e.g., Debian/Ubuntu). For other systems, please install them manually (e.g., Arch/Fedora).<br>

<h3>TODO:</h3><br>
add language selection and English support☑️<br>
add support for searching youtube<br>
create a new chrome instance for each active guild for song searching, or create a queue for song search requests<br>
use a list instead of a dictonary for queue list<br>

