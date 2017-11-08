import tweepy
import random
import requests

from io import BytesIO
from PIL import Image, ImageFile

from twitter_scrambler.settings import *

ImageFile.LOAD_TRUNCATED_IMAGES = True


# authenticate with twitter, start session
def authenticate(consumer_key, consumer_secret, access_token, access_token_secret):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    return auth

auth = authenticate(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)


def tweet_image(url, username, status_id):
    filename = 'temp.png'
    request = requests.get(url, stream=True)
    if request.status_code == 200:
        img = Image.open(BytesIO(request.content))
        img.save(filename)
        scramble(filename)
        api.update_with_media('scramble.png', status='@{0}'.format(username), in_reply_to_status_id=status_id)
    else:
        print("unable to download image")


def scramble(filename):
    img = Image.open(filename)
    width, height = img.size
    xblock = width // BLOCK_LENGTH
    yblock = height // BLOCK_LENGTH
    blockmap = [(xb * BLOCK_LENGTH, yb * BLOCK_LENGTH, (xb + 1) * BLOCK_LENGTH, (yb + 1) * BLOCK_LENGTH)
                for xb in range(xblock) for yb in range(yblock)]
    shuffle = list(blockmap)
    random.shuffle(shuffle)
    result = Image.new(img.mode, (width, height))
    for box, sbox in zip(blockmap, shuffle):
        crop = img.crop(sbox)
        result.paste(crop, box)
    result.save('scramble.png')


class TwitterStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        username = status.user.screen_name
        status_id = status.id

        # scrambler is inserted into listener
        if 'media' in status.entities:
            for image in status.entities['media']:
                tweet_image(image['media_url'], username, status_id)


def main():
    listener = TwitterStreamListener()
    stream = tweepy.Stream(auth, listener)
    stream.filter(track=['@DKAcatay'])


if __name__ == '__main__':
    main()