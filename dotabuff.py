"""
Post match thread bot:

- Detect when set ends (?) (Dota client or through dotabuff?)
- POST request to strawpoll.me for each game of the set:
-- "Must watch, good match, okay match, bad match, Don't watch" ... ideally 6-12 hour time limit.
-- (Occasionally update the post itself with results from these polls: average and std. deviation?)
- Create reddit thread. Sticky reddit thread through some automoderator user-checked keyword.
- After 6-12 hours, take the final list of all strawpolls created that day and collate the results.
-- Create a final "best of today" thread based on those results.
- Sticky that thread (probably some protection to make sure there's not already 2 stickies)
"""

import requests
from bs4 import BeautifulSoup

base_url = 'https://www.dotabuff.com/'
endpoints = {
    'recent_pro': 'esports/series?league_tier=professional',
    'recent_premium': 'esports/series?league_tier=premium',
}
firefox_headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)'}


class Series(object):
    def __init__(self, data):
        """ These are mostly hardcoded references and the most likely thing to break.
            Each "series" data contains 9 <td> elements which contain the info we extract.
        """
        self.data = data
        # TODO: Handle games that are in a TBA state (8 <td> results)
        self.winner = data[3].find_all('div')[-1].string
        if self.winner in ['Tied', 'TBA']:
            data.insert(3, 'Dummy element to normalize results...')
            self.winner = None
        assert len(data) == 9, 'The dotabuff results page has changed, update API.\n%s' % self.data
        self.league_id = data[0].find_next('img')['title']
        self.start_time = data[2].find_next('time')['datetime']
        self.max_games = int(data[1].find_next('a').string[-1])
        self.status = data[2].find_next('div').string
        self.teams = list(set([team.string for team in data[5].select(".r-only-mobile")]))
        self.duration = data[6].find_next('div').string
        self.game_ids = [game['title'].split()[-1] for game in data[7].select('a[title]')]

    def __repr__(self):
        winner_string = "was won by %s" % self.winner if self.winner else "was tied"
        return ("A best of {self.max_games} between {self.teams[0]} and {self.teams[1]} "
                "{winner_string} in {self.duration}".format(**vars()))

def get_matches_from_dotabuff():
    r = requests.get(base_url + endpoints['recent_pro'], headers=firefox_headers)
    soup = BeautifulSoup(r.content, "lxml")
    recent_matches = soup.find(attrs={'class': 'recent-esports-matches'})
    table = recent_matches.findChildren(['th', 'tr'])
    all_cells = [row.findChildren('td') for row in table if row.findChildren('td')]

    sets = []
    cells_iterator = iter(all_cells)
    for cell in cells_iterator:
        # iterate over the cells we've grabbed, then group by 3's to collate data about each series
        set_to_build = cell
        next(cells_iterator) # skip this one, it has no meaningful info
        set_to_build += next(cells_iterator)
        sets.append(set_to_build)
    return sets

#================================================================

all_series = [Series(match_data) for match_data in get_matches_from_dotabuff()]
completed_series = [series for series in all_series if series.status == 'Completed']
for series in completed_series:
    print(series)


