from flask import Blueprint,request,jsonify,render_template
from flask_login import current_user,login_user,logout_user,login_required
from util import getUserWord,getUserWordCount,extendProgress

from db import session,Task,UserTag,Note,Tag,HistoryTask,User,Word,Progress
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import and_

from datetime import date

main=Blueprint('main',__name__)

#返回error
def error(dic):
    dic['result']='error'
    return jsonify(dic)
#返回success
def success(dic):
    dic['result']='success'
    return jsonify(dic)

#错误码
@main.errorhandler(401)
def page_unauthenticated(error):
    return render_template('401.html'),401
@main.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'),404

@main.route('/',methods=['GET'])
def index():
    return render_template('index.html')

@main.route('/login',methods=['POST'])
def login():
    name = request.form.get("name")
    password = request.form.get("password")
    try:
        user = session.query(User).filter(User.name==name).one()
        if user.password==password:
            login_user(user)
            return success({})
        else:
            return error({'message':'用户名或密码错误！'})
    except NoResultFound:
        return error({"message": "用户名不存在！"})

@main.route('/logout',methods=['POST','GET'])
@login_required
def logout():
    logout_user()
    return success({})

@main.route('/register',methods=['POST'])
def register():
    if current_user is None:
        return error({'message':'当前有用户登录！'})
    name=request.form['name']
    password=request.form['password']
    if name is None or password is None:
        return error(message='错误！'), 404
    user=User(name=name,password=password)
    User.insert(user)
    login_user(user)
    return success({'message':'注册成功！'})

@main.route('/jidanci',methods=['GET','POST'])
@login_required
def jidanci():
    return render_template('jidanci.html')
    # #获取当前进度
    # if current_user.tmpJidanci is None:
    #     current_user.tmpJidanci=iter(getUserWord(current_user,100))
    # try:
    #     return render_template('jidanci.html',next(current_user.tmpJidanci))
    # #如果当前数据已被全部取出，再从数据表中取出100个
    # except StopIteration:
    #     tmp=getUserWord(current_user,100)
    #     #如果progress数据表中没有数据，则从word表中再进行添加，暂定1000个
    #     if len(tmp)==0:
    #         #先假设word表的ID没有变化，想用原生的SQL语句弄，快点的
    #         quickExtendProgress(current_user,1000)
    #         tmp=getUserWord(current_user,100)
    #         if len(tmp)==0:
    #             slowExtendProgress(current_user,1000)
    #             tmp=getUserWord(current_user,100)
    #             if len(tmp)==0:
    #                 return jsonify({'result':'complete','message':'恭喜您已完成所有复习！'})
    #     current_user.tmpJidanci=iter(getUserWord(current_user,100))
    #     return render_template('jidanci.html',next(current_user.tmpJidanci))

@main.route('/today_word',methods=['GET'])
@login_required
def todayWord():
    if current_user.task is None:
        current_user.task=Task(user=current_user,wordNumPerDay=0)
        session.commit()
    if session.query(HistoryTask).filter(HistoryTask.user==current_user,HistoryTask.taskTime==date.today()).count()==0:
        history=HistoryTask(userId=current_user.id,taskTime=date.today(),plan=current_user.task.wordNumPerDay,complete=0)
        session.add(history)
        session.commit()
    else:
        history=session.query(HistoryTask).filter(HistoryTask.user==current_user,HistoryTask.taskTime==date.today()).first()
    need=history.plan-history.complete
    if need<=0:
        return success({'words':[]})
    count=session.query(Word).filter(Word.progresses.any(and_(Progress.progress<5,Progress.userId==current_user.id))).count()
    try:
        if count<need:
            extendProgressCount=extendProgress(current_user, 1000)
        if count==0 and extendProgressCount.rowcount==0:
            return error({'message':'您已背完所有单词！'})
        progresses=session.query(Progress).filter(Progress.user==current_user,Progress.progress<5).order_by(Progress.progress).limit(need).all()
        print(progresses)
        words=[progress.word.asDict() for progress in progresses]
        return success({'words':words})
    except Exception as e:
        print(e)
        import traceback
        traceback.print_exc()
        session.rollback()
        return error({'message':"抱歉出现错误，请发送详细内容到hantaouser@163.com"})

