from werkzeug.utils import secure_filename
from app import app, db
from flask_login import current_user, login_user
from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, RegistrationForm, MarketSearchForm, FileUploadForm
from app.models import User, MarketRequest, UploadFile
from flask_login import logout_user, login_required
import sqlalchemy as sa
from app.api_requests import MarketSearchAPI


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/index')
@login_required
def index():
    user = db.first_or_404(sa.select(User).where(User.username == current_user.username))
    return render_template('index.html', title='Home', user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    print(form.password)
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    print("username :", form.username.data)
    if form.validate_on_submit():
        print("----validate_on_submit----")
        get_user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        print(get_user)
        if get_user is None:
            filename = secure_filename(form.profile_picture.data.filename)
            form.profile_picture.data.save(app.config.get('UPLOAD_FOLDER') + '\\' + filename)

            user = User(
                username=form.username.data,
                firstname=form.firstname.data,
                lastname=form.lastname.data,
                gender=int(form.gender.data),
                email=form.email.data,
                profile_picture=filename)

            user.set_password(form.password.data)

            db.session.add(user)
            db.session.commit()

            login_user(user)
            flash('Congratulations, you are now a registered test_user!')

            return redirect(url_for('index'))
        else:
            flash('Username already exists!')
            return redirect(url_for('test_formulaire'))
    return render_template('register.html', title='register', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/user/<username>")
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))

    return render_template('user.html', user=user)


@app.route("/users")
def users():
    users = db.session.execute(sa.select(User)).scalars().all()
    return render_template("list_users.html", users=users)


@app.route("/historic_company", methods=['GET', 'POST'])
@login_required
def ticker_infos():
    tickers = db.session.execute(
        sa.select(MarketRequest).where(MarketRequest.user_id == current_user.id)).scalars().all()
    print(tickers)
    return render_template("ticker_infos.html", tickers=tickers)


@app.route("/market_search", methods=['GET', 'POST'])
@login_required
def market_search():
    form = MarketSearchForm()
    if form.validate_on_submit():
        flash(f'Search requested for symbol {form.symbol.data}')
        api_request = MarketSearchAPI()
        result = api_request.search_quote(str(form.symbol.data).upper())
        print(result)
        ticker_market = MarketRequest(symbol=result["symbol"],
                                      company_name=result["companyName"],
                                      price=result['primaryData']["askPrice"],
                                      net_change=result['primaryData']["netChange"],
                                      user_id=current_user.id
                                      )
        db.session.add(ticker_market)
        db.session.commit()
        return redirect(url_for('ticker_infos', userid=current_user.id, ticker=result["symbol"]))
    return render_template("market_search.html", form=form)


@app.route("/upload_and_analyze", methods=['GET', 'POST'])
@login_required
def upload_and_analyze():
    files_uploaded = db.session.execute(
            sa.select(UploadFile).where(UploadFile.user_id == current_user.id)).scalars().all()
    form = FileUploadForm()
    if form.validate_on_submit():
        filename = secure_filename(form.file.data.filename)
        form.file.data.save(app.config.get('UPLOAD_FOLDER') + '\\' + filename)
        upload_file = UploadFile(
            title=form.title.data,
            filename=filename,
            user_id=current_user.id
        )
        db.session.add(upload_file)
        db.session.commit()
        return redirect(url_for(("upload_and_analyze")))
    return render_template("upload_and_analyze.html", form=form, files_uploaded=files_uploaded)
