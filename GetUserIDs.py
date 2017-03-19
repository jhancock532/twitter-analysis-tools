import sys, time, tweepy, json
from random import randint
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

userIDList = []
filename = "userIDs.txt"
userIDsGathered = 0

class listener(StreamListener):
    
    def on_data(self, data):
        try:
            object = json.loads(data)

            #username = object["user"]["screen_name"] #screen names can be edited!
            userId = object["user"]["id_str"] #userID is therefore safer
            #time.sleep(randint(0,2)) #this will make your sample more random as you increase the 2 to a higher number.
            #it will also take a longer time to process users. Because of the rate of tweeting of the UK (multiple tweets per second),
            #you could possibly get away with just using time.sleep(0.2), and if you have a bad internet connection no time.sleep whatsoever.

            with open(filename, "a") as out_file:
                out_file.write(userID+"\n")
            global userIDsGathered
            userIDsGathered += 1
            print(str(userIDsGathered)) #printing output takes a long time in python - altenatively print every MOD 100 users analysed 
            #if userIDsGathered % 100 = 0:
            #   print(str(userIDsGathered))
            return True
        
        except:
            print ("Error:",sys.exc_info()[0], sys.exc_info()[1])

    def on_error(self, status):
        print("Error;")

twitterStream = Stream(auth, listener())
twitterStream.filter(languages=["en"],locations=[-11,49,0,59]) #This streams tweets from the UK, of users speaking english.