@main.route('/recite',methods=['POST'])
def recite():
    wordId=request.form['wordId']
    remember=request.form['remember']
    try:
        if session.query(Progress).filter(Progress.user==current_user,Progress.wordId==wordId).count()==0:
            progress=Progress(user=current_user,wordId=wordId)
            session.add(progress)
        else:
            progress=session.query(Progress).filter(Progress.user==current_user,Progress.wordId==wordId).first()

        if session.query(HistoryTask).filter(HistoryTask.user==current_user,HistoryTask.taskTime==date.today()).count()==0:
            history=HistoryTask(userId=current_user.id,taskTime=date.today(),plan=current_user.task.wordNumPerDay,complete=0)
            session.add(history)
        else:
            history=session.query(HistoryTask).filter(HistoryTask.user==current_user,HistoryTask.taskTime==date.today()).first()

        if remember:
            progress.progress=progress.progress+1
            history.complete=history.complete+1
        else:
            progress.progress=progress.progress-1
            if progress.progress<-5:
                progress.progress=-5
        session.commit()
        return success({})
    except Exception as e:
        print(e)
        session.rollback()
        return error({'message':"抱歉出现错误，请发送详细内容到hantaouser@163.com"})

@main.route('/setting',methods=['GET'])
@login_required
def setting():
    if current_user.task is None:
        current_user.task=Task(user=current_user,wordNumPerDay=0)
        session.commit()
    return render_template('setting.html',tags=Tag.query_many(),wordNumPerDay=current_user.task.wordNumPerDay)

@main.route('/current_tag',methods=['GET'])
@login_required
def getCurrentTag():
    tagIds=[tag.id for tag in current_user.tags]
    return success({'tagIds':tagIds})

@main.route('/current_task',methods=['GET'])
@login_required
def getCurrentTask():
    return success({'wordNumPerDay':current_user.task.wordNumPerDay})

@main.route('/update_tag',methods=['POST'])
@login_required
def updateTag():
    tagIds=request.form.getlist('tags')
    print(type(tagIds))
    print(tagIds)
    try:
        current_user.tags=[]
        session.commit()
        for tagId in tagIds:
            # if session.query(UserTag).filter(UserTag.userId==current_user.id,UserTag.tagId==tagId).count()==0:
            # session.add(UserTag(userId=current_user.id,tagId=tagId))
            current_user.tags.append(Tag.query_one(id=tagId))
        session.commit()
        return success({})
    except Exception as e:
        print(e)
        session.rollback()
        return error({'message':"抱歉出现错误，请发送详细内容到hantaouser@163.com"})

@main.route('/update_task',methods=['POST'])
@login_required
def updateTask():
    num=request.form['wordNumPerDay']
    try:
        if current_user.task is None:
            current_user.task=Task(wordNumPerDay=num)
        else:
            current_user.task.wordNumPerDay=num
        session.commit()
        return success({})
    except:
        session.rollback()
        return error({'message':"抱歉出现错误，请发送详细内容到hantaouser@163.com"})

@main.route('/add_note',methods=['POST'])
@login_required
def addNote():
    wordId=request.form['wordId']
    note=request.form['note']
    try:
        if Note.query_count(userId=current_user.id,wordId=wordId)==0:
            session.add(Note(userId=current_user.id,wordId=wordId,note=note))
        else:
            tmp=Note.query_one(userId=current_user.id,wordId=wordId)
            tmp.note=note
        session.commit()
        return success({})
    except:
        session.rollback()
        return error({'message':"抱歉出现错误，请发送详细内容到hantaouser@163.com"})

@main.route('/get_notes',methods=['GET'])
def getNotes():
    wordId=request.args['wordId']
    notes=[note.note for note in Note.query_many(wordId=wordId)]
    return success({'notes':notes})
