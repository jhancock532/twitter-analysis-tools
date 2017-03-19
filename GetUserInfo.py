import sys, time, tweepy, json, re, sqlite3, datetime, timeit
from tweepy import Stream
from tweepy import OAuthHandler
#optional - gender analysis
import gender_guesser.detector as gender
from tweepy.streaming import StreamListener
#optional - tweet sentiment
from textblob import TextBlob
d = gender.Detector(case_sensitive=False)

#consumer key, consumer secret, access token, access secret. Get me from Twitter API
ckey=""
csecret=""
atoken=""
asecret=""

auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)
api = tweepy.API(auth)
api.wait_on_rate_limit=True;

tweetCount = 100 #set how many tweets you wish to analyse per username

#For my study I counted how many months users accounts had existed on Twitter.
now = datetime.datetime.now()
currentDate = str(now)
currentYear = int(currentDate[0:4])
currentMonth = int(currentDate[5:7]) 

conn = sqlite3.connect('databaseName.db') 
c = conn.cursor()

# I admit that the following create table method looks like something from a nightmare -  
def create_table():
    c.execute('CREATE TABLE IF NOT EXISTS twitterData(username TEXT, gender TEXT, followerCount INTEGER, friendCount INTEGER, accountAge INTEGER, statusCount INTEGER, listCount INTEGER, retweetCount INTEGER, quoteCount INTEGER, repliesCount INTEGER, emojiCount INTEGER, positiveEmojiCount INTEGER, passiveEmojiCount INTEGER, negativeEmojiCount INTEGER, emoticonCount INTEGER, positiveEmoticonCount INTEGER, negativeEmoticonCount INTEGER, positiveTweetCount INTEGER, negativeTweetCount INTEGER, overallSentiment REAL, totalFavouritedCount INTEGER, totalRetweetedCount INTEGER, totalMentionedCount INTEGER, hashtagCount INTEGER, URLCount INTEGER, mediaCount INTEGER, questionCount INTEGER, exclaimCount INTEGER, fullStopCount INTEGER, commaCount INTEGER, hypenCount INTEGER, quotationMarkCount INTEGER, apostropheCount INTEGER, colonCount INTEGER, semicolonCount INTEGER, averageWordLength REAL, averageTweetLength REAL, capitalLetterCount INTEGER, lowerLetterCount INTEGER, firstPersonCount INTEGER, secondPersonCount INTEGER, thirdPersonCount INTEGER, saidRetweetCount INTEGER, saidFollowCount INTEGER, punctuationCount INTEGER)')

create_table() 

# -- Emoji Values - Positive, Negative
positiveEmojis = ["\\ud83d\\ude02","\\ud83d\\ude0d","\\ud83d\\ude0a","\\ud83d\ude18","\\ud83d\\udc95",
                  "\\ud83d\\udc4c","\\ud83d\\ude0f","\\ud83d\\ude01","\\ud83d\ude09","\\ud83d\\udc4d",
                  "\\ud83d\\ude0c","\\ud83d\\ude4c","\\ud83d\\ude48","\\ud83d\ude0e","\\ud83d\\ude05",
                  "\\ud83d\\ude04","\\ud83d\\udc9c","\\ud83d\\udcaf","\\ud83d\udc96","\\ud83d\\udc99",
                  "\\ud83d\\ude1c","\\ud83d\\ude0b","\\ud83d\\udc4f","\\ud83d\ude1d","\\ud83d\\udc98",
                  "\\ud83d\\udc9e","\\ud83d\\udc97","\\ud83d\\udc4a","\\ud83d\ude03","\\ud83c\\udf89",
                  "\\ud83c\\udf39","\\ud83d\\udc9b","\\ud83d\\ude06","\\ud83d\ude4f","\\ud83d\\ude3b",
                  "\\ud83d\\udc9a","\\ud83d\\ude00","\\ud83d\\udc93","\\ud83d\ude1a","\\ud83d\\ude1b",
                  "\\ud83d\\ude07","\\ud83d\\ude4b","\\ud83c\\udf1f","\\ud83d\udc83","\\ud83d\\ude39",
                  "\\u2764","\\u2665","\\u2728","\\u2714","\\u2713","\\u2705","\\u2611","\\u270c"
                  ]
