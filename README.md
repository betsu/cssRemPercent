cssRemPercent
------------------
fork from https://github.com/flashlizi/cssrem/



####增加
* % 轉換
* 動態修改 rem root 值和 % 轉換的父層寬度

####安裝
1. 安裝前請先關閉 sublime text
2. 進入目錄 C:\Users\[電腦的user名稱]\AppData\Roaming\Sublime Text 3\Installed Packages
3. 開啟壓縮檔 cssrem.sublime-package
4. 將 cssrem.py 丟進去覆蓋
5. 啟動 sublime text
6. 增加command呼叫
  * Preferences > Key Bindings - User
  * 增加
  ```
    {
        "keys": ["ctrl+alt+w"],
         "command": "root_width"
    },
    {
        "keys": ["ctrl+alt+r"],
         "command": "root_rem"
    }
  ```
####使用方法
* `ctrl+alt+w`：修改 % 轉換父層寬度
* `ctrl+alt+r`：修改 rem root 值
