import sys, time, tweepy, json
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener

#consumer key, consumer secret, access token, access secret. Get me from Twitter API
ckey=""
csecret=""
atoken=""
asecret=""

auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)
api = tweepy.API(auth)

usernameList = []
filename = "usernames.txt"
usernamesGathered = 0

class listener(StreamListener):
    
    def on_data(self, data):
        try:
            object = json.loads(data)

            username = object["user"]["screen_name"]

            with open("usernamesExtra.txt", "a") as out_file:
                out_file.write(username+"\n")
            usernamesGathered += 1
            print(str(usernamesGathered))
            return True
        
        except:
            print ("Error:",sys.exc_info()[0], sys.exc_info()[1])

    def on_error(self, status):
        print("Error;")

twitterStream = Stream(auth, listener())
twitterStream.filter(languages=["en"],locations=[-11,49,0,59]) #This streams tweets from the UK, of users speaking english.
