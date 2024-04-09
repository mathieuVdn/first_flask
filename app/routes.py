import io
import os

import pandas as pd
import sqlalchemy as sa
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user
from flask_login import logout_user, login_required
from sqlalchemy import desc
from werkzeug.utils import secure_filename

from app import app, db
from app.api_requests import MarketSearchAPI
from app.forms import LoginForm, RegistrationForm, MarketSearchForm, FileUploadForm
from app.models import User, MarketRequest, UploadFile


@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
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
            flash('error: Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        flash('success: You are now logged in!')
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        get_user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
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
            flash('success: Congratulations, you are now a registered!')
            return redirect(url_for('index'))
        else:
            flash('error: Username already exists!')
            return redirect(url_for('test_formulaire'))
    return render_template('register.html', title='register', form=form)


@app.route("/logout")
def logout():
    logout_user()
    flash('success: You are now logged out!')
    return redirect(url_for("home"))


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
    last_ticker = (
        db.session.query(MarketRequest)
        .filter_by(user_id=current_user.id)
        .order_by(desc(MarketRequest.timestamp))
        .first()
    )

    form = MarketSearchForm()
    if form.validate_on_submit():
        api_request = MarketSearchAPI()
        result = api_request.search_quote(str(form.symbol.data).upper())
        if result is not None:
            ticker_market = MarketRequest(symbol=result["symbol"],
                                          company_name=result["companyName"],
                                          price=result['primaryData']["lastSalePrice"],
                                          net_change=result['primaryData']["netChange"],
                                          user_id=current_user.id
                                          )
            db.session.add(ticker_market)
            db.session.commit()
            flash(f'success: Search requested for symbol {form.symbol.data} success')
            return redirect(url_for('market_search',
                                    userid=current_user.id,
                                ticker=result["symbol"]))
        else:
            flash(f'error: Search requested for symbol {form.symbol.data} failed')
            return redirect(url_for('market_search',
                                    userid=current_user.id,
                                    ticker=form.symbol.data))
    return render_template("market_search.html", form=form, last_ticker=last_ticker)


@app.route("/upload_and_analyze", methods=['GET', 'POST'])
@login_required
def upload_and_analyze():
    files_uploaded = db.session.execute(
            sa.select(UploadFile).where(UploadFile.user_id == current_user.id)).scalars().all()
    form_upload = FileUploadForm()
    if form_upload.validate_on_submit():
        filename = secure_filename(form_upload.file.data.filename)
        filepath = os.path.join(app.config.get('UPLOAD_FOLDER'), filename)
        form_upload.file.data.save(filepath)
        filesize = os.path.getsize(filepath)
        upload_file = UploadFile(
            title=form_upload.title.data,
            filename=filename,
            user_id=current_user.id,
            filesize=filesize
        )
        db.session.add(upload_file)
        db.session.commit()
        flash(f'success: File {filename} has been uploaded')
        return redirect(url_for(("upload_and_analyze")))
    return render_template("upload.html",
                           form_upload=form_upload,
                           files_uploaded=files_uploaded)


@app.route("/delete_file/<filename>")
@login_required
def delete_file(filename):
    file_to_delete = db.session.execute(
        sa.select(UploadFile).where(UploadFile.filename == filename, UploadFile.user_id == current_user.id)
    ).scalar()

    if file_to_delete:
        file_path = os.path.join(app.config.get('UPLOAD_FOLDER'), file_to_delete.filename)
        if os.path.exists(file_path):
            os.remove(file_path)

        db.session.delete(file_to_delete)
        db.session.commit()

        flash(f'success: File {filename} has been deleted')
    else:
        flash(f'error: File {filename} not found')

    return redirect(request.referrer)

@app.route("/analyze")
@login_required
def analyze():
    files_uploaded = db.session.execute(
        sa.select(UploadFile).where(UploadFile.user_id == current_user.id)).scalars().all()
    return render_template("analyze.html",
                           files_uploaded=files_uploaded)
@app.route("/head/<filename>")
@login_required
def head(filename):
    file_path = os.path.join(app.config.get('UPLOAD_FOLDER'), filename)
    print(file_path)
    if not os.path.exists(file_path):
        flash(f'error: File {filename} not found.')
        return redirect(url_for('upload_and_analyze'))

    df = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path)
    head_df = df.head()
    head_html = head_df.to_html(classes='table is-fullwidth is-bordered')



    return render_template("head.html",
                           filename=filename,
                          head_html=head_html)


@app.route("/infos/<filename>")
@login_required
def infos(filename):
    file_path = os.path.join(app.config.get('UPLOAD_FOLDER'), filename)
    df = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path)

    info_buffer = io.StringIO()
    df.info(buf=info_buffer)
    info_summary = info_buffer.getvalue()
    info_buffer.close()
    print(info_summary)
    total_entries = None
    for line in info_summary.split('\n'):
        if line.strip().startswith("RangeIndex"):
            total_entries = line.strip().replace("RangeIndex: ", "")
            break

    info_table = "<table class='table is-fullwidth is-bordered'><thead><tr><th>Column</th><th>Non-Null Count</th><th>Dtype</th></tr></thead><tbody>"
    for line in info_summary.split('\n')[5:]:
        if line.strip() and not line.strip().startswith("RangeIndex"):
            parts = line.split()
            info_table += f"<tr><td>{parts[0]}</td><td>{parts[1]}</td><td>{' '.join(parts[2:])}</td></tr>"
    info_table += "</tbody></table>"

    return render_template("infos.html",
                           filename=filename,
                           infos=info_table,
                           total_entries=total_entries)


@app.route("/describe/<filename>")
@login_required
def describe(filename):
    file_path = os.path.join(app.config.get('UPLOAD_FOLDER'), filename)
    df = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path)
    description = df.describe()
    description_html = description.to_html(classes='table is-fullwidth is-bordered')

    return render_template("describe.html",
                           filename=filename,
                           description=description_html)

