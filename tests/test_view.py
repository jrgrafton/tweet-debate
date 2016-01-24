"""
test_views.py - tests views
"""

from appengine_fixture_loader.loader import load_fixture
from tweetdebate.models import Question
from tweetdebate.models import State
from tweetdebate.views import tasks
from test_base import TestBase

class TestView(TestBase):
    def setUp(self):
        return super(TestView, self).setUp()

    def tearDown(self):
        self.testbed.deactivate()

    def test_view_tasks_twitter_post_status(self):
        load_fixture('tests/states.json', kind={'State': State})
        load_fixture('tests/questions.json', 
                        kind={'Question': Question,'State': State})

        result = tasks.__dict__["twitter_post_status"](1)
        assert "Posted new status" in result[0]
        assert result[1] == 200

        result = tasks.__dict__["twitter_post_status"](60*24*365*100)
        assert result[0] == "New question not ready"
        assert result[1] == 200

    def test_view_tasks_twitter_post_status_unstarted(self):
        load_fixture('tests/states.json', kind={'State': State})
        load_fixture('tests/questions_unstarted.json', 
                        kind={'Question': Question})

        # No last question so should always post something
        result = tasks.__dict__["twitter_post_status"](60*24*365*100)
        assert "Posted new status" in result[0]
        assert result[1] == 200

    def test_view_tasks_twitter_post_status_complete(self):
        load_fixture('tests/states.json', kind={'State': State})
        load_fixture('tests/questions_complete.json', 
                        kind={'Question': Question})

        # No last question so should always post something
        result = tasks.__dict__["twitter_post_status"](1)
        assert result[0] == "New question not ready"
        assert result[1] == 200

    def test_view_tasks_is_time_for_new_question(self):
        load_fixture('tests/questions.json', 
                        kind={'Question': Question,'State': State})
        
        # 1 minute cadence should be true
        result = tasks.__dict__["__is_time_for_new_question"](1)
        assert result == True

        # Should always be false for 100 years interval!
        result = tasks.__dict__["__is_time_for_new_question"](60*24*365*100)
        assert result == False
    
    def test_view_tasks_is_time_for_new_question_unstarted(self):
        load_fixture('tests/questions_unstarted.json', 
                        kind={'Question': Question})
        
        # 1 minute cadence should be true
        result = tasks.__dict__["__is_time_for_new_question"](1)
        assert result == True

        # Should always be false for 100 years interval!
        result = tasks.__dict__["__is_time_for_new_question"](60*24*365*100)
        assert result == True

    def test_404(self):
        rv = self.app.get('/missing')
        assert rv.status == '404 NOT FOUND'
        assert 'Sorry, Nothing at this URL.' in rv.data

#if __name__ == '__main__':
#    unittest.main()