var Debate = React.createClass({
  render: function() {
    return (
      <div>
        <CurrentQuestionInfo question={this.props.debate.current_qestion} />
        <CurrentQuestionMap state_scores={this.props.debate.current_qestion.state_scores} />
        <CastYourVote />
        <QuestionArchive archived_questions={this.props.debate.archived_questions} />
      </div>
    );
  }
});

var CurrentQuestionInfo = React.createClass({
  format_date: function(date) {
    var date = new Date(date)
    var end_date = (date.getHours() >= 12)? date.getHours() - 12 :
                    date.getHours()
    end_date += ":"
    end_date += (date.getMinutes() < 10)? "0" + date.getMinutes() :
                 date.getMinutes()
    end_date += (date.getHours() < 12)? " AM" : " PM"
  },
  render: function() {
    var end_date = this.format_date(this.props.question.end_time)
    return (
      <div id="current-question-info">
        <h1>Current question info</h1>
        <div className="question-start">{end_date}</div>
        <div className="question-text">
            <b>{this.props.question.question_text}</b>
        </div>
        <div className="vote-count">
            <i>{this.props.question.vote_count} RETWEETS</i>
        </div>
      </div>
    );
  }
});

var CurrentQuestionMap = React.createClass({
  render: function() {
    var state_scores = []
    var college_scores = [0, 0]
    this.props.state_scores.forEach(function(state_score) {
        var vote_total_republican = state_score.party_score_votes[0] +
                                    state_score.party_score_sway[0]
        var vote_total_democrat = state_score.party_score_votes[1] +
                                  state_score.party_score_sway[1]

        // Add data for college votes
        if(vote_total_republican > vote_total_democrat) {
            college_scores[0] += state_score.college_votes
        }
        else if(vote_total_democrat > vote_total_republican) {
            college_scores[1] += state_score.college_votes
        }

        state_scores.push(
            <li key={state_score.state_abbreviation}>
                votes-sway-r:{vote_total_republican}, 
                votes-sway-d:{vote_total_democrat}
            </li>
        )
    })
    return (
      <div id="current-question-map">
        <h1>Current question map</h1>
        <ul>
            {state_scores}
        </ul>
        <CurrentQuestionResult college_scores={college_scores} />
      </div>
    );
  }
});

var CurrentQuestionResult = React.createClass({
  render: function() {
    return (
      <div id="current-question-result">
        <h1>Current question result (pie chart)</h1>
        <p>
            {this.props.college_scores[0]} : {this.props.college_scores[1]}
        </p>
      </div>
    );
  }
});

var CastYourVote = React.createClass({
  render: function() {
    return (
      <div id="cast-your-vote">
        <b>CAST YOUR VOTE</b>
      </div>
    );
  }
});

var QuestionArchive = React.createClass({
  format_date: function(date_string) {
    var date = new Date(date_string)
    return date.getMonth() + "/" + 
           date.getDay() + "/" + 
           date.getFullYear().toString().substr(2, 2);
  },
  render: function() {
    var archived_questions = []
    var that = this
    this.props.archived_questions.forEach(function(archived_question) {
        var date = that.format_date(archived_question.end_time)
        archived_questions.push(
            <div key={archived_question.end_time}>
                <div>
                    <b>{date}</b>
                </div>
                <div>
                    {archived_question.college_score[0]} :
                    {archived_question.college_score[1]}
                </div>
                <div>{archived_question.random_quote.vote_text}</div>
                <div>{archived_question.random_quote.user}</div>
            </div>
        )
    })
    return (
      <div id="question-archive">
        <h1>Question Archive</h1>
        {archived_questions}
      </div>
    );
  }
});

var DEBATE = {
    "current_qestion": {
        "start_time": "2016-02-16 23:48:30.531648",  
        "image": null, 
        "question_text": "\"President Obama gave away too much, too early.\" #yes or #no #GaveAllSeeds",
        "twitterid": "699742177644060672",
        "party": 0,
        "vote_score": [],
        "college_score": [],
        "state_scores": [
            {
                "last_winning_party": null, 
                "college_votes": 55,
                "party_score_sway": [10, 50],
                "party_score_votes": [15, 20],
                "state_abbreviation": "CA"
            },
            {
                "last_winning_party": null, 
                "college_votes": 18,
                "party_score_sway": [10, 10],
                "party_score_votes": [25, 20],
                "state_abbreviation": "OH"
            }
        ],
        "vote_count": 35,
        "end_time": "2016-02-16 21:48:30.531648-08:00"
    },
    "archived_questions": [{
        "vote_score": [10, 50],
        "college_score": [332, 206],
        "question_text": "\"Americans are tired of Washington corporate interest and Democrats who are interested in politics and power\" #yes or #no #birdcorps",
        "end_time": "2016-02-16 21:48:30.531648-08:00",
        "random_quote": {
            "user": "jrgrafton",
            "vote_text" : "#yes #CA totally agree! Long quote OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO"
        }
    },
    {
        "vote_score": [125, 75],
        "college_score": [206, 332],
        "question_text": "\"Its a bad deal with Iran - we're not staying with Israel. I think the people are looking for real Leadership.\" right? #yes #no #birddeal",
        "end_time": "2016-01-26 21:48:30.531648-08:00",
        "random_quote": {
            "user": "jrgrafton",
            "vote_text" : "#no #WA this quote sucks balls!"
        }
    }]
}

ReactDOM.render(
  <Debate debate={DEBATE}/>,
  document.getElementById('debate')
);
