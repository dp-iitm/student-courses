from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///week7_database.sqlite3'

db = SQLAlchemy()
db.init_app(app)
app.app_context().push()


class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roll_number = db.Column(db.String, nullable=False, unique=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)
    courses_taken = db.relationship('Course', secondary='enrollments')


class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_code = db.Column(db.String, nullable=False, unique=True)
    course_name = db.Column(db.String, nullable=False)
    course_description = db.Column(db.String)
    students_enrolled = db.relationship('Student', secondary='enrollments', overlaps='courses_taken')


class Enrollments(db.Model):
    __tablename__ = 'enrollments'
    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    estudent_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    ecourse_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)


# CRUD for courses #
db.create_all()

@app.route('/courses', methods=['GET', 'POST'])
def get():
    course_list = Course.query.all()
    if course_list:
        return render_template('course_list.html', courses=course_list)
    else:
        return render_template('no_courses.html')


@app.route('/course/create', methods=['GET', 'POST'])
def post():
    if request.method == 'GET':
        return render_template('add_course.html')
    elif request.method == 'POST':
        course_code = request.form['code']
        course_name = request.form['c_name']
        course_desc = request.form['desc']
        course = Course.query.filter_by(course_code=course_code).first()
        if course:
            return render_template('course_exists.html')
        else:
            course_obj = Course(course_code=course_code,
                                course_name=course_name,
                                course_description=course_desc)
            db.session.add(course_obj)
            db.session.commit()

            current_courses = Course.query.all()

            return redirect('/courses')


@app.route('/course/<int:course_id>/update', methods=['GET', 'POST'])
def put(course_id):
    course = Course.query.filter_by(course_id=course_id).first()

    if request.method == 'GET':
        return render_template('update_course.html', course=course)
    elif request.method == 'POST':
        new_course_name = request.form['c_name']
        new_course_description = request.form['desc']

        course.course_name = new_course_name
        course.course_description = new_course_description

        db.session.commit()

        return redirect('/courses')


@app.route('/course/<int:course_id>/delete', methods=['GET', 'POST'])
def delete(course_id):
    course = Course.query.filter_by(course_id=course_id).first()
    db.session.delete(course)

    enrollments = Enrollments.query.filter_by(ecourse_id=course_id).all()
    for enrollment in enrollments:
        db.session.delete(enrollment)
    db.session.commit()

    return redirect('/')

@app.route('/course/<int:course_id>')
def course_details(course_id):
    course = Course.query.filter_by(course_id=course_id).first()
    return render_template('show_course_details.html', course=course)


# CRUD for students #


@app.route('/', methods=['GET', 'POST'])
def get_student():
    student_list = Student.query.all()
    if student_list:
        return render_template('student_list.html', students=student_list)
    else:
        return render_template('no_student.html')


@app.route('/student/create', methods=['GET', 'POST'])
def post_student():

    if request.method == 'GET':
        return render_template('add_student.html')
    elif request.method == 'POST':
        roll_number = request.form['roll']
        first_name = request.form['f_name']
        last_name = request.form['l_name']

        student = Student.query.filter_by(roll_number=roll_number).first()
        if student:
            return render_template('student_exists.html')
        else:
            student_obj = Student(roll_number=roll_number,
                                  first_name=first_name,
                                  last_name=last_name)

            db.session.add(student_obj)
            db.session.commit()

            current_students = Student.query.all()
            return redirect('/')


@app.route('/student/<int:student_id>/update', methods=['GET','POST'])
def put_student(student_id):
    student = Student.query.filter_by(student_id=student_id).first()
    if request.method == 'GET':
        courses = Course.query.all()
        return render_template('update_student.html', student=student, current_courses=courses)
    elif request.method == 'POST':
        first_name = request.form['f_name']
        last_name = request.form['l_name']
        enrolled_course_id = request.form['course']

        student.first_name = first_name
        student.last_name = last_name

        student.courses_taken.append(Course.query.filter_by(course_id=enrolled_course_id).first())

        course = Course.query.filter_by(course_id=enrolled_course_id).first()
        course.students_enrolled.append(Student.query.filter_by(student_id=student_id).first())

        db.session.commit()

        return redirect('/')


@app.route('/student/<int:student_id>/delete', methods=['GET', 'POST'])
def delete_student(student_id):
    student = Student.query.filter_by(student_id=student_id).first()
    db.session.delete(student)

    enrollments = Enrollments.query.filter_by(estudent_id=student_id).all()
    for enrollment in enrollments:
        db.session.delete(enrollment)
    db.session.commit()

    return redirect('/')


@app.route('/student/<int:student_id>')
def student_details(student_id):
    student = Student.query.filter_by(student_id=student_id).first()
    return render_template('show_student_details.html', student=student)


@app.route('/student/<int:student_id>/withdraw/<int:course_id>')
def withdraw_enrollment(student_id, course_id):
    #student = Student.query.filter_by(student_id=student_id).first()
     #course = Course.query.filter_by(course_id=course_id).first()

    enrollments = db.session.query(Enrollments).filter_by(estudent_id=student_id,ecourse_id=course_id).all()
    for enroll in enrollments:
        db.session.delete(enroll)
    db.session.commit()

    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True, port=5000)