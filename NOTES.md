# NAO 的使用方法及注意事项

## NAO 的固件型号与序列号

Naoqi version:  2.1.2

BO S/N:         ALDR1312N090156

## 检测 NAO 的关节状况信息

将 nao_ip 替换成 NAO 的互联网地址：

> http://nao_ip/advanced/#hardware

管理 NAO 的设置：

> http://nao_ip/#/menu/myrobot

其中，alive by default 要关闭以避免 NAO 瞎动。

## 避免 NAO 关节过热

如果长时间保持关节 stiffness 会导致关节过热，解决方法是不用 NAO 的时候使用 rest() 函数让他休息，此时关节 stiffness 为 0 ，电机不发热。

## 联系 Aldebaran 的客户服务

发送邮件到：

> support@aldebaran-robotics.com

或在网页入口提交 issue 。一般半小时之内得到回复，非常及时，推荐使用！（注意说清楚型号和序列号）

## 使用 Webots 虚拟环境调试 Nao

(Courtesy of Dstray)

直接下载 webots for nao 的 deb 包用 dpkg 进行安装，然后第一次打开之后一定要更新不然好多东西没有（下载很多，等着就行）。

更新之后重启 webots 会自动加载一张地图。这时候连本机 (127.0.0.1:9559) 就可以在本地进行调试了。
