from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import SQLAlchemyError
import os

app = Flask(__name__)
CORS(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'library.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

MAX_BORROW_LIMIT = 5

db = SQLAlchemy(app)
jwt = JWTManager(app)


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'message': 'Token 已过期，请重新登录',
        'error': 'token_expired'
    }), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'message': '无效的 Token',
        'error': 'invalid_token'
    }), 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        'message': '缺少认证 Token，请先登录',
        'error': 'authorization_required'
    }), 401


@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'message': 'Token 已被撤销',
        'error': 'token_revoked'
    }), 401


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    borrow_records = db.relationship('BorrowRecord', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'is_admin': self.is_admin
        }


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text)
    total_copies = db.Column(db.Integer, default=1)
    available_copies = db.Column(db.Integer, default=1)
    borrow_records = db.relationship('BorrowRecord', backref='book', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'description': self.description,
            'total_copies': self.total_copies,
            'available_copies': self.available_copies
        }


class BorrowRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    borrow_date = db.Column(db.DateTime, default=datetime.utcnow)
    return_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='borrowed')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'book_title': self.book.title,
            'username': self.user.username,
            'borrow_date': self.borrow_date.strftime('%Y-%m-%d %H:%M:%S') if self.borrow_date else None,
            'return_date': self.return_date.strftime('%Y-%m-%d %H:%M:%S') if self.return_date else None,
            'status': self.status
        }


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': '用户名和密码不能为空'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message': '用户名已存在'}), 400

    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': '注册成功', 'user': user.to_dict()}), 201


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({'message': '用户名或密码错误'}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({
        'message': '登录成功',
        'access_token': access_token,
        'user': user.to_dict()
    }), 200


@app.route('/api/books', methods=['GET'])
@jwt_required()
def get_books():
    books = Book.query.all()
    return jsonify([book.to_dict() for book in books]), 200


@app.route('/api/books/<int:book_id>', methods=['GET'])
@jwt_required()
def get_book(book_id):
    book = Book.query.get_or_404(book_id)
    return jsonify(book.to_dict()), 200


@app.route('/api/books', methods=['POST'])
@jwt_required()
def create_book():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    if not current_user.is_admin:
        return jsonify({'message': '只有管理员可以添加图书'}), 403

    required_fields = ['title', 'author', 'isbn']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'message': f'{field} 不能为空'}), 400

    if Book.query.filter_by(isbn=data['isbn']).first():
        return jsonify({'message': 'ISBN 已存在'}), 400

    book = Book(
        title=data['title'],
        author=data['author'],
        isbn=data['isbn'],
        description=data.get('description', ''),
        total_copies=data.get('total_copies', 1),
        available_copies=data.get('total_copies', 1)
    )

    db.session.add(book)
    db.session.commit()

    return jsonify({'message': '图书添加成功', 'book': book.to_dict()}), 201


@app.route('/api/books/<int:book_id>', methods=['PUT'])
@jwt_required()
def update_book(book_id):
    data = request.get_json()
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    if not current_user.is_admin:
        return jsonify({'message': '只有管理员可以修改图书'}), 403

    book = Book.query.get_or_404(book_id)

    if 'title' in data:
        book.title = data['title']
    if 'author' in data:
        book.author = data['author']
    if 'isbn' in data:
        if Book.query.filter_by(isbn=data['isbn']).first() and data['isbn'] != book.isbn:
            return jsonify({'message': 'ISBN 已存在'}), 400
        book.isbn = data['isbn']
    if 'description' in data:
        book.description = data['description']
    if 'total_copies' in data:
        new_total = data['total_copies']
        if new_total < (book.total_copies - book.available_copies):
            return jsonify({'message': '总册数不能少于已借阅册数'}), 400
        book.available_copies += (new_total - book.total_copies)
        book.total_copies = new_total

    db.session.commit()

    return jsonify({'message': '图书更新成功', 'book': book.to_dict()}), 200