negativeEmojis = ["\\ud83d\\ude12","\\ud83d\\ude2d","\\ud83d\\ude29","\\ud83d\\ude14","\\ud83d\\ude22",
                  "\\ud83d\\ude34","\\ud83d\\ude11","\\ud83d\\udc94","\\ud83d\\ude15","\\ud83d\\ude1e",
                  "\\ud83d\\ude2a","\\ud83d\\ude31","\\ud83d\\ude08","\\ud83d\\ude21","\\ud83d\\ude2b",
                  "\\ud83d\\ude24","\\ud83d\\udc80","\\ud83d\\ude13","\\ud83d\\ude37","\\ud83d\\ude23",
                  "\\ud83d\\ude25","\\ud83d\\ude16","\\ud83d\\ude20","\\ud83d\\udd2b","\\ud83d\\ude2c",
                  "\\ud83d\\udc4e","\\ud83d\\ude45","\\ud83d\\ude30","\\ud83d\\ude1f","\\ud83d\\ude28",
                  "\\ud83d\\ude26","\\ud83d\\ude27","\\ud83d\\ude35","\\ud83d\\ude3f","\\ud83d\\ude3e",
                  "\\u274c", "\\u274e"
                ]

positiveEmojiSubjectSet = frozenset(positiveEmojis)
negativeEmojiSubjectSet = frozenset(negativeEmojis)

# -- Emoticon Values - Positive and Negative 
regexPositiveEmoticons = r" #\)| #\-\)| :-\)| :\)| :D| :o\)| :\]| :3| :c\)| :>|=\]| 8\)| =\)| :\}| :\^\)| :?\)| \(:| \(\-:| :-D| 8-D| 8D | x-D| xD| X-D| XD| =-D| =D| =-3| =3| B\^D| :'-\)| :'\)| :\*| :\-\*| :\^\*| \( '\}\{' \)| ;-\)| ;\)| \*\-\)| \*\)| ;-\]| ;\]| ;D| ;\^\)| :-,| :-P| :P| :-p| :p| =p| :-b| :b| d:"
regexNegativeEmoticons = r">:\[| :-\(| :\(| :-c| :c| :-<| :C| :<| :-\[| :\[| :\{| :'-\(| :'\(| :@ | >:\(| D:<| D:| D;| D=| v.v| D-':| >:/| :-/| :/| =/| :L| =L| :-&| :&"

s_upper=frozenset(["E", "T", "A", "O", "I", "N", "S", "R", "H", "D", "L", "U", "C", "M", "F", "Y", "W", "G", "P", "B", "V", "K", "X", "Q", "J", "Z"] )
s_lower=frozenset(["e", "t", "a", "o", "i", "n", "s", "t", "h", "d", "l", "u", "c", "m", "f", "y", "w", "g", "p", "b", "v", "k", "x", "q", "j", "z"])

#if you want to search for specific words, create the regex below, copy paste a regex search, create a counter variable, and update the database format.
regexFirst = r"I | we | me | us | my | our | mine | ours |We |My |Our |Ours"
regexRetweet = r"RT|Retweet|retweet"
regexFollow = r"follow|Follow"
regexSecond = r" you | your | yours |You |Your "
regexThird = r" he | they | him | them | his | her | their | she | hers | theirs |They" 

userList = [line.rstrip('\n') for line in open('userIDs.txt')]
userCount = 0 #This is the position in the usernames list which you have analysed to previously.
del userList[:userCount] #If the program crashes, skip past all the usernames already analysed with this.

