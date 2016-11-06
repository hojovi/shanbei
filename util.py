from db import engine,session,Progress
# from db.rawsql import connection

from sqlalchemy import text

def getUserWord(user,limit):
    progresses=session.query(Progress).filter(Progress.user==user,Progress.progress<5).limit(limit).all()
    # progresses=Progress.query_many_with_limit(limit,Progress.user==user,Progress.progress<5)
    return progresses

def getUserWordCount(user):
    return Progress.query_count(Progress.user==user,Progress.progress<5)

#插入数据到progress表，用原生sql
# def quickExtendProgress(user,len):
#     #sql语句基本就是这样，有6个参数要填，分别是：
#     #用户ID，初始progress，用户ID，用户ID，用户ID，想要插入的数据条数
#     sql='''
#         insert into progress(userId,wordId,progress)
#         (select %s,word.id,%s from tag left join word
#         on exists(select * from word_tag where tagId=tag.id and wordId=word.id) and word.id>(select  isnull(max(wordId),0)  from progress where userId=%s)
#         where exists(select * from user_tag where userId=%s and tagId=tag.id) and not exists(select * from progress where userId=%s and wordId=word.id)
#         limit %s);
#     '''%(user.id,0,user.id,user.id,user.id,len)
#     # cursor=connection.cursor()
#     # effected_row=cursor.execute(sql)
#     # connection.commit()
#     # cursor.close()
#     unknown_return=engine.execute(text(sql).execution_options(autocommit=True))
#     return unknown_return

#插入数据到progress表，用原生sql
def extendProgress(user,len):
    #sql语句基本就是这样，有6个参数要填，分别是：
    #用户ID，初始progress，用户ID，用户ID，想要插入的数据条数
    sql='''
        insert into progress(userId,wordId,progress)
        (select %s,word.id,%s from tag left join word
        on exists(select * from word_tag where tagId=tag.id and wordId=word.id)
        where exists(select * from user_tag where userId=%s and tagId=tag.id) and not exists(select * from progress where userId=%s and wordId=word.id)
        limit %s);
    '''%(user.id,0,user.id,user.id,len)
    # cursor=connection.cursor()
    # effected_row=cursor.execute(sql)
    # connection.commit()
    # cursor.close()
    unknown_return=engine.execute(text(sql).execution_options(autocommit=True))
    return unknown_return
