try:
    import time, random, re, pycurl, hmac, urllib, simplejson, sys, calendar
    from hashlib import sha256
    try:
        from io import BytesIO
    except ImportError:
        from StringIO import StringIO as BytesIO

    POPULAR = 1
    LIKE = 2
    LIKE_FOLLOW = 3
    UNFOLLOW = 4
    UNFOLLOW_ALL = 5
    SANITIZE = 6

    #
    # 1: Swap out <CLIENT_ID_HERE> for your CLIENT_ID and <REDIRECT_URI_HERE> for your REDIRECT_URI, visit the URL to return the CODE (will be in return URI):
    #
    # https://api.instagram.com/oauth/authorize/?client_id=<CLIENT_ID_HERE>&redirect_uri=https://starbs.net&response_type=code&display=touch&scope=likes+relationships
    #
    # 2: Swap out all variables in CAPS for their respective values and execute the following command in a Linux terminal, this will return your ACCESS_TOKEN
    #
    # curl -F 'client_id=CLIENT_ID' -F 'client_secret=CLIENT_SECRET' -F 'grant_type=authorization_code' -F 'redirect_uri=AUTHORIZATION_REDIRECT_URI' -F 'code=CODE' https://api.instagram.com/oauth/access_token
    #
    # 3: Swap out all of the 'changeme' variables below
    # 

    INSTAGRAM_API = "https://api.instagram.com/v1/"
    USER_AGENT = 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_0 like Mac OS X; en-us) AppleWebKit/532.9 (KHTML, like Gecko) Version/4.0.5 Mobile/8A293 Safari/6531.22.7'
    ACCESS_TOKEN = "changeme"
    CLIENT_ID = "changeme"
    CLIENT_SECRET = "changeme"
    IP = "changeme"
    ACTION = LIKE_FOLLOW
    MAX_COUNT = 10
    MAX_SECS = 3

    TAGS = ["love",
            "selfie",
            "me"]

    # If you change these delays, you will exceed the Instagram API rate-limit
    LIKE_DELAY = 36
    REL_DELAY = 60
    API_DELAY = 0

    # DO NOT CHANGE ANYTHING BELOW THIS POINT

    NO_FOLLOW = 0
    FOLLOWS = 1

    likedDict = {}
    headers = {}
    dataDict = ""
    count = 0
    response = "500"

    totalFollows = 0
    totalUnfollows = 0
    totalAPICalls = 0
    totalLikes = 0
    totalErrors = 0

    globErrorMessage = ""

    class tCol:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'

    def currentTime():
        theTime = calendar.timegm(time.gmtime())
        return theTime

    lastLike = currentTime() - LIKE_DELAY
    lastRel = currentTime() - REL_DELAY
    lastAPI = currentTime() - API_DELAY

    userArray = []
    likeArray = []
    APIArray = []
    followArray = []
    followedArray = []

    relArray = []
    picArray = []

    def messageHandler(message, prefix = "FLIB", level = "OKGREEN"):
        print ( "[" + getattr(tCol, level) + prefix + tCol.ENDC + "] "
                + getattr(tCol, level) + message + tCol.ENDC )

    def execPause(length):
        messageHandler('Paused for ' + tCol.FAIL + str(length) + tCol.WARNING + ' seconds...', "TIME", "WARNING")
        time.sleep(length)

    if ACCESS_TOKEN == "changeme" or CLIENT_ID == "changeme" or CLIENT_SECRET == "changeme" or IP == "changeme":
        print messageHandler("You must change all variables which equal 'changeme'", "FAIL", "FAIL")
        sys.exit(1)

    def headerFunction(header_line):
        if ':' not in header_line:
            return
        name, value = header_line.split(':', 1)
        name = name.strip()
        value = value.strip()
        name = name.lower()
        headers[name] = value

    def reqURL(url, post = "", proto = "GET", reqType = "API"):
        global count, dataDict, response, globErrorMessage
        global API_DELAY, LIKE_DELAY, REL_DELAY
        global totalAPICalls, totalErrors

        bytesIO = BytesIO()
        pc = pycurl.Curl()

        signature = hmac.new(CLIENT_SECRET, IP, sha256).hexdigest()
        header = '|'.join([IP, signature])
        header = ["X-Insta-Forwarded-For: " + header]

        post_data = {'access_token' : ACCESS_TOKEN,
                     'client_id' : CLIENT_ID}
        post_data.update(post)
        postfields = urllib.urlencode(post_data)


        if proto == "POST":
            pc.setopt(pc.CUSTOMREQUEST, 'POST')
            pc.setopt(pc.POSTFIELDS, postfields)
        else:
            getURL = url
            url = url + "?" + postfields
            pc.setopt(pc.CUSTOMREQUEST, 'GET')

        pc.setopt(pc.URL, str(url))
        pc.setopt(pc.WRITEFUNCTION, bytesIO.write)
        pc.setopt(pc.HEADERFUNCTION, headerFunction)
        pc.setopt(pycurl.HTTPHEADER, header)

        count = count + 1

        timeDifference = currentTime() - lastAPI
        if timeDifference < API_DELAY:
            execPause(API_DELAY - timeDifference)
        if len(APIArray) > 0:
            while APIArray[0] <= currentTime() - 3600:
                del APIArray[0]
            if len(relArray) >= 4999:
                waitTime = currentTime() - APIArray[0] - 3600
                execPause(waitTime)

        try:
            totalAPICalls = totalAPICalls + 1
            pc.perform()
            response = str(pc.getinfo(pc.HTTP_CODE))
            pc.close()

            encoding = None
            if 'content-type' in headers:
                content_type = headers['content-type'].lower()
                match = re.search('charset=(\S+)', content_type)
                if match:
                    encoding = match.group(1)
            if encoding is None:
                encoding = 'iso-8859-1'

            body = bytesIO.getvalue()

            dataDict = simplejson.loads(body)
            messageHandler(tCol.BOLD + 'Request #' + str(count), "NUM#", "HEADER")
            messageHandler('Remaining API calls: ' + tCol.FAIL + headers['x-ratelimit-remaining'] + '/' + headers['x-ratelimit-limit'] + tCol.ENDC, "RATE", "OKBLUE")
        except Exception as e:
            dataDict = ""
            response = "500"
            error_message = e

        if proto == "POST":
            messageHandler(url, "RURL", "OKBLUE")
        else:
            messageHandler(getURL, "RURL", "OKBLUE")

        messageHandler(postfields, "FLDS", "OKBLUE")
        messageHandler(proto, "HTTP", "OKBLUE")

        if response == "200":
            messageHandler(response, "CODE")
            APIArray.append(currentTime())
        elif response == "500":
            totalErrors = totalErrors + 1
            globErrorMessage = str(error_message)
            if globErrorMessage == "(23, 'Failed writing header')":
                print ""
                messageHandler(tCol.BOLD + "Keyboard Interrupt!", "INPT", "FAIL")
                sys.exit(1)
            messageHandler(str(error_message), "ERRO", "FAIL")
        elif response != "200":
            totalErrors = totalErrors + 1
            error_message = dataDict["meta"]["error_message"]
            error_type = dataDict["meta"]["error_type"]
            messageHandler(response, "CODE", "FAIL")
            messageHandler(error_type, "TYPE", "FAIL")
            messageHandler(error_message, "FAIL", "FAIL")
            if response == "400" and error_type == "OAuthAccessTokenException":
                sys.exit(1)
            if response == "429":
                rates = [int(s) for s in error_message.split() if s.isdigit()]
                messageHandler('Rate exceeded: ' + tCol.FAIL + str(rates[0]) + '/' + str(rates[1]) + tCol.WARNING + ' in the last hour.', "RATE", "WARNING")
                if reqType == "Like":
                    LIKE_DELAY = LIKE_DELAY + 1
                    rateArray = likeArray
                    rateLen = 99
                elif reqType == "Relation":
                    REL_DELAY = REL_DELAY + 1
                    rateArray = relArray
                    rateLen = 99
                else:
                    API_DELAY = API_DELAY + 1
                    rateArray = APIArray
                    rateLen = 4999
                rateDiff = rateLen - len(rateArray)
                if rateDiff > 0:
                    while len(rateArray) < rateLen:
                        rateArray.append(currentTime())
                rateArray[0] = currentTime() - 3900
                waitTime = 0
                waitTime = currentTime() - rateArray[0] - 3600
                execPause(waitTime)
                reqURL(url, post, proto, reqType)

        return dataDict

    def getUsers(next_cursor = None, num_users = 0, stage = 0):
        global userArray
        if stage == 0:
            userURL = INSTAGRAM_API + "users/self/follows"
            arrayName = followArray
        elif stage == 1:
            userURL = INSTAGRAM_API + "users/self/followed-by"
            arrayName = followedArray
        else:
            userArray = list(set(followArray) - set(followedArray))
            messageHandler(tCol.FAIL + tCol.BOLD + str(num_users) + tCol.ENDC + tCol.WARNING + " users added to interaction blacklist", "USER", "WARNING")
            return

        if next_cursor is not None:
            post = {'cursor' : next_cursor}
        else:
            post = {}

        data = reqURL(userURL, post)
        if response != "200":
            if globErrorMessage == "(23, 'Failed writing header')":
                sys.exit(1)
            messageHandler("Retrying request...", "RTRY", "WARNING")
            getUsers(next_cursor, num_users, stage)
            return

        dataPage = data["pagination"]

        next_cursor = None
        if dataPage:
            next_cursor = data["pagination"]["next_cursor"]
        for user in data["data"]:
            for k, v in user.iteritems():
                if k == "id":
                    userID = v
                    arrayName.append(userID)
                    num_users = num_users + 1

        if next_cursor is None:
            stage = stage + 1
        getUsers(next_cursor, num_users, stage)

    def getFollowing(next_cursor = None, num_users = 0):
        global userArray
        userURL = INSTAGRAM_API + "users/self/follows"

        if next_cursor is not None:
            post = {'cursor' : next_cursor}
        else:
            post = {}

        data = reqURL(userURL, post)
        if response != "200":
            if globErrorMessage == "(23, 'Failed writing header')":
                sys.exit(1)
            messageHandler("Retrying request...", "RTRY", "WARNING")
            getFollowing(next_cursor, num_users)
            return

        dataPage = data["pagination"]

        next_cursor = None
        if dataPage:
            next_cursor = data["pagination"]["next_cursor"]
        for user in data["data"]:
            for k, v in user.iteritems():
                if k == "id":
                    userID = v
                    followArray.append(userID)
                    num_users = num_users + 1

        if next_cursor is None:
            userArray = list(set(followArray))
            messageHandler(tCol.FAIL + tCol.BOLD + str(num_users) + tCol.ENDC + tCol.WARNING + " users added to interaction blacklist", "USER", "WARNING")
            return
        getFollowing(next_cursor, num_users)

    def getPics(next_max_like_id = None, num_likes = 0):
        likeURL = INSTAGRAM_API + "users/self/media/liked"

        if next_max_like_id is not None:
            post = {'max_like_id' : next_max_like_id}
        else:
            post = {}

        data = reqURL(likeURL, post)
        if response != "200":
            if globErrorMessage == "(23, 'Failed writing header')":
                sys.exit(1)
            messageHandler("Retrying request...", "RTRY", "WARNING")
            getPics(next_max_like_id, num_likes)
            return

        dataPage = data["pagination"]

        next_max_like_id = None
        if dataPage:
            next_max_like_id = data["pagination"]["next_max_like_id"]

        for image in data["data"]:
            for k, v in image.iteritems():
                if k == "id":
                    imageID = v
                    picArray.append(imageID)
                    num_likes = num_likes + 1

        if next_max_like_id is not None:
            getPics(next_max_like_id, num_likes)
        else:
            messageHandler(tCol.FAIL + tCol.BOLD + str(num_likes) + tCol.ENDC + tCol.WARNING + " pictures added to interaction blacklist", "LIKE", "WARNING")

    # Like `pictureID`
    def likePicture(pictureID):
        if pictureID in picArray:
            messageHandler("You already like picture " + tCol.WARNING + pictureID, "LIKE", "FAIL")
            return
        global totalLikes
        global lastLike
        likeURL = INSTAGRAM_API + "media/%s/likes" % (pictureID)
        messageHandler("Liking picture " + pictureID, "LIKE")
        timeDifference = currentTime() - lastLike
        if timeDifference < LIKE_DELAY:
            execPause(LIKE_DELAY - timeDifference)
        if len(likeArray) > 0:
            while likeArray[0] <= currentTime() - 3600:
                del likeArray[0]
            if len(likeArray) >= 99:
                waitTime = currentTime() - likeArray[0] - 3600
                if waitTime > 0:
                    execPause(waitTime)
        reqURL(likeURL, "", "POST", "Like")
        if response != "200":
            return
        lastLike = currentTime()
        likeArray.append(currentTime())
        totalLikes = totalLikes + 1

    # Follow or unfollow `userID`
    def modUser(userID, action):
        global lastRel
        userURL = INSTAGRAM_API + "users/%s" % (userID)
        modURL = userURL + "/relationship"
        data = reqURL(userURL)
        if response != "200":
            return
        try:
            followsCount = int(data['data']['counts']['follows'])
            followedByCount = int(data['data']['counts']['followed_by'])
        except Exception:
            messageHandler("Failed to get follow counts. Skipping...", "FLLW", "FAIL")
            return
        post = {'action' : action}
        if action == "follow":
            if userID in userArray:
                messageHandler("You are already following user " + tCol.WARNING + userID, "FLLW", "FAIL")
                return
            if followsCount < (followedByCount / 2):
                messageHandler("User " + tCol.WARNING + userID + tCol.FAIL + " is following less than half of their follower count. Skipping...", "FLLW", "FAIL")
                return
            verbAct = "Following"
            swap = 0
        elif action == "unfollow":
            if userID not in userArray:
                messageHandler("You are not following user " + tCol.WARNING + userID, "FLLW", "FAIL")
                return
            verbAct = "Unfollowing"
            swap = 1
        elif action == "block":
            verbAct = "Blocking"
            swap = 1
        timeDifference = currentTime() - lastRel
        if timeDifference < REL_DELAY:
            execPause(REL_DELAY - timeDifference)
        if len(relArray) > 0:
            while relArray[0] <= currentTime() - 3600:
                del relArray[0]
            if len(relArray) >= 99:
                waitTime = currentTime() - relArray[0] - 3600
                if waitTime > 0:
                    execPause(waitTime)
        messageHandler(verbAct + " user " + userID, "RLAT")
        reqURL(modURL, post, "POST", "Relation")
        if response != "200":
            return
        if action == "follow":
            if userID not in userArray:
                userArray.append(userID)
        else:
            if userID in userArray:
                userArray.remove(userID)
        lastRel = currentTime()
        relArray.append(currentTime())
        if action != "block":
            getRelationship(userID, "outgoing", swap)

    # Return relationship to `userID`
    def getRelationship(userID, direction = "incoming", swap = 0):
        global totalFollows, totalUnfollows
        followURL = INSTAGRAM_API + "users/%s/relationship" % (userID)
        data = reqURL(followURL)
        if response != "200":
            return
        status = data["data"]
        incoming = status["incoming_status"]
        outgoing = status["outgoing_status"]

        if swap == 1:
            followLevel = "FAIL"
            noFollowLevel = "OKGREEN"
        else:
            followLevel = "OKGREEN"
            noFollowLevel = "FAIL"

        if direction == "outgoing":
            if outgoing == "follows":
                if swap == 0:
                    totalFollows = totalFollows + 1
                messageHandler("You are following user " + userID, "GREL", followLevel)
                return FOLLOWS
            else:
                if swap == 1:
                    totalUnfollows = totalUnfollows + 1
                messageHandler("You are not following user " + userID, "GREL", noFollowLevel)
                return NO_FOLLOW
        else:
            if incoming != "followed_by":
                messageHandler("User " + userID + " does not follow you", "GREL", noFollowLevel)
                return NO_FOLLOW
            else:
                messageHandler("User " + userID + " follows you", followLevel)
                return FOLLOWS

    # Unfollow users who are not following back
    def unfollowUsers(allUsers = False):
        num_unfollows = 0
        for userID in userArray:
            if allUsers == True:
                modUser(userID, "unfollow")
                num_unfollows = num_unfollows + 1
            elif allUsers == False:
                relationship = getRelationship(userID)
                if relationship == NO_FOLLOW:
                    modUser(userID, "unfollow")
                    num_unfollows = num_unfollows + 1
            secs = random.randint(1, MAX_SECS)
            time.sleep(secs)
        print num_unfollows
        if num_unfollows % 10 == 0:
            print "Unfollowed %s users " % num_unfollows
        messageHandler("Number of users unfollowed is " + str(num_unfollows), "UNFL")
        global ACTION
        ACTION = LIKE_FOLLOW
        begin()
        return num_unfollows

    def likeUsers(max_results, max_id, tag, likeCount, followCount):
        urlFindLike = INSTAGRAM_API + "tags/%s/media/recent" % (tag);
        post = {'max_id' : max_id}
        data = reqURL(urlFindLike, post)
        if response != "200":
            return
        #numResults = len(data['data'])
        #pictureID = 0
        likeCount = 0
        followCount = 0
        for likeObj in data['data']:
            #pictureID = likeObj['id']
            #paginationId = data["pagination"]['next_max_id']
            user = likeObj['user']
            userID = user['id']
            if userID not in userArray:
                try:
                    likeFollowCount = likeAndFollowUser(userID)
                    likeCount = likeCount + likeFollowCount
                except Exception:
                    return
                if (ACTION == LIKE_FOLLOW):
                    if likeAndFollowUser(userID):
                        likeCount = likeCount + int(likeAndFollowUser(userID))
                        followCount = followCount + 1
                else:
                    if likeAndFollowUser(userID):
                        likeCount = likeCount + int(likeAndFollowUser(userID))
                    followCount = followCount + 1
                secs = random.randint(1, MAX_SECS)
                time.sleep(secs)
            if (likeCount % 10 == 0 and likeCount != 0):
                messageHandler('Liked ' + str(likeCount) + ' pictures from #' + tag, 'LIKE')
            if (ACTION == LIKE_FOLLOW):
                if (followCount % 10 == 0 and followCount != 0):
                    messageHandler('Followed ' + str(followCount) + ' users from #' + tag, 'FLLW')
                if (followCount == max_results):
                    break
            elif (ACTION == LIKE):
                if (likeCount == max_results):
                    break
        #if(likeCount != max_results):
        #    likeUsers(max_results, max_id, tag, likeCount, followCount)
        messageHandler('Liked ' + str(likeCount) + ' pictures and followed ' + str(followCount) + ' users from tag #' + tag, 'TAGS')
        return

    # Like and follow users
    def likeAndFollowUser(userID, follow = True):
        numLikesFollows = 0
        userURL = INSTAGRAM_API + "users/%s" % (userID)
        urlUserMedia = userURL+ "/media/recent"
        data = reqURL(userURL)
        if response != "200":
            return
        followsCount = data['data']['counts']['follows']
        followedByCount = data['data']['counts']['followed_by']
        if followsCount < (followedByCount / 2):
            messageHandler("User " + tCol.WARNING + userID + tCol.FAIL + " is following less than half of their follower count. Skipping...", "FLLW", "FAIL")
            return
        data = reqURL(urlUserMedia)
        if response != "200":
            return
        picsToLike = random.randint(1, 4)
        messageHandler("Liking " + str(picsToLike) + " pictures for user " + str(userID))
        countPicViews = 0
        for picture in data['data']:
            if picture['id'] not in likeArray:
                likePicture(picture['id'])
                countPicViews = countPicViews + 1
                numLikesFollows = numLikesFollows + 1
                if(countPicViews == picsToLike):
                    break
        if follow:
            modUser(userID, "follow")
        return numLikesFollows

    def popFunction():
        urlPopular = INSTAGRAM_API + "media/popular"
        data = reqURL(urlPopular)
        if response != "200":
            return
        followCount = 0
        likeCount = 0
        for obj in data['data']:
            for comment in obj['likes']['data']:
                myid = comment['id']
                result = likeAndFollowUser(myid)
                if(result > 0):
                    followCount = followCount + 1
                likeCount = likeCount + 1
                if(followCount % 10 == 0):
                    messageHandler("Followed " + str(followCount) + " users", "followCount")
                seconds = random.randint(1, MAX_SECS)
                time.sleep(seconds)
                if (followCount == MAX_COUNT):
                    break
            if (followCount == MAX_COUNT):
                break
        messageHandler("Followed " + str(followCount) + " users", "followCount")
        messageHandler("Liked " + str(likeCount) + " pictures", "LIKE")

    def sanitizePopUsers():
        num_blocks = 0
        urlPopular = INSTAGRAM_API + "media/popular"
        data = reqURL(urlPopular)
        if response != "200":
            pass
        for obj in data['data']:
            try:
                for key, value in obj['caption'].iteritems():
                    if key == "text":
                        textCap = value
                        isBad = "my bio"
                        if isBad in textCap:
                            for key, value in obj['caption']['from'].iteritems():
                                if key == "id":
                                    modUser(value, "block")
                                    sanitizePopUsers()
                                    return
            except Exception:
                continue
        secs = random.randint(1, MAX_SECS)
        time.sleep(secs)
        sanitizePopUsers()
        messageHandler("Number of users blocked is " + str(num_blocks), "BLKD")
        return num_blocks

    def sanitizeUsers():
        num_blocks = 0
        for userID in userArray:
            urlUserMedia = INSTAGRAM_API + "users/%s/media/recent" % (userID)
            data = reqURL(urlUserMedia)
            if response != "200":
                pass
            for obj in data['data']:
                try:
                    for key, value in obj['caption'].iteritems():
                        if key == "text":
                            textCap = value
                            isBad = "my bio"
                            if isBad in textCap:
                                modUser(userID, "block")
                                sanitizeUsers()
                                return
                except Exception:
                    continue
            secs = random.randint(1, MAX_SECS)
            time.sleep(secs)
        messageHandler("Number of users blocked is " + str(num_blocks), "BLKD")
        return num_blocks

    def decider():
        if(ACTION == LIKE or ACTION == LIKE_FOLLOW):
            getUsers()
            getPics()
            for tag in TAGS:
                likeUsers(MAX_COUNT, 0, tag, 0, 0)
        elif(ACTION==POPULAR):
            getUsers()
            getPics()
            popFunction()
        elif(ACTION==UNFOLLOW):
            getUsers()
            unfollowUsers(False)
        elif(ACTION==UNFOLLOW_ALL):
            getFollowing()
            unfollowUsers(True)
        elif(ACTION==SANITIZE):
            getUsers()
            sanitizePopUsers()
        else:
            messageHandler("Invalid ACTION specified", "ACTO", "FAIL")

    def begin():
        decider()
        begin()

    messageHandler("----------------------", "FLIB", "HEADER")
    messageHandler("  Welcome to Flibber  ", "FLIB", "HEADER")
    messageHandler("  Chip (itschip.com)  ", "FLIB", "HEADER")
    messageHandler("----------------------", "FLIB", "HEADER")

    begin()

except KeyboardInterrupt:
    print ""
    messageHandler(tCol.BOLD + "Keyboard Interrupt!", "INPT", "FAIL")

except Exception as e:
    print ""
    messageHandler(tCol.BOLD + str(e), "EXEP", "FAIL")

else:
    print ""
    messageHandler(tCol.BOLD + "Unknown Error!", "ERRO", "FAIL")

finally:
    print ""
    messageHandler(tCol.UNDERLINE + "Statistics from run:", "STAT", "WARNING")
    messageHandler("Total Unfollows: " + tCol.BOLD + str(totalUnfollows), "STAT", "FAIL")
    messageHandler("Total Follows: " + tCol.BOLD + str(totalFollows), "STAT", "OKGREEN")
    messageHandler("Total Likes: " + tCol.BOLD + str(totalLikes), "STAT", "OKBLUE")
    messageHandler("Total API Calls: " + tCol.BOLD + str(totalAPICalls), "STAT", "HEADER")
    print ""
