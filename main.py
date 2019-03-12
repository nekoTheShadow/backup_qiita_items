import urllib.request
import json
import itertools
import time
import pathlib
import datetime

def fetch_json(token, url):
    time.sleep(1)
    print(f'fetch_json `{url}`')

    headers = {
        'Authorization' : f'Bearer {token}'
    }
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read())


def fetch_items(token, page):
    url = f'https://qiita.com/api/v2/authenticated_user/items?page={page}&per_page=20'
    return fetch_json(token, url)


def fetch_comments(token, item_id):
    url = f'https://qiita.com/api/v2/items/{item_id}/comments'
    return fetch_json(token, url)


def dump_json(dirpath, obj):
    id = obj['id']
    fpath = dirpath.joinpath(id).with_suffix('.json')
    print(f'dump_json `{fpath}`')
    with fpath.open('w') as fp:
        json.dump(obj, fp)


def main():
    print('アクセストークンを入力してください:')
    token = input()

    all_items = []
    all_comments = []
    
    for page in itertools.count(1):
        items = fetch_items(token, page)
        if len(items) == 0:
            break
        all_items.extend(items)

        for item in items:
            item_id = item['id']
            comments_count = item['comments_count']
            if comments_count > 0:
                comments = fetch_comments(token, item_id)
                all_comments.extend(comments)
        
    pwd = pathlib.Path(__file__).parent.resolve()
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    result_dir = pwd.joinpath(timestamp)
    item_dir = result_dir.joinpath('item')
    comment_dir = result_dir.joinpath('comment')
    for dir_path in (result_dir, item_dir, comment_dir):
        dir_path.mkdir()

    for item in all_items:
        dump_json(item_dir, item)
    
    for comment in all_comments:
        dump_json(comment_dir, comment)


if __name__ == '__main__':
    main()