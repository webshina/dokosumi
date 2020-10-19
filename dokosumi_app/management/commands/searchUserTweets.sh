# DESCRIPTION：キーワードを検索し、そのキーワードをつぶやいたユーザーを取得
# INPUT：検索するツイートに含まれるキーワード
# OUTPUT：./userTweets.json

#!/bin/sh

source /home/apps/myenv/bin/activate

python /home/apps/dokosumi/manage.py searchUserTweets $1