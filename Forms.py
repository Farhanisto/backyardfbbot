from flask_wtf import Form
from wtforms.fields import StringField

from wtforms.validators import DataRequired



class BackyardForm(Form):



	comment = StringField('comment', validators=[DataRequired()])




