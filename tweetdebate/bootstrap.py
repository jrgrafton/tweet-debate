import datetime
import json
import os
import logging
from tweetdebate.models import GameStatus
from tweetdebate.models import Question

class Bootstrap(object):
    """Loads initial fixtures into DB"""
    game_status = None
    questions = None
    bootstrap_json = None

    def __init__(self):
        self.game_status = GameStatus.query().get()
        self.questions = Question.query().get()

    def activate(self):        
        if self.game_status is None or self.questions is None:
            data_file = open(os.path.join(os.path.dirname(__file__),
                                          'bootstrap.json'))  
            self.bootstrap_json = json.load(data_file)
            self.load_questions()
            self.load_game_status()
            self.load_states()
    
    def load_questions(self):
        # Load questions
        logging.info('load_questions:')
        questions = self.bootstrap_json["questions"]
        for question in questions:
            image = question["image"]
            question_text = question["question_text"]
            republican = question["republican"]
            democrat = question["democrat"]
            question = Question(
                image = image,
                question_text = question_text,
                republican = republican,
                democrat = democrat)
            question.put()
    
    def load_game_status(self):
        # Load game status
        logging.info('load_game_status:')
        question_cadence_minutes = \
            self.bootstrap_json["gamestatus"]["question_cadence_minutes"]

        game_status = GameStatus(
            question_cadence_minutes = question_cadence_minutes)
        game_status.put()

    def load_states(self):
        # @TODO load states
        return True