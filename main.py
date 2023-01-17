import re
import time
import arrow
import random
import asyncio
import argparse
from rich.console import Console
from rich.progress import Progress, BarColumn, MofNCompleteColumn, SpinnerColumn, TaskProgressColumn, TimeElapsedColumn, TimeRemainingColumn
from xml.etree.ElementTree import Element, SubElement
from bilibili_api import video, Credential


def prettify_xml(root, level=0, indent='    ', new_line='\n'):
    result = ''

    if level == 0:
        result += f'<{root.tag}>{new_line}'
        result += prettify_xml(root, level + 1)
        result += f'</{root.tag}>{new_line}'
    else:
        for child in root:
            if child.text is None:
                result += f'{indent * level}<{child.tag}>{new_line}'
                result += prettify_xml(child, level + 1)
                result += f'{indent * level}</{child.tag}>{new_line}'
            else:
                if len(child.attrib) != 0:
                    result += f'{indent * level}<{child.tag}'
                    for key, value in child.attrib.items():
                        result += ' '
                        result += f'{key}="{value}"'
                    result += f'>{child.text}</{child.tag}>{new_line}'
                else:
                    result += f'{indent * level}<{child.tag}>{child.text}</{child.tag}>{new_line}'

    return result


async def main_logic(bvid, buvid3, bili_jct, sessdata):
    # 初始化凭证实例
    credential = Credential(buvid3=buvid3, bili_jct=bili_jct, sessdata=sessdata)
    # 初始化视频实例
    video_instance = video.Video(bvid=bvid, credential=credential)

    # 获取视频信息
    video_info = await video_instance.get_info()

    # 获取视频标题
    video_title = video_info['title']

    # 获取视频作者
    video_author = video_info['owner']['name']

    # 获取视频 cid (TODO 分P弹幕下载)
    video_cid = video_info['pages'][0]['cid']

    # 获取视频发布日期
    publish_time = arrow.get(video_info['pubdate'])

    # 获取当前日期
    now_time = arrow.utcnow()

    # 打印视频信息
    console.print(f'[*] 视频标题: {video_title}', style='blue')
    console.print(f'[*] 视频作者: {video_author}', style='blue')
    console.print(f'[*] 视频弹幕数: {video_info["stat"]["danmaku"]}', style='blue')
    console.print(f'[*] 视频识别码: AV号 {video_info["aid"]} BV号 {video_info["bvid"]}', style='blue')

    # 遍历从视频发布的日期到现在有弹幕的日期
    date_list = []
    total_count = (now_time.year * 12 + now_time.month) - (publish_time.year * 12 + publish_time.month) + 1
    task_danmaku_index = progress.add_task('[green]获取弹幕日期', total=total_count)
    while publish_time.year * 12 + publish_time.month <= now_time.year * 12 + now_time.month:
        danmaku_index = await video_instance.get_history_danmaku_index(cid=video_cid, date=publish_time)
        date_list += danmaku_index
        publish_time = publish_time.shift(months=1)
        progress.update(task_danmaku_index, advance=1)

        # 随机休眠一小段时间
        time.sleep(random.randint(2, 7) / 10)

    # 打印弹幕日期信息
    # console.print(f'[+] 共 {len(date_list)} 天有弹幕记录', style='green')
    
    # 遍历弹幕日期获取弹幕
    danmaku_list = []
    task_danmaku_info = progress.add_task('[green]获取弹幕信息', total=len(date_list))
    for date in date_list:
        danmaku = await video_instance.get_danmakus(cid=video_cid, date=arrow.get(date))
        danmaku_list += danmaku
        progress.update(task_danmaku_info, advance=1)

        # 随机休眠一小段时间
        time.sleep(random.randint(2, 7) / 10)
    
    # 弹幕去重算法
    danmaku_id_list = []
    danmaku_list_filtered = []
    for danmaku in danmaku_list:
        if danmaku.id_ not in danmaku_id_list:
            danmaku_id_list.append(danmaku.id_)
            danmaku_list_filtered.append(danmaku)
    
    # 打印弹幕信息
    # console.print(f'[+] 共获取到 {len(danmaku_list)} 条弹幕信息', style='green')

    # 合成弹幕文件名
    danmaku_file_path = f'{video_title} - {video_author}.xml'

    # 处理合成弹幕文件名非法字符
    if re.match('[\\\\/:*?\"<>|]', danmaku_file_path):
        danmaku_file_path = re.sub('[\\\\/:*?\"<>|]', '', danmaku_file_path)
    
    # 创建 XML 元素
    root = Element('i')

    # 写入 XML 必要信息
    chat_server_element = SubElement(root, 'chatserver')
    chat_server_element.text = 'chat.bilibili.com'

    chat_id_element = SubElement(root, 'chatid')
    chat_id_element.text = str(video_cid)

    mission_element = SubElement(root, 'mission')
    mission_element.text = '0'

    max_limit_element = SubElement(root, 'maxlimit')
    max_limit_element.text = str(len(danmaku_list_filtered))

    state_element = SubElement(root, 'state')
    state_element.text = '0'

    real_name_element = SubElement(root, 'real_name')
    real_name_element.text = '0'

    source_element = SubElement(root, 'source')
    source_element.text = 'k-v'

    # 遍历弹幕列表写入 XML
    task_write_danmaku = progress.add_task('[green]写入弹幕文件', total=len(danmaku_list_filtered))
    for danmaku in danmaku_list_filtered:
        danmaku_element = SubElement(root, 'd')
        danmaku_element.attrib['p'] = f'{danmaku.dm_time},{danmaku.mode},{danmaku.font_size},{int(danmaku.color, 16)},{danmaku.send_time},{danmaku.pool},{danmaku.crc32_id},{danmaku.id_},{danmaku.weight}'
        danmaku_element.text = danmaku.text
        progress.update(task_write_danmaku, advance=1)
    
    # 休眠 0.1 绘制进度条
    time.sleep(0.1)

    # 导出 XML 文件
    with open(danmaku_file_path, 'w', encoding='utf-8') as f:
        f.write(prettify_xml(root))


if __name__ == '__main__':
    # 创建参数处理器
    parser = argparse.ArgumentParser()
    parser.add_argument('bvid', type=str, help='video bvid')
    parser.add_argument('-buvid3', type=str, help='user buvid3')
    parser.add_argument('-bili_jct', type=str, help='user bili_jct')
    parser.add_argument('-sessdata', type=str, help='user sessdata')
    args = parser.parse_args()

    # 初始化实例
    console = Console()
    progress = Progress(SpinnerColumn(), '{task.description}', BarColumn(), MofNCompleteColumn(), TaskProgressColumn(), TimeElapsedColumn(), TimeRemainingColumn())
    progress.start()

    # 处理输入参数
    if args.bvid is None or args.bvid == '':
        console.print('[-] 视频 bvid 不能为空', style='red')
    elif args.buvid3 is None or args.buvid3 == '':
        console.print('[-] 用户 buvid3 不能为空', style='red')
    elif args.bili_jct is None or args.bili_jct == '':
        console.print('[-] 用户 bili_jct 不能为空', style='red')
    elif args.sessdata is None or args.sessdata == '':
        console.print('[-] 用户 sessdata 不能为空', style='red')
    else:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(main_logic(args.bvid, args.buvid3, args.bili_jct, args.sessdata))
