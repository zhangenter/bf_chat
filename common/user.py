class User(object):
    def __init__(self):
        self.name = ''
        self.nick_name = ''
        self.depart_id = -1

    def keys(self):
        return ('name', 'nick_name', 'depart_id')

    def __getitem__(self, item):
        return getattr(self, item)

    @staticmethod
    def parse_from_dic(dic):
        user = User()
        user.name = dic['name']
        user.nick_name = dic['nick_name']
        user.depart_id = dic['depart_id']
        return user