import json
from struct import pack, unpack
LOGIN = 1
LOGOUT = 2
MSG = 3
USER_INFO = 4
ONLINE = 5
CONFIRM_LOGIN = 6


class MsgParse(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.parser_dic = {}
            cls._instance.parser_dic[LOGIN] = parse_login_msg
            cls._instance.parser_dic[LOGOUT] = parse_logout_msg
            cls._instance.parser_dic[USER_INFO] = parse_userinfo_msg
            cls._instance.parser_dic[ONLINE] = parse_online_msg

        return cls._instance

def build_user_msg(user):
    dic = dict(user)
    body = json.dumps(dic).encode()
    msg_len = 4 + 2 + len(body) + 2
    return pack('I', msg_len) + pack('H',USER_INFO) + body + bytearray(2)

def build_login_msg(name, pwd):
    msg_len = 4 + 2 + 64 + 64 + 2
    byte_name = name.encode()
    byte_pwd = pwd.encode()
    return pack('I', msg_len) + pack('H',LOGIN)+byte_name+bytearray(64-len(byte_name))+byte_pwd+bytearray(64-len(byte_pwd))+bytearray(2)

def build_online_msg(user):
    dic = dict(user)
    body = json.dumps(dic).encode()
    msg_len = 4 + 2 + len(body) + 2
    return pack('I', msg_len) + pack('H',ONLINE) + body + bytearray(2)

def build_logout_msg(name):
    msg_len = 4 + 2 + 64 + 2
    name_bytes = name.encode()
    return pack('I', msg_len) + pack('H',LOGOUT) + name_bytes + bytearray(64-len(name_bytes)+2)

def parse_json_msg(bytes):
    msg_len = unpack('I', bytes[:4])[0]
    body = bytes[6:msg_len - 2].decode()
    dic = json.loads(body)
    return dic

def parse_userinfo_msg(bytes):
    return parse_json_msg(bytes)

def parse_name_msg(bytes):
    name = bytes[6:len(bytes)-2].decode()
    return {'name': name}

def parse_online_msg(bytes):
    return parse_json_msg(bytes)

def parse_login_msg(bytes):
    name = bytes[6:6+64].decode()
    pwd = bytes[6+64:6+64+64].decode()
    return {'name': name, 'pwd': pwd}

def parse_logout_msg(bytes):
    return parse_name_msg(bytes)

def parse_msg(bytes):
    if len(bytes) < 6:
        return None
    n = unpack('I', bytes[0:4])[0]
    if n != len(bytes):
        return None
    msg_id = unpack('H', bytes[4:6])[0]

    if msg_id in MsgParse().parser_dic:
        dic = MsgParse().parser_dic[msg_id](bytes)
        dic['msg_id'] = msg_id
        return dic
    else:
        return None

if __name__ == '__main__':
    from common.user import User
    user = User()
    user.name = 'test'
    user.nick_name = '测试'
    user.depart_id = 1
    msg = build_login_msg(user)
    print(parse_msg(msg))