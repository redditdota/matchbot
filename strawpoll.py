import requests
import json

strawpoll_api = 'https://strawpoll.me/api/v2/polls'
ratings = ['6 - (Must watch)', '5', '4', '3', '2', '1 - (Skip it)']


def create_strawpoll(title, options):
    data = {
        'title': title,
        'options': options,
        'multi': 'false',
        'dupcheck': 'normal',
        'captcha': 'false',
    }
    poll = requests.post(strawpoll_api, data=json.dumps(data))
    assert poll.status_code == '200', 'Poll was not created successfully:\n%s' % poll.content
    return poll.content

def get_current_poll_results(poll_id):
    url = '%s/%s' % (strawpoll_api, poll_id)
    poll = json.loads(requests.get(url).content)
    return poll['votes']

def calculate_weighted_percent(votes):
    num_votes = sum(votes)
    weights = [int(option[0]) for option in ratings]
    weighted_average = [a * b for a, b in zip(weights, votes)]
    max_score = num_votes * weights[0]
    actual_percentage = sum(weighted_average) / float(max_score) * 100
    fudged_percentage = actual_percentage / 2 + 50 # Make results ~= grades, with min score of 50%
    return '%s%%' % round(fudged_percentage, 1)

#================================================================

example_created_id = '11935980'
results = get_current_poll_results(example_created_id)
print(calculate_weighted_percent(results))
