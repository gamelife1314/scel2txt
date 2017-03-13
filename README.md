### 将搜狗(sogou)的细胞词库转换为txt文件
----------------------------------------

环境：python3.5，python2请看：[https://github.com/archerhu/scel2mmseg](https://github.com/archerhu/scel2mmseg)

使用方式如下：

1.  作为工具使用
    ```
    python3 scel2txt.py ./ ./dict.txt
    ```
    第一个参数：`./` 表明scel文件的目录，也可以指定单个文件：`./亲戚称呼.scel`
    第二个参数(可选)，默认为：`./dict.txt`

2.  整合在其他程序中
    ```python
        for word in transform("./"):
            print(word)
    ```
    或者
    ```python
       transform_and_save("./", "./dict.txt")
    ```



