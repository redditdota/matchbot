import requests
import json

strawpoll_api = 'https://strawpoll.me/api/v2/polls'
ratings = ['6 - (Must watch)', '5', '4', '3', '2', '1 - (Skip it)']

class Poll(object):
    def __init__(self, response=None, poll_id=None):
        if response:
            poll_data = json.loads(response.content)
            self.title = poll_data['title']
            self.id = poll_data['id']
            self.votes = poll_data['votes']
        elif poll_id:
            self.id = poll_id
            self.update()
        else:
            raise ValueError("Provide one of the two parameters when creating a Poll")

    def __repr__(self):
        return "[%s]: %s (%s)" % (self.score, self.title, self.id)

    @property
    def score(self):
        """ This may cause timing issues if we start doing bulk operations on many polls. ~2s per.
        """
        self.update()
        return self._calculate_weighted_percent()

    def update(self):
        url = '%s/%s' % (strawpoll_api, self.id)
        poll = Poll(requests.get(url))
        self.title = poll.title
        self.votes = poll.votes
        return poll

    def _calculate_weighted_percent(self):
        """ Calculate a percentage metric for the poll's score, weighted between 50% and 100%
        """
        num_votes = sum(self.votes)
        if num_votes == 0:
            return '-----'
        weights = [int(option[0]) for option in ratings]
        weighted_average = [a * b for a, b in zip(weights, self.votes)]
        max_score = num_votes * weights[0]
        actual_percentage = sum(weighted_average) / float(max_score) * 100
        fudged_percentage = actual_percentage / 2 + 50
        return '%s%%' % round(fudged_percentage, 1)


def create_strawpoll(title, options):
    data = {
        'title': title,
        'options': options,
        'multi': 'false',
        'dupcheck': 'normal',
        'captcha': 'false',
    }
    poll = requests.post(strawpoll_api, data=json.dumps(data))
    assert int(poll.status_code) == 200, (
        'Poll was not created successfully: %s\n%s' % (poll.status_code, poll.content))
    return Poll(poll)


#================================================================

example_created_id = '11935980'
test_poll = Poll(poll_id=example_created_id)
results = test_poll.votes # can't fake it easily anymore
print(test_poll)

new_poll = create_strawpoll("How many rapiers is too many?", ratings)
print(new_poll)
