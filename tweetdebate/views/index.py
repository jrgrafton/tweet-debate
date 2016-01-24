from flask import Blueprint, render_template
from tweetdebate.models import Question
from tweetdebate.models import Vote

mod = Blueprint('index', __name__)

@mod.route('/')
@mod.route('/home')
def home():
    return render_template('home.html')
