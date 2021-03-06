import json
from struct import pack, unpack
from common.user import User

PORT = 3998

LOGIN = 1
LOGOUT = 2
ONLINE = 3
CONFIRM_LOGIN = 4
USER_INFO = 5
GET_USER_INFOS = 6
ALL_USER_INFOS = 7
LOGIN_FAIL = 8
CHAT_MSG = 20

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
            cls._instance.parser_dic[ALL_USER_INFOS] = parse_all_user_info_msg
            cls._instance.parser_dic[CHAT_MSG] = parse_chat_msg

        return cls._instance

def build_nopara_msg(msg_id):
    msg_len = 4 + 2 + 2
    return pack('I', msg_len) + pack('H',msg_id) + bytearray(2)

def build_login_fail_msg():
    return build_nopara_msg(LOGIN_FAIL)

def build_json_msg(msg_id, data):
    body = json.dumps(data).encode()
    msg_len = 4 + 2 + len(body) + 2
    return pack('I', msg_len) + pack('H',msg_id) + body + bytearray(2)

def build_user_msg(user):
    return build_json_msg(USER_INFO, dict(user))

def build_login_msg(name, pwd):
    msg_len = 4 + 2 + 64 + 64 + 2
    byte_name = name.encode()
    byte_pwd = pwd.encode()
    return pack('I', msg_len) + pack('H',LOGIN)+byte_name+bytearray(64-len(byte_name))+byte_pwd+bytearray(64-len(byte_pwd))+bytearray(2)

def build_online_msg(user):
    return build_json_msg(ONLINE, dict(user))

def build_logout_msg(name):
    msg_len = 4 + 2 + 64 + 2
    name_bytes = name.encode()
    return pack('I', msg_len) + pack('H',LOGOUT) + name_bytes + bytearray(64-len(name_bytes)+2)

def build_get_all_users_msg():
    return build_nopara_msg(GET_USER_INFOS)

def build_all_users_msg(users):
    arr = []
    for user in users:
        arr.append(dict(user))
    return build_json_msg(ALL_USER_INFOS, arr)

def build_chat_msg(ufrom, uto, val):
    return build_json_msg(CHAT_MSG, {'from':ufrom, 'to':uto, 'val':val})


def parse_json_msg(bytes):
    msg_len = unpack('I', bytes[:4])[0]
    body = bytes[6:msg_len - 2].decode()
    data = json.loads(body)
    return data

def parse_chat_msg(bytes):
    return parse_json_msg(bytes)

def parse_userinfo_msg(bytes):
    user_dic = parse_json_msg(bytes)
    return User.parse_from_dic(user_dic)

def parse_all_user_info_msg(bytes):
    user_dic_arr = parse_json_msg(bytes)
    users = []
    for user_dic in user_dic_arr:
        users.append(User.parse_from_dic(user_dic))
    return users

def parse_name_msg(bytes):
    name = bytes[6:len(bytes)-2].decode()
    return {'name': name}

def parse_online_msg(bytes):
    user_dic = parse_json_msg(bytes)
    return User.parse_from_dic(user_dic)

def parse_login_msg(bytes):
    name = bytes[6:6+64].decode()
    pwd = bytes[6+64:6+64+64].decode()
    return {'name': name.strip('\0'), 'pwd': pwd.strip('\0')}

def parse_logout_msg(bytes):
    return parse_name_msg(bytes)

def is_msg_valid(read_bytes):
    if len(read_bytes) < 6:
        return False
    n = unpack('I', read_bytes[0:4])[0]
    if n != len(read_bytes):
        return False

    return True

def parse_msg(read_bytes):
    if not is_msg_valid(read_bytes):
        return None

    msg_id = unpack('H', read_bytes[4:6])[0]

    if msg_id in MsgParse().parser_dic:
        data = MsgParse().parser_dic[msg_id](read_bytes)
        return {'msg_id':msg_id,'data':data}
    else:
        return {'msg_id':msg_id}

if __name__ == '__main__':
    from common.user import User
    user = User()
    user.name = 'test'
    user.nick_name = '测试'
    user.depart_id = 1
    msg = build_login_msg(user)
    print(parse_msg(msg))