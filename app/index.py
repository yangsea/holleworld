#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   XueWeiHan
#   E-mail  :   595666367@qq.com
#   Date    :   16/3/11 下午3:54
#   Desc    :   首页
import logging

from app import BaseHandler, UserHandler
from model import models


class LoginHandler(BaseHandler):
    """
    登陆
    """
    @staticmethod
    def check_login(user_name, password):
        """
        验证用户，支持邮箱和用户名登陆
        """
        user = models.User.find_first('where email=? and password=?',
                                      user_name, password) or \
               models.User.find_first('where name=? and password=?',
                                      user_name, password)
        return user

    def get(self):
        # log记录访问者的ip
        logging.info('{}！'.format(self.request.remote_ip))
        if self.session:
            self.redirect('/article/list')
        self.render('index.html')

    def post(self):
        user_name = self.get_argument('email', None)
        password = self.get_argument('password', None)
        user = LoginHandler.check_login(user_name, password)
        if user:
            self.session = {'uid': user.uid,
                            'name': user.name,
                            'admin': user.admin}
            self.write_success()
        else:
            self.write_fail()


class SignHandler(BaseHandler):
    """
    注册
    """
    @staticmethod
    def check_code(code):
        """
        检查邀请码是否正确
        :return code_obj: 用于注册成功后，设置邀请码失效
        """
        if not code:
            return False
        _code = models.Code.find_first('where code=? and status=0', code)
        if _code:
            code_obj = models.Code.get(_code.id)
            return code_obj
        else:
            return False

    def post(self):
        name = self.get_argument('name', None)
        email = self.get_argument('email', None)
        password = self.get_argument('passwd', None)
        password2 = self.get_argument('rePasswd', None)

        # 检测两次密码输入是否相同
        if password != password2:
            self.write_fail(message=u'注册失败')

        # 初期打算加上邀请码
        code = self.get_argument('code', None)
        code_obj = SignHandler.check_code(code)
        if not code_obj:
            self.write_fail(message=u'邀请码错误')

        u = models.User(email=email, name=name, password=password)
        try:
            u.insert()
            # 注册成功，该邀请码失效
            code_obj.status = 1
            code_obj.update_time = self.now()  # 记录失效时间
            code_obj.update()
        except Exception:
            self.write_fail(message=u'注册失败')
        self.write_success()


class CheckoutSignArgsHandler(BaseHandler):
    """
    检查注册时输入的参数
    """
    def post(self):
        name = self.get_argument('name', None)
        email = self.get_argument('email', None)
        if name:
            if models.User.find_first('where name=? and status=0', name):
                self.write_fail(message=u'抱歉，用户名已被占用')

        if email:
            if models.User.find_first('where email=? and status=0', email):
                self.write_fail(message=u'抱歉，邮箱已被占用')
        self.write_success()


class LogoutHandler(UserHandler):
    """
    注销
    """
    def get(self):
        del self.session
        self.redirect('/')


class TestHandler(BaseHandler):
    """
    用于练习一些功能
    """
    def get(self):
        # self.render('upload_pic.html')
        self.render('test.html')

    def post(self):
        img_file = self.request.fi

        print img_file
