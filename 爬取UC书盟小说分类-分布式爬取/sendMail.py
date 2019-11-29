'''
Python发送一个未知MIME类型的文件附件其基本思路如下：
1. 构造MIMEMultipart对象做为根容器
2. 构造MIMEText对象做为邮件显示内容并附加到根容器
3. 构造MIMEBase对象做为文件附件内容并附加到根容器
 　　a. 读入文件内容并格式化
 　　b. 设置附件头
4. 设置根容器属性
5. 得到格式化后的完整文本
6. 用smtp发送邮件
'''

import smtplib, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


class Mailer(object):
    def __init__(self, maillist, mailtitle, mailcontent, content_type):
        self.mail_list = maillist
        self.mail_title = mailtitle
        self.mail_content = mailcontent
        self.content_type = content_type

        # 测试用邮件服务器
        self.mail_host = "smtp.qq.com"
        self.mail_user = "*******"
        self.mail_pass = "********"
        self.mail_postfix = "qq.com"
        
    def sendMail(self, filelist=None):

        me = self.mail_user + "<" + self.mail_user + "@" + self.mail_postfix + ">"
        msg = MIMEMultipart()
        msg['Subject'] = self.mail_title
        msg['From'] = me
        msg['To'] = ";".join(self.mail_list)

        # puretext = MIMEText('<h1>你好，<br/>'+self.mail_content+'</h1>',self.content_type,'utf-8')
        puretext = MIMEText(self.mail_content, self.content_type, 'utf-8')
        msg.attach(puretext)

        if filelist is not None:  # 添加多个附件文件
            for filepath in filelist:
                filename = os.path.basename(filepath)
                part = MIMEApplication(open(filepath, 'rb').read())
                part.add_header('Content-Disposition', 'attachment', filename=('gbk', '', filename))
                msg.attach(part)

        try:
            s = smtplib.SMTP()  # 创建邮件服务器对象
            s.connect(self.mail_host)  # 连接到指定的smtp服务器。参数分别表示smpt主机和端口
            s.login(self.mail_user, self.mail_pass)  # 登录到你邮箱
            s.sendmail(me, self.mail_list, msg.as_string())  # 发送内容
        finally:
            s.close()


def send(mailto_list, mail_title, mail_content, content_type='plain', filelist=None):
    mailtolist = mailto_list.replace(' ', '').split(',')
    mm = Mailer(mailtolist, mail_title, mail_content, content_type)
    mm.sendMail(filelist)


if __name__ == '__main__':
    # send list
    try:
        mailto_list = "*******"
        mail_title = '测试发送附件'
        mail_content = '测试发送附件'
        send(mailto_list, mail_title, mail_content, 'plain', ['./excel/*****.xlsx'])
    except Exception as e:
        print(str(e))
