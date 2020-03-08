from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from common.user import User

engine = create_engine('sqlite:///bf_chat.db?check_same_thread=False',echo=True)
Session = sessionmaker(bind=engine)
session = Session()

def get_all_users():
    users = session.query(User).all()
    return users

def add_user(user):
    session.add(user)
    session.commit()

def load_user_info(name, pwd):
    user = session.query(User).filter(and_(User.name==name, User.password==pwd)).first()
    print(user)
    return user

if __name__ == '__main__':
    # from common.user import Base
    # Base.metadata.create_all(engine)
    import hashlib

    md5 = hashlib.md5()
    md5.update('123'.encode())
    # user = User()
    # user.name = 'test'
    # user.nick_name = '测试'
    # user.password = md5.hexdigest()
    # add_user(user)
    #
    # user = User()
    # user.name = 'test1'
    # user.nick_name = '测试1'
    # user.password = md5.hexdigest()
    # add_user(user)
    #
    # user = User()
    # user.name = 'test2'
    # user.nick_name = '测试2'
    # user.password = md5.hexdigest()
    # add_user(user)

    user = load_user_info('test', md5.hexdigest())
    print(user)
