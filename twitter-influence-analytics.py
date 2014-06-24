import twitter
import pandas
import time
import json

# tw = twitter.Twitter(auth=twitter.OAuth('1149944478-vXoBfwZ718WW12m6xFjoGHEvjQk73H1qP1g2q0Z',
#                                 'muJVicR46pW7dlMqxDkyAakJMDtijFyPeMCzcETU5ohf0',
#                                 'v5b3mm9hRjZ7kL7gcOUvxwr4m',
#                                 't2NZr2T18jOEFcX8h2B1jS8k8JH5jwD2eVUZBFyGAdEVI22GT6'))

# Load the config.json file
with open('config.json', 'r') as f:
    jsonData = f.read()
config = json.loads(jsonData)
# Create the twitter object
tw = twitter.Twitter(auth=twitter.OAuth(config['access_token'], config['access_token_secret'], config['consumer_key'], config['consumer_secret']))

# Prompt the user
userinput = raw_input('Enter a comma-separated list of Twitter screen names to analyze: ')
userinput = userinput.replace(' ', '').split(',')
query = raw_input('Enter your query: ')

# The first query
print 'Running query...'
results = tw.search.tweets(q=query,
        count=100,
        until='2014-06-13')
df = pandas.DataFrame(results['statuses'])
df['user_id'] = [r['user']['id_str'] for r in results['statuses']]
with open('data.csv', mode='w') as f:
        df.to_csv(f, encoding='UTF-8')
counter = 100
# Loop the query
while not df.empty and counter > 0:
    counter -= 1
    minId = min(df.id) - 1
    results = tw.search.tweets(q=query,
            count=100,
            max_id=str(minId))
    df = pandas.DataFrame(results['statuses'])
    df['user_id'] = [r['user']['id_str'] for r in results['statuses']]
    with open('data.csv', mode='a') as f:
        df.to_csv(f, encoding='UTF-8', header=False)
print 'Completed query'

# twitter_accounts = ['catiewayne', 'Animalists']
print 'Determining influence...'
twitter_accounts = userinput
followers = []
for sn in twitter_accounts:
    next_cursor = -1
    max_list = 1000000 / 5000 # Put a limit to how many followers we want to get
    while next_cursor and max_list >= 0:
        max_list -= 1
        x = tw.application.rate_limit_status(resources='followers')
        # print(x['resources']['followers']['/followers/ids'])
        # Wait 10 minutes for the rate limit to reset
        if x['resources']['followers']['/followers/ids']['remaining'] <= 5:
            time.sleep(60 * 10)
        results = tw.followers.ids(screen_name=sn, cursor=next_cursor, stringify_ids=True)
        next_cursor = results['next_cursor']
        followers += results['ids']
print 'Completed influence'

tweetData = pandas.DataFrame.from_csv('data.csv')
counter = 0
influencers = []
for user in followers:
    if not tweetData[tweetData.user_id == int(user)].empty:
        counter += 1
        influencers.append(user)
# print(counter)
# print(len(followers))

impressions = 0
for user in influencers:
    impressions += tw.users.lookup(user_id=user)[0]['followers_count']

# userPrettyPrint = ''
# if len(twitter_accounts) == 1:
#     userPrettyPrint = twitter_accounts[0]
# elif len(twitter_accounts) == 2:
#     userPrettyPrint = twitter_accounts[0] + ' and ' + twitter_accounts[1]
# elif len(twitter_accounts) > 2:
#     for i in range(len(twitter_accounts) - 1):
#         userPrettyPrint += twitter_accounts[i] + ','

userPrettyPrint = ''
if len(twitter_accounts) == 1:
    userPrettyPrint = '@' + twitter_accounts[0]
elif len(twitter_accounts) == 2:
    userPrettyPrint = '@' + twitter_accounts[0] + ' and @' + twitter_accounts[1]
elif len(twitter_accounts) > 2:
    for i in range(len(twitter_accounts) - 1):
        userPrettyPrint += '@' + twitter_accounts[i] + ', '
    userPrettyPrint = userPrettyPrint[:-2] + ' and @' + twitter_accounts[-1]
print 'Twitter users {} have a total of {} followers.'.format(userPrettyPrint, len(followers))
print 'Of those {} followers, {} were engaged in the topic of {} in the past seven days.'.format(len(followers), len(influencers), query)
print 'Those {} have {} followers of their own.'.format(len(influencers), impressions)
print 'Your impressions have gone from {} to {}!'.format(len(followers), len(followers) + impressions)
# print impressions
# print len(influencers)
# print len(followers)
#
