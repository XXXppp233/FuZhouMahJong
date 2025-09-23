ActionButton = 编辑按钮的样式
DiscardButton = 出牌按钮
MahjongGame = 游戏开始后的界面
MahjongTile = 编辑单个牌
MyTiles = 编辑自己的手牌区，包括弃牌区
Room = 加入房间后显示房间项目，包括聊天
RoomList = 链接到服务器后显示房间列表

vw,vh 让大小按照屏幕比例，相当于禁用缩放

上半部分占用 60vh, 其中 Chat 占有 15vw
下半部分占用 40vh, margin-top 为 5vh margin-bottom 为 2vh

full 系列的大图用在房间内选角色的界面，在右侧展示渐变的角色海报
head 系列的小图作为房间内选角色的选项和游戏内的头像，大部分二游角色可以使用铸币大头

``` 批量转换当前目录的 png 为 webp
for f in *.png; do     ffmpeg -i "$f" -vcodec libwebp -lossless 1 "${f%.png}.webp"; done
```
``` 循环播放动画
for f in *.png; do
    ffmpeg -i "$f" -vcodec libwebp -lossless 1 -loop 0 "${f%.png}.webp"
done
```


主题色彩应用范围
ActionButton 的背景色
MahjongTile 的选中 border-color
Message 的 border-left
Chat 的发送按钮背景色

z-index
-1: BackGround
0: Music(Visual)
1: 主页面
20: 音乐控件

Socketio 事件归属
App.vue

- connect, disconnect
- join_server_result # 登陆结果

roomlist.vue

- room_list_update
- create_room
- join_room

room.vue

- room_info_update

m 打开音乐控制面板，关闭面板时，如果音乐被暂停则继续播放。
c 让光标移动到聊天的输入框并屏蔽快捷键
esc 把光标从聊天输入框移除并恢复快捷键
q/e 左右移动选择的牌
d 打出牌



9.14 玩家离开房间没有为客户端更新房间状态
尝试使用 pina 来管理聊天信息
