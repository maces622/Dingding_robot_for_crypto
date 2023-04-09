import time
import hmac
import hashlib
import base64
import json
import urllib.parse
import urllib.request


class DingDingWebHook(object):
    secret=""
    url=""
    def __init__(self, secret, url):
        """
        :param secret: 安全设置的加签秘钥
        :param url: 机器人没有加签的WebHook_url
        """
        self.secret = secret
        self.url = url



    def send_meassage(self, data):
        """
        发送消息至机器人对应的群
        :param data: 发送的内容
        :return:
        """
        header = {
            "Content-Type": "application/json",
            "Charset": "UTF-8"
        }
        timestamp = round(time.time() * 1000)  # 时间戳
        secret_enc = self.secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, self.secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))  # 最终签名

        self.webhook_url = self.url + '&timestamp={}&sign={}'.format(timestamp, sign)  # 最终url，url+时间戳+签名
        send_data = json.dumps(data)  # 将字典类型数据转化为json格式
        send_data = send_data.encode("utf-8")  # 编码为UTF-8格式
        request = urllib.request.Request(url=self.webhook_url, data=send_data, headers=header)  # 发送请求

        opener = urllib.request.urlopen(request)  # 将请求发回的数据构建成为文件格式
        print(opener.read())  # 打印返回的结果


if __name__ == '__main__':
    my_secret = 'SECd9ca319eed07d2626182c8eace7a7a7fccafee6635cc93ac9a5ea5e6d879f3a2'
    my_url = 'https://oapi.dingtalk.com/robot/send?access_token=0bd7d9367869ce22f34958e9fa964ec922d2f2260eb129ac7f325dd32f11a5bc'
    my_data = {
        "msgtype": "text",
        "text": {
            "content":"sdljfl"
        },
        "at": {

            "isAtAll": False
        }
    }

    dingding = DingDingWebHook(secret=my_secret, url=my_url)
    dingding.send_meassage(my_data)
