# Max interpark 搶票機器人
help you quickly fill your order form online.

好多人想去看韓國追星，或是去看《英雄聯盟》世界賽，我寫了一個自動填表單的小程式，能幫你搶票更順利。

如果是在公用的電腦，建議不要填入自己所有的信用卡資料，以避免個人的資料遭其他共用電腦的使用者被盜用。

目前搶票機器人因為 CloudFlare 已無法使用, 需要找時間把腳本從 selenium 改寫為 DrissionPage 格式, 如果想了解進度，可以在下面的專案去看看:

https://github.com/g1879/DrissionPage/


# Demo (示範影片)

Max Interpark Bot 2023-08-31 自動填表單與勾選

https://youtu.be/UKgGG2nZPk0

Max Interpark Bot 2023-08-01 自動驗證碼

https://youtu.be/2bFhGDBXIBE



# Feature (主要功能)
* 自動登入 interpark 或 facebook 帳號。
* 會自動按「But Tickets」的按鈕。
* 自動選取第1個可以購買的場次。
* 自動選取第1個可以購買的時間。
* 自動關閉「Booking Info」訊息框框。
* 自動關閉「Secure Booking service」說明訊息框框。
* 自動猜測與輸入驗證碼，需要人工手動地點擊輸入。驗證碼可能會猜錯。
* 自動填入個人/信用卡資料。
* 自動勾選 I agree。


# How to use (如何使用)
https://max-everyday.com/2023/08/interpark-bot/

# How to execute source code (透過原始碼的執行方法)
1: install latest version python:

https://www.python.org/downloads/

2: install dependency packages:

<code>python -m pip install selenium</code>

3: run config interface:

<code>python settings.py</code>


# Introduce the implement (實作方法)
https://stackoverflow.max-everyday.com/2018/03/selenium-chrome-webdriver/

# Execute suggestion (填表單建議)
限量的訂位系統的是殘酷的，建議不要用破舊的電腦或連線不穩的手機網路來搶，因為只要比別人慢個 0.1 秒，名額可能就沒了。為了要搶到限量的名額真心建議去網咖或找一個網路連線穩定且快的地方並使用硬體不差的電腦來搶位子。

如果你在使用上有遇到問題，建議先看看下面這篇文章裡的問題排除，因為 MaxBot 和 Max Interpark Bot 用的程式幾乎一樣: https://max-everyday.com/2018/03/tixcraft-bot/

# Donate (贊助Max)
如果你覺得這篇文章或MaxBot寫的很好，想打賞Max，贊助方式如下： https://max-everyday.com/about/#donate

