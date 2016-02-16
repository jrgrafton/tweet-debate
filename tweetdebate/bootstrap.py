import datetime
import json
import os
import logging

from tweetdebate.models import Question
from tweetdebate.models import State

class Bootstrap(object):
    """Loads initial data into DB"""
    questions = None
    bootstrap_json = None

    def __init__(self):
        self.questions = Question.query().get()

    def activate(self):        
        if  self.questions is None:
            data_file = open(os.path.join(os.path.dirname(__file__),
                                          'bootstrap.json'))  
            self.bootstrap_json = json.load(data_file)
            self.load_questions()
            self.load_states()
    
    def load_questions(self):
        # Load questions
        logging.info('load_questions:')
        questions = self.bootstrap_json["questions"]
        for question in questions:
            image = question["image"]
            question_text = question["question_text"]
            party = question["party"]
            question = Question(
                image = image,
                question_text = question_text,
                party = party)
            question.put()

    def load_states(self):
        # Load states
        logging.info('load_states:')
        states = self.bootstrap_json["states"]
        for state in states:
            state = State(
                state_abbreviation = state["state_abbreviation"],
                college_votes = int(state["college_votes"]),
                party_score_votes = [0, 0],
                party_score_sway = [0, 0]
            )
            state.put()