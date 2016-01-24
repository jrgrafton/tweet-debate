"""
test_model.py - tests models
"""

from appengine_fixture_loader.loader import load_fixture
from tweetdebate.models import Question
from tweetdebate.models import State
from test_base import TestBase

class TestModel(TestBase):
    def setUp(self):
        return super(TestModel, self).setUp()

    def tearDown(self):
        self.testbed.deactivate()

    def test_model_state(self):
        # Load fixtures
        load_fixture('tests/states.json', kind={'State': State})
        load_fixture('tests/questions.json', 
                        kind={'Question': Question,'State': State})

        question_entity = Question.get_current_question()
        State.update_state_scores(question_entity.state_scores)

        state_entity = State.get_state_by_abbreviation("CA")
        assert state_entity.party_score_votes[0] == 1
        assert state_entity.party_score_votes[1] == 0

        state_entity = State.get_state_by_abbreviation("WA")
        assert state_entity.party_score_votes[0] == 0
        assert state_entity.party_score_votes[1] == 1

        state_entity = State.get_state_by_abbreviation("NY")
        assert state_entity.party_score_votes[0] == 0
        assert state_entity.party_score_votes[1] == 0

    def test_model_question(self):
        # Load fixtures
        load_fixture('tests/questions.json', 
                        kind={'Question': Question,'State': State})

        # Check get next questions
        question_entity = Question.get_next_question()
        assert question_entity.key.id() == "q3"

        # Check get last question start  time
        current_question_start_time = Question.get_current_question_start_time()
        current_question_start_time_string = str(current_question_start_time)
        assert current_question_start_time_string == "2016-01-23 00:00:00"

    def test_model_question_unstarted(self):
        # Load fixtures
        load_fixture('tests/questions_unstarted.json', 
                        kind={'Question': Question})

        # Check get next questions
        question_entity = Question.get_next_question()
        assert question_entity.key.id() == "q1"

        # Check get current question start time
        current_question_start_time = Question.get_current_question_start_time()
        assert current_question_start_time == None

    def test_model_question_complete(self):
        # Load fixtures
        load_fixture('tests/questions_complete.json', 
                        kind={'Question': Question})

        # Check get next questions
        question_entity = Question.get_next_question()
        assert question_entity == None

        # Check get current question start  time
        current_question_start_time = Question.get_current_question_start_time()
        assert current_question_start_time == None
    
#if __name__ == '__main__':
#    unittest.main()