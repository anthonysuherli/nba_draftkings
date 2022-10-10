
from draft_kings import Sport, Client
import os
import requests
import io
import pytz
import pandas as pd
import datetime as dt
import warnings
warnings.filterwarnings('ignore')

def get_contests(names, date=dt.datetime.now()):
    contests = Client().contests(sport=Sport.NBA).contests
    names = [x.lower() for x in names]
    cinfo = {}
    for idx, contest in enumerate(contests):
        # contest_start =
        # contest_start.replace(tzinfo = et)
        if contest.name.lower() in names and contest.starts_at.replace(tzinfo=et) >= date.replace(tzinfo=et):
            cinfo[contest.name] = {
                'start_time': contest.starts_at,
                'id': contest.contest_id,
                'draft_id': contest.draft_group_id,
                'payout': contest.payout
            }
    return cinfo


def get_players(contest):
    draft_id = contest['draft_id']
    draft = Client().draftables(draft_group_id=draft_id)

    player_dict = {}

    for player in draft.players:
        player_name = player.name_details.display
        player_dict[player_name] = {
            'Position': player.position_name,
            'Name + ID': f'{player_name} + {player.player_id}',
            'Name': player_name,
            'ID': player.player_id,
            'Game': player.competition_details.name,
            'Time': player.competition_details.starts_at,
            'TeamAbbrev': player.team_details.abbreviation,
            'Salary': player.salary,
        }

    return player_dict


def get_draft(contest):
    draft_id = contest['draft_id']

    url = f'https://www.draftkings.com/bulklineup/getdraftablecsv?draftGroupid={draft_id}'

    resp = requests.get(url)
    resp = ',,,,,,,,,'.join(resp.text.split(',,,,,,,,,')[6:])
    return pd.read_csv(io.StringIO(resp), sep=",").reset_index().loc[:, 'Position':]


if __name__ == "__main__":
    et = pytz.timezone('America/New_York')
    with open('config.txt', 'r') as f:
        names = f.read().split('\n')

    names = [x.upper() for x in names]
    date = dt.datetime.now() + dt.timedelta(1)

    contests = get_contests(names, date)

    print(f'contests: {contests}')
    print(f"current time (ET): {dt.datetime.now().strftime('%m-%d-%y %H:%M')}")

    for contest_name in contests.keys():
        print(f'\nprocessing for {contest_name}')

        if contest_name.upper() not in os.listdir('data'):
            os.mkdir(f'data/{contest_name}')
            print(f'created directory for {contest_name}')

        player_dict = get_players(contests[contest_name])
        df_players = pd.DataFrame.from_dict(player_dict, orient='index').reset_index().iloc[:, 1:]

        data_path = f"data/{contest_name}/{date.strftime('%Y-%m-%d')}.csv"
        df_players.to_csv(data_path, index=False)

        print(f'roster saved to: {data_path}\n')