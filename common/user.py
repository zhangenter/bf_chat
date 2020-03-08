from sqlalchemy import  Column, Integer,String
from common.model_base import Base
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    nick_name = Column(String(64))
    password = Column(String(128))
    depart_id = Column(Integer)

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

    def __repr__(self):
        return "<User(name='%s', nick_name='%s', depart_id=%s)>" % (
                   self.name, self.nick_name, self.depart_id)

if __name__ == '__main__':
    # user = User()
    # user.name='zjh'
    # user.nick_name='测试'
    # user.depart_id=1

    user = User.parse_from_dic({"name": "zjh", "nick_name": "\u6d4b\u8bd5", "depart_id": 1})
    import json
    print(json.dumps(dict(user)))