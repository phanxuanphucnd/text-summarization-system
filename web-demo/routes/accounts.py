from flask import request, render_template, session, redirect
from . import routes

from helpers import users


@routes.route("/login", methods=['POST', 'GET'])
def login():
    if 'user_name' in session:
        return redirect('/')

    error_login = ""
    data = {"success": False}
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        login_user = users.find_one({'user_name': user_name})

        if not login_user is None:
            if (login_user['password'] == request.form.get('password')):
                session['user_name'] = user_name
                data['success'] = True
                return redirect('/')

        data['success'] = False
        error_login = 'Invalid username or password. Please try again!'
        return render_template('login.html', error_login=error_login)

    if request.method == 'GET':
        return render_template('login.html', error_login=error_login)


@routes.route('/register', methods=['POST', 'GET'])
def register():
    if 'user_name' in session:
        return redirect('/')

    if request.method == 'POST':
        email = request.form.get('email')
        phone = request.form.get('phone')
        user_name = request.form.get('user_name')
        password = request.form.get('password')
        re_password = request.form.get('re_password')

        if (re_password == password):
            hashpass = password
            existing_user = users.find_one(
                {'user_name': user_name})

            if not existing_user:
                users.insert(
                    {'email': email, 'phone': phone, 'user_name': user_name, 'password': hashpass})
                print(users)
                return redirect('/login')
            else:
                error_register = 'That username already exists!'
                return render_template('register.html', error_register=error_register)
        else:
            error_register = "Type in the wrong password. Please check it again."
            return render_template('register.html', error_register=error_register)
    else:
        error_register = ""
        return render_template('register.html', error_register=error_register)


@routes.route('/logout')
def logout():
    session.pop('user_name', None)
    return redirect('/login')
