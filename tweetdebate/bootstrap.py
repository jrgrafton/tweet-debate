from tweetdebate.models import GameStatus
from tweetdebate.models import Question

class Bootstrap(object):
    """Loads initial fixtures into DB"""
    game_status = None
    questions = None
    bootstrap_json = None

    def __init__(self):
        game_status = GameStatus.query().get()
        questions = Question.query().get()

    def activate(self):        
        if game_status is None or questions is None:
            data_file = open(os.path.join(__location__, 'bootstrap.json'))  
            self.bootstrap_json = json.load(data_file)
            self.loadQuestions()
            self.loadGameStatus()
            logging.info('load_default_game_status: %s' % self.bootstrap_json["gamestatus"]["states"])
    
    def loadQuestions(self):
        return
    
    def loadGameStatus(self):
        return