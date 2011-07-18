BASE_URL='http://sebest.api.dev.int.dmcloud.net'
USER_ID='4cadc039dede832941000000'
API_KEY='f728debf25de13d367c2b73a6647979dd4f234e6'

from cloudkey import CloudKey
from cloudkey import AuthenticationError, NotFound, InvalidParameter, Exists, MissingParameter

from flask import Flask
from flask import render_template, request, url_for

app = Flask(__name__)

cloudkey = CloudKey(USER_ID, API_KEY, base_url=BASE_URL)

# The page with the upload FORM
@app.route("/")
def upload():
    # this is the URL that will recieve the information at the end of the upload
    target = request.base_url + url_for('upload_done')
    
    # this API call will return the upload url and the status url
    upload = cloudkey.file.upload(target=target, status=True, jsonp_cb='?')

    # this is the URL where we will upload our file
    upload_url = upload['url']

    # this is the URL that we poll using JSONP to get the upload status
    upload_status = upload['status']

    # the HTML page with the upload FORM
    return render_template('upload.html', upload_url=upload_url, upload_status=upload_status)

# The page called at the end of the upload
# request.args contrains the query string parameters
@app.route("/done")
def upload_done():
    # the url that you will use for media.create
    url = request.args['url']
    
    # the filename, you can use it as a title
    name = request.args['name']

    # we create a new media
    media = cloudkey.media.create(url=url, meta={'title': name})

    # the media id that you can store in your own DB
    media_id = media['id']
    return ''

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5003, debug=True)
