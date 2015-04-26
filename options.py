# 1: Change the variables here and navigate to the URL, the page you are
# redirected to will have your CODE appended to the URI
#
# https://api.instagram.com/oauth/authorize/?client_id=fa712a28d6c943d38f4c50a2b6bca30a&redirect_uri=http://itsthisforthat.com&response_type=code&display=touch&scope=likes+relationships
#
# 2: Run the program, it will execute correctly, but will give you the
# ACCESS_TOKEN on the first run which you should replace below
#

INSTAGRAM_API = "https://api.instagram.com/v1/"
USER_AGENT = 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_0 like Mac OS X; en-us) \
AppleWebKit/532.9 (KHTML, like Gecko) Version/4.0.5 \
Mobile/8A293 Safari/6531.22.7'

CLIENT_ID = "fa712a28d6c943d38f4c50a2b6bca30a"  # CHANGE THIS
CLIENT_SECRET = "3a73e328395b44519efedaac05057e7d"  # CHANGE THIS
IP = "172.31.32.112"  # PUBLIC IP - CHANGE THIS
REDIRECT_URI = "http://itsthisforthat.com"  # CHANGE THIS
CODE = "dff027f76e944a5390e12a9cd7d1a648"  # Code for @gilbert account
#ACCESS_TOKEN = "1775173292.fa712a2.e868353c4a10441e8736d34448339b39"  # CHANGE AFTER FIRST RUN
ACCESS_TOKEN = "5046.fa712a2.a996369c17db46d4ac2ff96fcfe258cd" #@gilbert

ACTION = "LIKE"  # CHANGE IF DESIRED
# LIKE (like photos based on TAGS below)
# LIKE_FOLLOW (like and follow users based on TAGS below)
# UNFOLLOW (unfollow users who are not following you)
# UNFOLLOW_ALL (unfollow all users)
# POPULAR (like photos and follow users based on popular tags)

MAX_COUNT = 10  # ACTIONS PER TAG - CHANGE IF YOU WANT
MAX_SECS = 3  # INCREASE IF YOUR ACCESS_TOKEN KEEPS GETTING REVOKED

TAGS = ["rei1440project"]
