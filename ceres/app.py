# coding: utf-8
# import simplejson
import time
import datetime
from xml.dom.minidom import parseString
from flask import Flask, request, abort
from mako.template import Template
from ceres.lib.wechat_sdk.WXBizMsgCrypt import WXBizMsgCrypt
from ceres.config import AppConfig
from ceres.model.user import User
from ceres.model.bill import Bill


# config data
WECHAT_TOKEN = AppConfig.WECHAT_TOKEN
ENCODING_AES_KEY = AppConfig.ENCODING_AES_KEY
WECHAT_CORP_ID = AppConfig.WECHAT_CORP_ID

wxcpt = WXBizMsgCrypt(WECHAT_TOKEN, ENCODING_AES_KEY, WECHAT_CORP_ID)

app = Flask(__name__)


@app.route('/wechat/', methods=['GET'])
def wechat_get():
    '''微信接口验证'''
    msg_signature = request.values.get('msg_signature')
    timestamp = request.values.get('timestamp')
    nonce = request.values.get('nonce')
    echostr = request.values.get('echostr')

    ret, echostr_d = wxcpt.VerifyURL(msg_signature, timestamp, nonce, echostr)
    if ret:
        abort(401)

    return echostr_d


@app.route('/wechat/', methods=['POST'])
def wechat_post():
    msg_signature = request.values.get('msg_signature')
    timestamp = request.values.get('timestamp')
    nonce = request.values.get('nonce')
    data = request.data
    ret, msg = wxcpt.DecryptMsg(data, msg_signature, timestamp, nonce)
    request_data = parse_xml(msg)
    if ret:
        abort(401)

    # 处理消息
    process_func_list = [
        # echo_reply,
        create_bill,
        join_bill,
        check_bills,
        delete_bill,
        say_hello,
    ]

    ret_content = ''
    for process_func in process_func_list:
        content = process_func(request_data)
        if content:
            ret_content = content
            break

    if ret_content:
        ret, ret_content = wxcpt.EncryptMsg(ret_content.encode('utf-8'), nonce, timestamp)

    return ret_content


@app.route("/")
def hello():
    return "Hello World!"


def echo_reply(request_data):
    message_type = request_data.get('MsgType', '')
    if message_type != 'text':
        return

    text = request_data.get('Content')

    if isinstance(text, unicode):
        text = text.encode('utf-8')
    return generate_text_msg(request_data, text)


def say_hello(request_data):
    wx_id = request_data.get('FromUserName')
    user = User.get_by_wx_id(wx_id)
    msg = '''Hello, {}
AA 制各自创建报销单，非 AA 由付钱的人来创建报销单其他人再加入

【创建】输入 金额 创建报销餐费记录，如 30
【加入】输入 J单号 来加入别人的报销单，如 J145
【查询】输入「报销单」、「月报销单」来分别查询自己的当天和上一个报销月创建的报销单和加入的报销单
【删除】输入 D单号 来删除自己创建的报销单及相关记录，如 D145
'''.format(user.name)
    return generate_text_msg(request_data, msg)


def create_bill(request_data):
    message_type = request_data.get('MsgType', '')
    if message_type != 'text':
        return
    text = request_data.get('Content')

    if isinstance(text, unicode):
        text = text.encode('utf-8')
    try:
        amount = float(text)
    except:
        return
    wx_id = request_data.get('FromUserName')
    user = User.get_by_wx_id(wx_id)
    bill = Bill.create_one(user.id, amount)
    extra = ''
    if bill.average_amount() > 30:
        extra = '\n报销金额大于 30，让同行的小伙伴输入「J{}」来加入'.format(bill.id)
    ret_msg = '报销单创建成功！\n金额 {amount}{extra}'.format(amount=bill.amount, extra=extra)
    return generate_text_msg(request_data, ret_msg)


def join_bill(request_data):
    message_type = request_data.get('MsgType', '')
    if message_type != 'text':
        return
    text = request_data.get('Content')

    if isinstance(text, unicode):
        text = text.encode('utf-8')
    if not text.startswith('J') and not text.startswith('j'):
        return
    try:
        bill_id = int(text[1:])
    except:
        return
    wx_id = request_data.get('FromUserName')
    user = User.get_by_wx_id(wx_id)
    bill = Bill.get_by_id(bill_id)
    if not bill:
        return generate_text_msg(request_data, '单号不存在')
    if user.id in bill.take_part_in_user_ids():
        return generate_text_msg(request_data, '已经加入')
    bill.add_take_part_in_user(user)
    msg = '加入成功，{} 创建，当前 {} 人，总金额 {}，当前平均 {}'.format(bill.payer().name,
        bill.take_part_in_users_count(),
        bill.amount,
        bill.average_amount())
    return generate_text_msg(request_data, msg)


