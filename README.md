# B 站历史弹幕采集

[![STARS](https://img.shields.io/github/stars/HenryWu01/BiliBili-Danmaku-Collect?color=yellow&label=Github%20Stars)][stargazers]
[![LICENSE](https://img.shields.io/badge/LICENSE-AGPLv3-red)][license]
![PYTHON](https://img.shields.io/badge/Python-3.10|3.9|3.8|3.7|3.6-blue)

B 站现在获取到的弹幕格式都是 protobuf 不再是 xml 格式了.

## 特性
1. 自动转换 XML 文件
2. 获取视频的所有弹幕
3. 简介漂亮好用的命令行界面

## 安装依赖
```
pip install -r requirements.txt
```

## 使用方法
```
usage: main.py [-h] [-buvid3 BUVID3] [-bili_jct BILI_JCT] [-sessdata SESSDATA] bvid

positional arguments:
  bvid                video bvid

options:
  -h, --help          show this help message and exit
  -buvid3 BUVID3      user buvid3
  -bili_jct BILI_JCT  user bili_jct
  -sessdata SESSDATA  user sessdata
```

## 参数获取
``buvid3``, ``bili_jct`` 和 ``sessdata`` 的获取方法可以参考[这篇文章](https://bili.moyu.moe/#/get-credential)

## 特别感谢
1. [bilibili-api](https://github.com/Nemo2011/bilibili-api) (B 站 API)
2. [bilibili-API-collect](https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/danmaku/danmaku_xml.md) (xml 弹幕格式)

[license]: https://github.com/HenryWu01/BiliBili-Danmaku-Collect/tree/main/LICENSE.md
[stargazers]: https://github.com/HenryWu01/BiliBili-Danmaku-Collect/stargazers