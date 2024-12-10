import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.form.widgets import Select2Widget
import psycopg2

from src.models import Lesson, Employee, Groups, Workload, WorkloadContainer

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost:5432/workload'
app.config['FLASK_ADMIN_SWATCH'] = 'simplex'


class WorkloadAdmin(ModelView):
    column_list = ['lesson', 'type', 'groups', 'workload']
    form_columns = ['type', 'workload', 'lesson', 'groups']
    form_args = {
        'groups': {
            'widget': Select2Widget(multiple=True)
        }
    }


class LessonAdmin(ModelView):
    column_list = ['name', 'year', 'semester','stream', 'faculty']
    form_columns = ['name', 'year', 'semester', 'stream','faculty', 'workloads']
    form_args = {
        'workloads': {
            'widget': Select2Widget(multiple=True)
        }
    }


class EmployeeAdmin(ModelView):
    column_list = ['name']
    form_columns = ['name', 'lessons']


class GroupAdmin(ModelView):
    column_list = ['name', 'students_count']
    form_columns = ['name', 'students_count']

class CompetencyAdmin(ModelView):
    column_list = ['name']
    form_columns = ['name']

class WorkloadContainerAdmin(ModelView):
    column_list = ['employee', 'workloads', 'sum_workload']
    form_columns = ['employee', 'workloads']


db = SQLAlchemy(app)
admin = Admin(app, name='Workload Admin', template_mode='bootstrap4')

admin.add_view(WorkloadAdmin(Workload, db.session))
admin.add_view(LessonAdmin(Lesson, db.session))
admin.add_view(EmployeeAdmin(Employee, db.session))
admin.add_view(GroupAdmin(Groups, db.session))
admin.add_view(WorkloadContainerAdmin(WorkloadContainer, db.session))

if __name__ == "__main__":
    app.run(debug=True)