def check_bills(request_data):
    message_type = request_data.get('MsgType', '')
    if message_type != 'text':
        return
    text = request_data.get('Content')

    if isinstance(text, unicode):
        text = text.encode('utf-8')

    if text == '报销单':
        mode = 'day'
    elif text == '月报销单':
        mode = 'month'
    else:
        return

    start_time, end_time = None, None
    if mode == 'month':
        now = datetime.datetime.now()
        today = datetime.datetime(now.year, now.month, now.day)
        if today.day < 24:
            # 前推 25 天，再重新设置天，保证是上月的 24 号
            _st = today - datetime.timedelta(25)
            start_time = datetime.datetime(_st.year, _st.month, 24)
            end_time = datetime.datetime(today.year, today.month, 24)

    wx_id = request_data.get('FromUserName')
    user = User.get_by_wx_id(wx_id)
    paid_bills = Bill.get_paid_by_user(user.id, start_time, end_time)
    only_joined_bills = Bill.get_only_joined_by_user(user.id, start_time, end_time)
    show_bills = ['支付的：']
    for bill in paid_bills:
        date_str = datetime.datetime.strftime(bill.receipt_time, '%m-%d')
        show_bills.append('{date} {user_count} 人 ￥{amount} ID {id}'.format(date=date_str, user_count=bill.take_part_in_users_count(), amount=bill.amount, id=bill.id))
    show_bills.append('仅参与的：')
    for bill in only_joined_bills:
        date_str = datetime.datetime.strftime(bill.receipt_time, '%m-%d')
        show_bills.append('{date} {user_count} 人 {payer}付'.format(date=date_str, user_count=bill.take_part_in_users_count(), payer=bill.payer().name))
    show_bills = '\n'.join(show_bills)
    return generate_text_msg(request_data, show_bills)


def delete_bill(request_data):
    message_type = request_data.get('MsgType', '')
    if message_type != 'text':
        return
    text = request_data.get('Content')
    if isinstance(text, unicode):
        text = text.encode('utf-8')
    if not text.startswith('D') and not text.startswith('d'):
        return
    try:
        bill_id = int(text[1:])
    except:
        return
    wx_id = request_data.get('FromUserName')
    user = User.get_by_wx_id(wx_id)
    bill = Bill.get_by_id(bill_id)
    if not bill:
        return generate_text_msg(request_data, '单号不存在')
    if bill.payer_id != user.id:
        return generate_text_msg(request_data, '只能有创建者删除')
    bill.delete_bill()
    return generate_text_msg(request_data, '删除成功！')


# help func

def parse_xml(data):
    '''将微信传来的 xml 解析成 dict'''
    result = {}
    dom = parseString(data)
    ele = dom.documentElement
    for i in ele.childNodes:
        ele = i.firstChild
        if ele:
            result[i.nodeName] = ele.nodeValue
    return result


def generate_text_msg(request_data, content):
    '''生成文本消息'''
    create_time = int(time.time())
    return text_msg_template.render(
        to_user_name=request_data.get('FromUserName'),
        from_user_name=request_data.get('ToUserName'),
        create_time=create_time,
        content=content)


def generate_image_text_msg(request_data, articles):
    '''
    生成图文消息

    articles sample:
    [
        {
            'title': '夏日蜜桃冰菓',
            'description': '桃子的新式吃法，夏日感十足',
            'pic_url': 'http://ww3.sinaimg.cn/large/006tNc79gw1f5kb16dn0dj30a005kglx.jpg',
            'url': 'https://simplecms.xiachufang.com/posts/992/',
        },
    ]

    - 第一个 article 的 pic 使用大图应该为 360 * 200
    - 剩余 article 的 pic 使用小图应该为 200 * 200
    - 只有当 article 为一个的时候才会显示 description
    '''
    create_time = int(time.time())
    return image_text_msg_template.render(
        to_user_name=request_data.get('FromUserName'),
        from_user_name=request_data.get('ToUserName'),
        create_time=create_time,
        articles=articles)


# 模板和配置


text_msg_template = Template('''<xml>
<ToUserName><![CDATA[${to_user_name}]]></ToUserName>
<FromUserName><![CDATA[${from_user_name}]]></FromUserName>
<CreateTime>${create_time}</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[${content}]]></Content>
</xml>
''')

image_text_msg_template = Template('''<xml>
<ToUserName><![CDATA[${to_user_name}]]></ToUserName>
<FromUserName><![CDATA[${from_user_name}]]></FromUserName>
<CreateTime>${create_time}</CreateTime>
<MsgType><![CDATA[news]]></MsgType>
<ArticleCount>${len(articles)}</ArticleCount>
<Articles>
%for article in articles:
<item>
<Title><![CDATA[${article['title']}]]></Title>
<Description><![CDATA[${article['description']}]]></Description>
<PicUrl><![CDATA[${article['pic_url']}]]></PicUrl>
<Url><![CDATA[${article['url']}]]></Url>
</item>
%endfor
</Articles>
</xml>
''')

transfer_customer_service_template = Template('''<xml>
<ToUserName><![CDATA[${to_user_name}]]></ToUserName>
<FromUserName><![CDATA[${from_user_name}]]></FromUserName>
<CreateTime>${create_time}</CreateTime>
<MsgType><![CDATA[transfer_customer_service]]></MsgType>
</xml>''')
