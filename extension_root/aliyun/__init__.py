import typing
import uuid
import json
import logging
from runtime import Runtime
from extension.models import Extension
from common.provider import SMSProvider
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.profile import region_provider
from .request.v20170525.SendSmsRequest import SendSmsRequest
from .views import AliyunSmsView, AliyunSmsSendView
from django.urls import path
from . import pages

class AliyunSMSProvider(SMSProvider):

    product_name = 'Dysmsapi'
    region = 'cn-hangzhou'
    domain = 'dysmsapi.aliyuncs.com'

    def __init__(self, access_key: str, secret_key: str, template: str, signature: str) -> None:
        self.access_key = access_key
        self.secret_key = secret_key
        self.template = template
        self.signature = signature

    def send_auth_code(self, mobile, code):
        template_param = {"code": str(code)}
        self.send_sms(mobile, self.signature, self.template, template_param)

    def send_sms(self, mobile, sign_name, template_code, template_param=None):
        business_id = uuid.uuid1()
        sms_req = SendSmsRequest()
        sms_req.set_TemplateCode(template_code)

        if template_param is not None:
            sms_req.set_TemplateParam(template_param)

        sms_req.set_OutId(business_id)
        sms_req.set_SignName(sign_name)
        sms_req.set_PhoneNumbers(mobile)
        acs_client = AcsClient(self.access_key, self.secret_key, self.region)
        region_provider.add_endpoint(self.product_name, self.region, self.domain)

        try:
            sms_res = acs_client.do_action_with_exception(sms_req)
            logging.error(sms_res)
            data = json.loads(str(sms_res, 'utf-8'))
            if data['Code'] == 'OK':
                return True
            else:
                logging.error('SMS[{}]: '.format(mobile) + data['Message'])
                raise Exception

        except Exception as e:
            raise RuntimeError(sms_res)


class AliyunExtension(Extension):    

    def start(self, runtime: Runtime, *args, **kwargs):
        sms_provider = AliyunSMSProvider(
            access_key=self.config('access_key'),
            secret_key=self.config('secret_key'),
            template=self.config('template'),
            signature=self.config('signature'),
        )

        runtime.sms_provider = sms_provider

        runtime.register_route([
            path('extension/aliyun/config', AliyunSmsView.as_view(), name='aliyun')
        ], namespace='global')
        runtime.register_route([
            path('extension/aliyun/send_sms', AliyunSmsSendView.as_view(), name='aliyun')
        ], namespace='global')

        super().start(runtime=runtime, *args, **kwargs)


extension = AliyunExtension(
    scope='global',
    name='aliyun',
    description="""基于阿里云平台的扩展功能
1. 短信发送
""",
    version='1.0',
    homepage='https://www.longguikeji.com',
    logo='',
    maintainer='insfocus@gmail.com',
)
