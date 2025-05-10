from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, RadioField, SelectMultipleField, TextAreaField
from wtforms.validators import DataRequired
from wtforms.widgets import ListWidget, CheckboxInput

class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class SurveyForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    birth_date = DateField('Birth Date', format='%Y-%m-%d', validators=[DataRequired()])
    education_level = SelectField(
        'Education Level',
        choices=[
            ('High School', 'High School'),
            ("Bachelor's", "Bachelor's"),
            ("Master's", "Master's"),
            ('PhD', 'PhD')
        ],
        validators=[DataRequired()]
    )
    city = StringField('City', validators=[DataRequired()])
    gender = RadioField(
        'Gender',
        choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
        validators=[DataRequired()]
    )
    models = MultiCheckboxField(
        'Models Tried',
        choices=[
            ('ChatGPT', 'ChatGPT'),
            ('Bard', 'Bard'),
            ('Claude', 'Claude'),
            ('Copilot', 'Copilot')
        ],
        validators=[DataRequired()]
    )
    chatgpt_cons = TextAreaField('ChatGPT Cons')
    bard_cons = TextAreaField('Bard Cons')
    claude_cons = TextAreaField('Claude Cons')
    copilot_cons = TextAreaField('Copilot Cons')
    use_case = StringField('Use Case', validators=[DataRequired()])
