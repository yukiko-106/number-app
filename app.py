import os
import logging
from flask import Flask, request, render_template, redirect, url_for, flash, session
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Import and initialize database
from models import db, User, AdminSession

# Initialize the app with the extension
db.init_app(app)

with app.app_context():
    # Create all tables
    db.create_all()
    app.logger.info("Database tables created successfully")
    
    # Migrate any existing CSV data
    csv_file = "user_log.csv"
    if os.path.exists(csv_file):
        try:
            with open(csv_file, newline='', encoding='utf-8') as f:
                import csv as csv_module
                reader = csv_module.reader(f)
                migrated_count = 0
                
                for row in reader:
                    if len(row) >= 2:
                        name, number = row[0], int(row[1])
                        
                        # Check if user already exists in database
                        existing_user = User.query.filter_by(name=name).first()
                        if not existing_user:
                            user = User(name=name, number=number)
                            db.session.add(user)
                            migrated_count += 1
                
                if migrated_count > 0:
                    db.session.commit()
                    app.logger.info(f"Migrated {migrated_count} users from CSV to database")
                    
                    # Backup and remove CSV file
                    os.rename(csv_file, f"{csv_file}.backup")
                    app.logger.info("CSV file backed up and removed")
                
        except Exception as e:
            app.logger.error(f"Error migrating CSV data: {e}")
            db.session.rollback()

def get_next_number():
    """Get the next available number for assignment"""
    last_user = User.query.order_by(User.number.desc()).first()
    return (last_user.number + 1) if last_user else 1

@app.route("/", methods=["GET", "POST"])
def index():
    """Main page with user registration form"""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        
        if not name:
            flash("名前を入力してください。", "error")
            return render_template("index.html")
        
        # Check if name already exists in database
        existing_user = User.query.filter_by(name=name).first()
        if existing_user:
            flash(f"{name} さんには既に番号 {existing_user.number} が割り当てられています。", "info")
            return render_template("index.html")
        
        try:
            # Assign new number
            assigned_number = get_next_number()
            
            # Create new user in database
            new_user = User(name=name, number=assigned_number)
            db.session.add(new_user)
            db.session.commit()
            
            flash(f"{name} さんの番号は {assigned_number} です。", "success")
            app.logger.info(f"Saved user {name} with number {assigned_number} to database")
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error saving user to database: {e}")
            flash("データの保存に失敗しました。もう一度お試しください。", "error")
    
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Admin login page"""
    if request.method == "POST":
        password = request.form.get("password", "").strip()
        
        # Check if password matches (you can change this password)
        if password == "osakano123":
            session['logged_in'] = True
            flash("ログインしました。", "success")
            return redirect(url_for('admin'))
        else:
            flash("パスワードが間違っています。", "error")
    
    return render_template("login.html")

@app.route("/admin")
def admin():
    """Admin page showing all registered users (login required)"""
    # Check if user is logged in
    if not session.get('logged_in'):
        flash("管理者ページにアクセスするにはログインが必要です。", "error")
        return redirect(url_for('login'))
    
    # Get all users from database, sorted by number
    users = User.query.order_by(User.number).all()
    user_list = [(user.name, user.number) for user in users]
    return render_template("admin.html", users=user_list, total_users=len(user_list))

@app.route("/logout")
def logout():
    """Logout from admin session"""
    session.pop('logged_in', None)
    flash("ログアウトしました。", "success")
    return redirect(url_for('index'))

@app.route("/reset")
def reset():
    """Reset all data (for development/testing purposes)"""
    if not session.get('logged_in'):
        flash("管理者権限が必要です。", "error")
        return redirect(url_for('login'))
    
    try:
        # Delete all users from database
        User.query.delete()
        db.session.commit()
        flash("全てのデータがリセットされました。", "success")
        app.logger.info("All user data reset from database")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error resetting data: {e}")
        flash("データのリセットに失敗しました。", "error")
    
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

import os

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///data.db')

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///db.sqlite3')

db = SQLAlchemy(app)

from dotenv import load_dotenv
load_dotenv()

