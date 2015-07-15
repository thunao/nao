# NAO 的使用方法及注意事项

## 检测 NAO 的关节状况信息

将 nao_ip 替换成 NAO 的互联网地址：

> http://nao_ip/advanced/#hardware

管理 NAO 的设置：

> http://nao_ip/#/menu/myrobot

其中，alive by default 要关闭以避免 NAO 瞎动。

## 避免 NAO 关节过热

如果长时间保持关节 stiffness 会导致关节过热，解决方法是不用 NAO 的时候使用 rest() 函数让他休息，此时关节 stiffness 为 0 ，电机不发热。
