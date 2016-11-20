from flask_login import UserMixin
from sqlalchemy import Column,create_engine,Table,Integer,ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects import mysql
from sqlalchemy.types import INT,VARCHAR,TEXT,DATE
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

db_config={
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'shanbei',
    'charset': 'utf8'
}

engine=create_engine('mysql+pymysql://%(user)s:%(password)s@%(host)s/%(database)s?charset=%(charset)s'%db_config,pool_recycle=10)

DBSession=sessionmaker(bind=engine,autoflush=True)
Base=declarative_base()
session=DBSession()

#辅助函数
class Addon:
    @classmethod
    def query_one(cls,*args):
        try:
            return session.query(cls).filter(*args).one()
        except:
            return None

    @classmethod
    def query_one(cls,**kwargs):
        try:
            aa=list()
            for key,value in kwargs.items():
                aa.append(getattr(cls,key)==value)
            return session.query(cls).filter(*aa).one()
        except:
            session.rollback()
            return None

    @classmethod
    def query_many(cls,*args):
        return session.query(cls).filter(*args).all()
    @classmethod
    def query_many(cls,**kwargs):
        aa=list()
        for key,value in kwargs.items():
            aa.append(getattr(cls,key)==value)
        return session.query(cls).filter(*aa).all()
    @classmethod
    def query_many_with_limit(cls,limit,**kwargs):
        aa=list()
        for key,value in kwargs.items():
            aa.append(getattr(cls,key)==value)
        return session.query(cls).filter(*aa).limit(limit).all()
#    @classmethod
#    def query_many_limit_desc(cls,limit,*args,**kwargs):
#        aa=list()
#        bb=list()
#        for key,value in kwargs.items():
#            aa.append(getattr(cls,key)==value)
#        for orderby in args:
#            bb.append(getattr(cls,key).desc())
#        return session.query(cls).filter(*aa).order_by(*bb).limit(limit).all()

#    @classmethod
#    def query_in_limit_desc(cls,col,colSet,orderby,limit):
#        return session.query(cls).filter(getattr(cls,col).in_(colSet)).order_by(getattr(cls,orderby).desc()).limit(limit).all()
    @classmethod
    def query_count(cls,*args):
        return session.query(cls).filter(*args).count()
    @classmethod
    def query_count(cls,**kwargs):
        aa=list()
        for key,value in kwargs.items():
            aa.append(getattr(cls,key)==value)
        return session.query(cls).filter(*aa).count()
    @classmethod
    def query_all(cls):
        return session.query(cls).all()
    @classmethod
    def get_query(cls):
        return session.query(cls)
    def update(self):
        session.commit()
    def insert(self):
        session.add(self)
        session.commit()

#单词标签关联表
WordTag=Table('word_tag',Base.metadata,
              Column('wordId',Integer,ForeignKey('word.id')),
              Column('tagId',Integer,ForeignKey('tag.id'))
              )
#用户标签关联表
UserTag=Table('user_tag',Base.metadata,
              Column('userId',Integer,ForeignKey('user.id')),
              Column('tagId',Integer,ForeignKey('tag.id'))
              )

#单词表
class Word(Base,Addon):
    __tablename__='word'

    id=Column(INT,primary_key=True)
    word=Column(VARCHAR(length=100),nullable=False)
    explanation=Column(TEXT)
    example=Column(TEXT)

    #单词对应的标签
    tags=relationship('Tag',secondary=WordTag,back_populates='words',lazy=True)
    #单词的笔记
    notes=relationship('Note',back_populates='word',lazy=True)
    #任务进行程度
    progresses=relationship('Progress',back_populates='word',lazy=True)

    def asDict(self):
        return {'id':self.id, 'word':self.word, 'explanation':self.explanation, 'example':self.example}

#标签表
class Tag(Base,Addon):
    __tablename__='tag'

    id=Column(INT,primary_key=True)
    tag=Column(VARCHAR(length=50),nullable=False)

    #标签对应的单词
    words=relationship('Word',secondary=WordTag,back_populates='tags',lazy=True)
    #标签对应的用户
    users=relationship('User',secondary=UserTag,back_populates='tags',lazy=True)

#用户表
class User(Base,UserMixin,Addon):
    __tablename__='user'

    id=Column(INT,primary_key=True)
    name=Column(VARCHAR(length=50),nullable=False)
    password=Column(VARCHAR(length=64),nullable=False)

    #用户的标签
    tags=relationship('Tag',secondary=UserTag,back_populates='users',lazy=True)
    #用户的任务
    task=relationship('Task',uselist=False,back_populates='user',lazy=True)
    #当前用户任务的进度
    progresses=relationship('Progress',back_populates='user',lazy=True)
    #当前用户的笔记
    notes=relationship('Note',back_populates='user',lazy=True)

    def login(cls,name,password):
        try:
            return session.query(User).filter(User.name==name,User.password==password).one()
        except:
            return None

#任务表
class Task(Base,Addon):
    __tablename__='task'

    id=Column(INT,primary_key=True)
    userId=Column(INT,ForeignKey('user.id'))
    wordNumPerDay=Column(INT,nullable=False)

    #任务对应的用户
    user=relationship('User',uselist=False,back_populates='task',lazy=True)

#历史任务
class HistoryTask(Base,Addon):
    __tablename__='history_task'

    id=Column(INT,primary_key=True)
    userId=Column(INT,ForeignKey('user.id'))
    taskTime=Column(DATE)
    plan=Column(INT)
    complete=Column(INT)

    user=relationship('User')


#用户单词进度表
class Progress(Base,Addon):
    __tablename__='progress'

    id=Column(INT,primary_key=True)
    userId=Column(INT,ForeignKey('user.id'))
    wordId=Column(INT,ForeignKey('word.id'))
    progress=Column(INT)

    user=relationship('User',uselist=False,back_populates='progresses',lazy=True)
    word=relationship('Word',uselist=False)

#笔记表
class Note(Base,Addon):
    __tablename__='note'

    id=Column(INT,primary_key=True)
    userId=Column(INT,ForeignKey('user.id'))
    wordId=Column(INT,ForeignKey('word.id'))
    note=Column(TEXT)

    user=relationship('User',uselist=False,back_populates='notes',lazy=True)
    word=relationship('Word',uselist=False,back_populates='notes',lazy=True)
