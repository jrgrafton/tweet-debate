"""
test_model.py - tests models
"""

from appengine_fixture_loader.loader import load_fixture

from tweetdebate.models import Question
from tweetdebate.models import State
from tweetdebate.models import User
from tweetdebate.models import Vote

from test_base import TestBase

class TestModel(TestBase):
    def setUp(self):
        return super(TestModel, self).setUp()

    def tearDown(self):
        self.testbed.deactivate()

    def test_model_user(self):
        # Load fixtures
        load_fixture('tests/states.json', kind={'State': State})
        load_fixture('tests/questions.json', 
                        kind={'Question': Question,'State': State})

        current_question_entity = Question.get_current_question()
        User.add_user_vote(None, 
                          "jrgrafton_test",
                          "https://pbs.twimg.com//profile_images//440698495// \
                          9929_128442162134_504357134_2556732_5649977_n_\
                          bigger.jpg",
                          Vote(
                            question = current_question_entity.key,
                            replyid = "692368266292023296",
                            state_abbreviation = "CA",
                            party = 0,
                            sway_points = 40
                          ))

        # Ensure user was created
        user_entity = User.query_by_userid("jrgrafton_test").fetch()
        assert len(user_entity) == 1
        assert user_entity[0].sway_points == User.get_starting_sway_points() - \
                                             40
        assert user_entity[0].userid == "jrgrafton_test"
        assert "https" in user_entity[0].profile_image_url
        assert user_entity[0].votes[0].question == current_question_entity.key
        assert user_entity[0].votes[0].replyid == "692368266292023296"
        assert user_entity[0].votes[0].state_abbreviation == "CA"
        assert user_entity[0].votes[0].party == 0

        # Ensure a reply to a different question is tallied
        next_question_entity = Question.get_current_question()
        User.add_user_vote(user_entity[0],
                          "jrgrafton_test",
                          "https://pbs.twimg.com//profile_images//440698495// \
                          9929_128442162134_504357134_2556732_5649977_n_\
                          bigger.jpg",
                          Vote(
                            question = next_question_entity.key,
                            replyid = "692368266292023297",
                            state_abbreviation = "WA",
                            party = 1,
                            sway_points = 10
                          ))

        # Ensure new vote was collated under existing user
        user_entity = User.query_by_userid("jrgrafton_test").fetch()
        assert len(user_entity) == 1
        assert len(user_entity[0].votes) == 2
        assert user_entity[0].sway_points == User.get_starting_sway_points() - \
                                             (40 + 10)
        # Verify integrity of new vote
        assert user_entity[0].votes[1].question == next_question_entity.key
        assert user_entity[0].votes[1].replyid == "692368266292023297"
        assert user_entity[0].votes[1].state_abbreviation == "WA"
        assert user_entity[0].votes[1].party == 1

        # Verify integrity of old vote
        assert user_entity[0].userid == "jrgrafton_test"
        assert "https" in user_entity[0].profile_image_url
        assert user_entity[0].votes[0].question == current_question_entity.key
        assert user_entity[0].votes[0].replyid == "692368266292023296"
        assert user_entity[0].votes[0].state_abbreviation == "CA"
        assert user_entity[0].votes[0].party == 0
        
    def test_model_state(self):
        # Load fixtures
        load_fixture('tests/states.json', kind={'State': State})
        load_fixture('tests/questions.json', 
                        kind={'Question': Question,'State': State})

        question_entity = Question.get_current_question()
        State.update_state_scores_for_completed_question(question_entity)

        state_entity = State.get_state_by_abbreviation("CA")
        assert state_entity.party_score_votes[0] == 0
        assert state_entity.party_score_votes[1] == 1
        assert state_entity.party_score_sway[0] == 5
        assert state_entity.party_score_sway[1] == 500
        assert state_entity.last_winning_party == 1

        state_entity = State.get_state_by_abbreviation("WA")
        assert state_entity.party_score_votes[0] == 0
        assert state_entity.party_score_votes[1] == 1
        assert state_entity.party_score_sway[0] == 50
        assert state_entity.party_score_sway[1] == 100
        assert state_entity.last_winning_party == 1

        # Random winner is allocated for state drawing
        state_entity = State.get_state_by_abbreviation("TX")
        assert state_entity.party_score_votes[0] == 1 or \
               state_entity.party_score_votes[1] == 1
        assert state_entity.party_score_sway[0] == 80
        assert state_entity.party_score_sway[1] == 70
        assert state_entity.last_winning_party != None

        # What happens when state hasn't been voted on?
        state_entity = State.get_state_by_abbreviation("NY")
        assert state_entity.party_score_votes[0] == 0 or \
               state_entity.party_score_votes[1] == 0
        assert state_entity.last_winning_party != None

        assert State.is_valid_state("CA") == True
        assert State.is_valid_state("WA") == True
        assert State.is_valid_state("INVALID") == False

    def test_model_question(self):
        # Load fixtures
        load_fixture('tests/states.json', kind={'State': State})
        load_fixture('tests/questions.json', 
                        kind={'Question': Question,'State': State})
        question_entity = Question.get_current_question()

        # Check current question
        assert question_entity.key.id() == "q2"
        State.update_state_scores_for_completed_question(question_entity)
        Question.tally_college_and_vote_scores(question_entity)

        # NY and TX was a draw so random 2 votes will be added
        assert question_entity.vote_score[0] == (505 + 120 + 100 + 150) or \
                                                (505 + 120 + 100 + 150) + 1 or \
                                                (505 + 120 + 100 + 150) + 2
        assert question_entity.vote_score[1] == (510 + 240 + 100 + 150) or \
                                                (510 + 240 + 100 + 150) +1 or \
                                                (510 + 240 + 100 + 150) +2 

        # NY and TX was a draw so could go either way (29, 38)
        assert question_entity.college_score[0] == 0 or 29 or 38 or (29 + 38)
        assert question_entity.college_score[1] == (55 + 12) + 0  or \
                                                   (55 + 12) + 29 or \
                                                   (55 + 12) + 38 or \
                                                   (55 + 12) + (29 + 38)

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