@app.route('/api/books/<int:book_id>', methods=['DELETE'])
@jwt_required()
def delete_book(book_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    if not current_user.is_admin:
        return jsonify({'message': '只有管理员可以删除图书'}), 403

    book = Book.query.get_or_404(book_id)

    if book.total_copies != book.available_copies:
        return jsonify({'message': '该图书还有未归还的借阅记录，无法删除'}), 400

    db.session.delete(book)
    db.session.commit()

    return jsonify({'message': '图书删除成功'}), 200


@app.route('/api/borrow', methods=['POST'])
@jwt_required()
def borrow_book():
    data = request.get_json()
    book_id = data.get('book_id')
    current_user_id = get_jwt_identity()

    if not book_id:
        return jsonify({'message': '请选择要借阅的图书'}), 400

    current_user = User.query.get(current_user_id)
    if not current_user:
        return jsonify({'message': '用户不存在，请重新登录'}), 401

    try:
        current_borrow_count = BorrowRecord.query.filter_by(
            user_id=current_user_id,
            status='borrowed'
        ).count()

        if current_borrow_count >= MAX_BORROW_LIMIT:
            return jsonify({
                'message': f'您已借阅 {current_borrow_count} 本图书，已达到最大借阅限制 {MAX_BORROW_LIMIT} 本'
            }), 400

        book = Book.query.get_or_404(book_id)

        if book.available_copies <= 0:
            return jsonify({'message': '该图书暂无可用副本'}), 400

        existing_borrow = BorrowRecord.query.filter_by(
            user_id=current_user_id,
            book_id=book_id,
            status='borrowed'
        ).first()

        if existing_borrow:
            return jsonify({'message': '您已借阅过该书，且尚未归还'}), 400

        borrow_record = BorrowRecord(
            user_id=current_user_id,
            book_id=book_id
        )

        book.available_copies -= 1

        db.session.add(borrow_record)
        db.session.commit()

        return jsonify({
            'message': '借阅成功',
            'borrow_record': borrow_record.to_dict(),
            'current_borrow_count': current_borrow_count + 1,
            'max_limit': MAX_BORROW_LIMIT
        }), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        app.logger.error(f'借阅数据库错误: {str(e)}')
        return jsonify({'message': '借阅失败，请稍后重试'}), 500
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'借阅未知错误: {str(e)}')
        return jsonify({'message': '借阅失败，请稍后重试'}), 500


@app.route('/api/return/<int:record_id>', methods=['POST'])
@jwt_required()
def return_book(record_id):
    current_user_id = get_jwt_identity()

    current_user = User.query.get(current_user_id)
    if not current_user:
        return jsonify({'message': '用户不存在，请重新登录'}), 401

    try:
        borrow_record = BorrowRecord.query.get_or_404(record_id)

        if borrow_record.user_id != current_user_id and not current_user.is_admin:
            return jsonify({'message': '您没有权限归还此图书'}), 403

        if borrow_record.status == 'returned':
            return jsonify({'message': '该图书已归还'}), 400

        book = Book.query.get(borrow_record.book_id)
        if not book:
            return jsonify({'message': '关联图书不存在'}), 404

        borrow_record.status = 'returned'
        borrow_record.return_date = datetime.utcnow()

        book.available_copies += 1

        if book.available_copies > book.total_copies:
            book.available_copies = book.total_copies

        db.session.commit()

        return jsonify({
            'message': '归还成功',
            'borrow_record': borrow_record.to_dict()
        }), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        app.logger.error(f'归还数据库错误: {str(e)}')
        return jsonify({'message': '归还失败，请稍后重试'}), 500
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'归还未知错误: {str(e)}')
        return jsonify({'message': '归还失败，请稍后重试'}), 500


@app.route('/api/borrow-records', methods=['GET'])
@jwt_required()
def get_borrow_records():
    current_user_id = get_jwt_identity()
    
    current_user = User.query.get(current_user_id)
    if not current_user:
        return jsonify({'message': '用户不存在，请重新登录'}), 401

    status = request.args.get('status')
    
    try:
        query = BorrowRecord.query
        
        if current_user.is_admin:
            if status:
                query = query.filter_by(status=status)
            records = query.order_by(BorrowRecord.borrow_date.desc()).all()
        else:
            query = query.filter_by(user_id=current_user_id)
            if status:
                query = query.filter_by(status=status)
            records = query.order_by(BorrowRecord.borrow_date.desc()).all()

        return jsonify([record.to_dict() for record in records]), 200

    except SQLAlchemyError as e:
        app.logger.error(f'查询借阅记录数据库错误: {str(e)}')
        return jsonify({'message': '查询失败，请稍后重试'}), 500
    except Exception as e:
        app.logger.error(f'查询借阅记录未知错误: {str(e)}')
        return jsonify({'message': '查询失败，请稍后重试'}), 500


@app.route('/api/current-user', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    
    current_user = User.query.get(current_user_id)
    if not current_user:
        return jsonify({'message': '用户不存在，请重新登录'}), 401

    return jsonify(current_user.to_dict()), 200


def init_db():
    with app.app_context():
        db.create_all()
        
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', is_admin=True)
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('管理员用户已创建: admin / admin123')

        if Book.query.count() == 0:
            sample_books = [
                Book(
                    title='Python编程从入门到实践',
                    author='Eric Matthes',
                    isbn='9787115428028',
                    description='本书是一本针对所有层次的Python读者而作的Python入门书。',
                    total_copies=5,
                    available_copies=5
                ),
                Book(
                    title='Flask Web开发',
                    author='Miguel Grinberg',
                    isbn='9787115408884',
                    description='本书全面介绍了用Python和Flask框架开发Web应用程序的过程。',
                    total_copies=3,
                    available_copies=3
                ),
                Book(
                    title='Vue.js实战',
                    author='梁灏',
                    isbn='9787111577041',
                    description='本书以Vue.js 2为基础，系统介绍了Vue.js的核心概念和使用方法。',
                    total_copies=4,
                    available_copies=4
                )
            ]
            for book in sample_books:
                db.session.add(book)
            db.session.commit()
            print('示例图书已添加')


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
