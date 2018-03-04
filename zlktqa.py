from flask import Flask,render_template,request,redirect,url_for,session,g
import config
from models import User,Question,Answer
from exts import db
from decorators import login_required

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)

@app.route('/')
@app.route('/index/')
def index():
    context={
        'questions':Question.query.order_by('-create_time').all()
    }
    return render_template('index.html',**context)

@app.route('/login/',methods=['GET','POST'])
def login():
    if request.method=='GET':
        return render_template('login.html')
    else:
        telephone=request.form.get('telephone')
        password=request.form.get('password')
        print(request.form)
        user = User.query.filter(User.telephone == telephone,User.password==password).first()
        if user:
            session['user_id']=user.id
            #如果想再31天内都不需要登录
            session.permanent=True
            return redirect(url_for('index'))
        else:
            return '用户名或密码不正确,请确认后再操作'


@app.route('/regist/',methods=['GET','POST'])
def regist():
    if request.method=='GET':
        return render_template('regist.html')
    else:
        telephone=request.form.get('telephone')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        #手机号码验证 如果被注册 就不能再注册
        user=User.query.filter(User.telephone==telephone).first()

        if user:
            return u'该手机号码被注册,请更换手机号码'
        else:
            # password1和password2是否相等
            if password1 != password2:
                return u'两次输入密码不一致'
            else:
                user=User(telephone=telephone,username=username,password=password1)
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('login'))
@app.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/question/',methods=['GET','POST'])
@login_required
def question():
    if request.method=='GET':
        return render_template('question.html')
    else:
        title=request.form.get('title')
        content=request.form.get('content')
        question=Question(title=title,content=content)
        user_id=session.get('user_id')
        user = User.query.filter(User.id == user_id).first()
        question.author=user
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('index'))

@app.route('/detail/<question_id>',methods=['POST','GET'])
def detail(question_id):
    if request.method is 'POST':
        return redirect(url_for('add_answer'))
    else:#Question.query.order_by('-create_time').all()
        context={'question':Question.query.filter(Question.id==question_id).first()}
        return render_template('detail.html',**context)

@app.route('/add_answer/',methods=['POST'])
@login_required
def add_answer():
    content=request.form.get('answer_content')
    answer = Answer(content=content)

    answer.author_id=session.get('user_id')
    question_id=request.form.get('question_id')
    answer.question_id=question_id

    db.session.add(answer)
    db.session.commit()

    return redirect(url_for('detail',question_id=question_id))


@app.context_processor
def my_context_processor():
    user_id=session.get('user_id')
    if user_id:
        user=User.query.filter(User.id==user_id).first()
        if user:
            return {'username':user.username}
    return {}
if __name__ == '__main__':
    app.run(host='0.0.0.0')
