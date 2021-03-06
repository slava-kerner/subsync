# !/usr/bin/python
import httplib2
import os
import sys

from googleapiclient.discovery import build_from_document
from googleapiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains

# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the {{ Google Cloud Console }} at
# {{ https://cloud.google.com/console }}.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "client_secrets.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
YOUTUBE_READ_WRITE_SSL_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:
   %s
with information from the APIs Console
https://console.developers.google.com

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__), CLIENT_SECRETS_FILE))


class YoutubeSubtitles:

    def __init__(self, args):
        self.youtube = self.get_authenticated_service(args)

    # Usage example:
    # python captions.py --videoid='<video_id>' --name='<name>' --file='<file>' --language='<language>' --action='action'


    # Authorize the request and store authorization credentials.
    @classmethod
    def get_authenticated_service(cls, args):
        flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_READ_WRITE_SSL_SCOPE,
                                       message=MISSING_CLIENT_SECRETS_MESSAGE)

        storage = Storage("%s-oauth2.json" % sys.argv[0])
        credentials = storage.get()

        if credentials is None or credentials.invalid:
            credentials = run_flow(flow, storage, args)

        # Trusted testers can download this discovery document from the developers page
        # and it should be in the same directory with the code.
        with open("youtube-v3-api-captions.json", "r") as f:
            doc = f.read()
            return build_from_document(doc, http=credentials.authorize(httplib2.Http()))

    # Call the API's captions.list method to list the existing caption tracks.
    def list_captions(self, video_id):
        results = self.youtube.captions().list(part="snippet", videoId=video_id).execute()

        for item in results["items"]:
            id = item["id"]
            name = item["snippet"]["name"]
            language = item["snippet"]["language"]
            print("Caption track '%s(%s)' in '%s' language." % (name, id, language))

        return results["items"]

    # Call the API's captions.insert method to upload a caption track in draft status.
    def upload_caption(self, video_id, language, name, file):
        insert_result = self.youtube.captions().insert(
            part="snippet",
            body=dict(
                snippet=dict(
                    videoId=video_id,
                    language=language,
                    name=name,
                    isDraft=True
                )
            ),
            media_body=file
        ).execute()

        id = insert_result["id"]
        name = insert_result["snippet"]["name"]
        language = insert_result["snippet"]["language"]
        status = insert_result["snippet"]["status"]
        print("Uploaded caption track '%s(%s) in '%s' language, '%s' status." % (name, id, language, status))

    # Call the API's captions.update method to update an existing caption track's draft status
    # and publish it. If a new binary file is present, update the track with the file as well.
    def update_caption(self, caption_id, file):
        update_result = self.youtube.captions().update(
            part="snippet",
            body=dict(
                id=caption_id,
                snippet=dict(
                    isDraft=False
                )
            ),
            media_body=file
        ).execute()

        name = update_result["snippet"]["name"]
        isDraft = update_result["snippet"]["isDraft"]
        print("Updated caption track '%s' draft status to be: '%s'" % (name, isDraft))
        if file:
            print("and updated the track with the new uploaded file.")

    # Call the API's captions.download method to download an existing caption track.
    def download_caption(self, caption_id, tfmt):
        subtitle = self.youtube.captions().download(
            id=caption_id,
            tfmt=tfmt
        ).execute()
        print("First line of caption track: %s" % (subtitle))

    # Call the API's captions.delete method to delete an existing caption track.
    def delete_caption(self, caption_id):
        self.youtube.captions().delete(id=caption_id).execute()
        print("caption track '%s' deleted succesfully" % (caption_id))