for user in userList:
    dataReturned = True;

    saidRetweetCount = 0
    saidFollowCount = 0
    punctuationCount = 0

    # -- Emoji Variables --
    emojiCount = 0
    positiveEmojiCount = 0
    passiveEmojiCount = 0
    negativeEmojiCount = 0

    # -- Emoticon Variables --
    emoticonCount = 0
    positiveEmoticonCount = 0
    negativeEmoticonCount = 0

    # -- Tweet Sentiment --
    positiveTweetCount = 0
    negativeTweetCount = 0
    overallSentiment = 0.0

    # -- Popularity variables --
    totalFavouritedCount = 0
    totalRetweetedCount = 0
    totalMentionedCount = 0
    totalRepliesCount = 0

    # -- Pronouns --
    firstCount = 0
    secondCount = 0
    thirdCount = 0

    # -- Format of Tweets --
    retweetCount = 0
    quoteCount = 0

    # -- Entities --
    hashtagCount = 0 
    URLCount = 0
    mediaCount = 0

    # -- Punctuation --
    questionCount = 0 
    exclaimCount = 0 
    ellipsisCount = 0
    fullStopCount = 0
    commaCount = 0
    hypenCount = 0
    quotationMarkCount = 0
    apostropheCount = 0
    colonCount = 0
    semicolonCount = 0

    # -- Lengths --
    wordCount = 0
    wordTotalLength = 0
    tweetTotalLength = 0

    # -- Caps and Lowercase Incrementers --
    capitalLetterCount = 0
    lowerLetterCount = 0
    
    ###
    print('Analysis of '+str(tweetCount)+' tweets from: '+ user + ' user count : ' + str(userCount))
    ###
    userCount += 1

    try:
        for status in tweepy.Cursor(api.user_timeline, id=user).items(tweetCount):

            tweet = status.text
            tweet = tweet.encode("unicode_escape")
            tweet = tweet.decode("utf-8") 

            if tweet[0] == 'R' and tweet[1] == 'T' and tweet[2] == ' ' and tweet[3] == '@': 
                retweetCount = retweetCount + 1 
                continue
        
            username = status.user.screen_name              #object["user"]["screen_name"]
            followerCount = status.user.followers_count     #object["user"]["followers_count"]
            friendCount = status.user.friends_count         #object["user"]["friends_count"]
            statusCount = status.user.statuses_count        #object["user"]["statuses_count"]
            listCount = status.user.listed_count            #object["user"]["listed_count"]
            rawname = status.user.name                      #object["user"]["name"]        
            accountCreationDate = status.user.created_at    #object["user"]["created_at"]
                
            # -- Punctuation --
            exclaimCount += tweet.count("!")
            questionCount += tweet.count("?")
            ellipsisCount += tweet.count("...")
            fullStopCount += tweet.count(".")
            commaCount += tweet.count(",")
            hypenCount += tweet.count("-")
            quotationMarkCount += tweet.count('"')
            apostropheCount += tweet.count("'")
            colonCount += tweet.count(":")
            semicolonCount += tweet.count(";")

            punctuationCount += exclaimCount + questionCount +ellipsisCount+fullStopCount+commaCount+hypenCount+quotationMarkCount+apostropheCount+colonCount+semicolonCount


            #region -- Personal Pronouns -- 
            # -- Pronouns -- 
            if re.search(regexFirst, tweet):
                m = re.findall(regexFirst, tweet)
                firstCount += len(m)

            if re.search(regexSecond, tweet):
                m = re.findall(regexSecond, tweet)
                secondCount += len(m)
                
            if re.search(regexThird, tweet):
                m = re.findall(regexThird, tweet)
                thirdCount += len(m)
            #endregion   
            if re.search(regexRetweet, tweet):
                m = re.findall(regexRetweet, tweet)
                saidRetweetCount += len(m)

            if re.search(regexFollow, tweet):
                m = re.findall(regexFollow, tweet)
                saidFollowCount += len(m)  
                                     
            # -- Popularity / Impact Information -- 
            totalFavouritedCount += status.favorite_count #the number of times the tweet has been favourited
            totalRetweetedCount += status.retweet_count #the number of times the tweet has been retweeted

            # -- Quotes --
            if hasattr(status, 'quoted_status'):
                quoteCount += 1

            # -- Replies --
            if status.in_reply_to_status_id is not None: 
                totalRepliesCount += 1

            # -- Tweet Sentiment Analysis --
            tweetBlob = TextBlob(tweet)
            tweetSentiment = float(tweetBlob.sentiment.polarity) #positive tweets return values of (0.001 - 1.0), negative tweets (-1.0 to -0.001), neutral (0.0)

            ### ---- Entities ---- ###
            # -- Users Mentioned --
            usersMentioned = status.entities["user_mentions"]
            totalMentionedCount += len(usersMentioned)

            # -- Hashtags used --
            hashtagsUsed = status.entities["hashtags"]
            hashtagCount += len(hashtagsUsed)

            # -- Urls used --
            URLsUsed = status.entities["urls"]
            URLCount += len(URLsUsed)
            for URL in URLsUsed:
                fullStopCount -= URL["url"].count(".")
                colonCount -= URL["url"].count(":")

            # -- Media used --
            for media in status.entities.get("media",[{}]):
                if media.get("type",None) == "photo":
                    mediaCount += 1

            ### ---- Emojis, Emoticons, Dingbats ---- ###
            #  -- Emoticon finder :-) --
            if re.search(regexPositiveEmoticons, tweet):
                m = re.findall(regexPositiveEmoticons, tweet)
                positiveEmoticonCount += len(m)
                emoticonCount += len(m)
                #tweetSentiment += len(m) * 0.2 #decide for yourself how you value the sentiment of positive or negative emojis

            if re.search(regexNegativeEmoticons, tweet):
                m = re.findall(regexNegativeEmoticons, tweet)
                negativeEmoticonCount += len(m)
                emoticonCount += len(m)
                #tweetSentiment += len(m) * -0.2

            #  -- Emoji, DingBat Finder --
            emoji_pattern = re.compile('[\U0001F300-\U0001F64F]')    #standard emoji character boundaries 
            dingBat_pattern = re.compile('[\U00002702-\U000027B0]')   #standard dingbat character boundaries

            json_input = status._json
            rawtext = json_input['text']

            emojis = emoji_pattern.findall(rawtext)
            dingbats = dingBat_pattern.findall(rawtext)

            for icon in dingbats:
                resultDingbat = ""
                rawDingbatValue = str(json.dumps(icon))
                resultDingbat = rawDingbatValue[1:-1] #this code gets rid of the quotes ' ' surrounding the value 

                if resultDingbat in positiveEmojiSubjectSet:
                    positiveEmojiCount += 1
                    #tweetSentiment += 0.2
                elif resultDingbat in negativeEmojiSubjectSet:
                    negativeEmojiCount += 1
                    #tweetSentiment -= 0.2
                else:
                    passiveEmojiCount += 1
                        
                emojiCount += 1

            for emoji in emojis:
                resultEmoji = ""
                rawEmojiValue = str(json.dumps(emoji))
                resultEmoji = rawEmojiValue[1:-1] #this code gets rid of the quotes ' ' surrounding the value
                if resultEmoji in positiveEmojiSubjectSet:
                    positiveEmojiCount = positiveEmojiCount + 1
                    #tweetSentiment += 0.2
                elif resultEmoji in negativeEmojiSubjectSet:
                    negativeEmojiCount = negativeEmojiCount + 1
                    #tweetSentiment -= 0.2
                else:
                    passiveEmojiCount = passiveEmojiCount + 1
                        
                emojiCount = emojiCount + 1

            noURLTweet = re.sub(r"http\S+", "", status.text)
            noPunctTweet = re.sub(r"[^\w\d'@#\s]+",'',noURLTweet)

            words = noPunctTweet.split()

            for word in words:
                try:
                    int(word)
                except ValueError:
                    wordCount += 1
                    wordTotalLength += len(word)

            tweetTotalLength += len(noURLTweet)

            # -- Tweet Sentiment Conclusion --
            if tweetSentiment >= 0.33:
                positiveTweetCount += 1

            if tweetSentiment <= -0.33:
                negativeTweetCount += 1

            overallSentiment += tweetSentiment

            #region -- Capital Letters --

            capitalLetterCount += sum(1 for c in noPunctTweet if c in s_upper)
            lowerLetterCount += sum(1 for c in noPunctTweet if c in s_lower)

            #endregion
            
    except:
        print ("Error:",sys.exc_info()[0], sys.exc_info()[1])
        dataReturned = False;

    ### ---- Data analysis ---- ###
    if dataReturned:
        if retweetCount != 50:
            averageTweetLength = tweetTotalLength/(50-retweetCount)
        else:
            averageTweetLength = 0
        if wordCount != 0:
            averageWordLength = wordTotalLength/wordCount
        else:
            averageWordLenght = 0

        if len(rawname.split()) > 1:
            name = rawname.split(' ', 1)[0]
        else:
            name = rawname

        userGender = d.get_gender(name,'great_britain') #I want to use british naming statistics, as all my tweets are from britian 
        if userGender == "mostly_male":
            userGender = "male"
        if userGender == "mostly_female":
            userGender = "female"

        # -- Account Age --
        accountAge = 0 
        userCreationDate = str(accountCreationDate) 

        iterMonth = int(userCreationDate[5:7])
        iterYear = int(userCreationDate[0:4])

        while iterMonth != currentMonth or iterYear != currentYear:
            accountAge = accountAge + 1
            iterMonth = iterMonth + 1
            if iterMonth == 13:
                iterMonth = 1
                iterYear = iterYear + 1

        ### ---- Data Saving ---- ### 
        c.execute("INSERT INTO twitterData (username, gender, followerCount, friendCount, accountAge, statusCount, listCount, retweetCount, quoteCount, repliesCount, emojiCount, positiveEmojiCount, passiveEmojiCount, negativeEmojiCount, emoticonCount, positiveEmoticonCount, negativeEmoticonCount, positiveTweetCount, negativeTweetCount, overallSentiment, totalFavouritedCount, totalRetweetedCount, totalMentionedCount, hashtagCount, URLCount, mediaCount, questionCount, exclaimCount,fullStopCount, commaCount, hypenCount, quotationMarkCount, apostropheCount, colonCount, semicolonCount, averageWordLength, averageTweetLength, capitalLetterCount, lowerLetterCount, firstPersonCount, secondPersonCount, thirdPersonCount, saidRetweetCount, saidFollowCount, punctuationCount ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                                        (username, userGender, followerCount, friendCount, accountAge, statusCount, listCount, retweetCount, quoteCount, totalRepliesCount, emojiCount, positiveEmojiCount, passiveEmojiCount, negativeEmojiCount, emoticonCount, positiveEmoticonCount, negativeEmoticonCount, positiveTweetCount, negativeTweetCount, overallSentiment, totalFavouritedCount, totalRetweetedCount, totalMentionedCount, hashtagCount, URLCount, mediaCount, questionCount, exclaimCount,fullStopCount, commaCount, hypenCount, quotationMarkCount, apostropheCount, colonCount, semicolonCount, averageWordLength, averageTweetLength, capitalLetterCount, lowerLetterCount, firstCount, secondCount, thirdCount, saidRetweetCount, saidFollowCount, punctuationCount))
        conn.commit()
