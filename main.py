import urllib.request
import json
import itertools
import time
import pathlib
import datetime

def fetch_json(token, url):
    '''
    指定したURL(Qiita API)にアクセスし、レスポンスボディ(JSON)をパースする。
    DoS対策として、指定したURLにアクセスする前に1秒sleepする。
    @param token アクセストークン
    @param url 
    @return JSONをパースしたDictionaryが格納されたList(Response Body)
    '''
    time.sleep(1)
    print(f'fetch_json `{url}`')

    headers = {
        'Authorization' : f'Bearer {token}'
    }
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read())


def fetch_items(token, page):
    """
    以下のURLにアクセスして、投稿者の記事を最大20個取得する。
    https://qiita.com/api/v2/docs#%E6%8A%95%E7%A8%BF
    @param token アクセストークン
    @param page ページネーションのページ(1..*)
    @return JSONをパースしたDictionaryが格納されたList
    """
    url = f'https://qiita.com/api/v2/authenticated_user/items?page={page}&per_page=20'
    return fetch_json(token, url)


def fetch_comments(token, item_id):
    """
    以下のURLにアクセスして、記事に紐づくコメントをすべて取得する。
    https://qiita.com/api/v2/docs#%E3%82%B3%E3%83%A1%E3%83%B3%E3%83%88
    @param token アクセストークン
    @param item_id 記事を一意に特定するID
    @return JSONをパースしたDictionaryが格納されたList
    """
    url = f'https://qiita.com/api/v2/items/{item_id}/comments'
    return fetch_json(token, url)


def dump_json(dirpath, obj):
    """
    DictionaryをJSONとみなして、ファイルに保存する。ファイル名は`${id}.json`となる。
    @param dirpath 保存先のディレクトリのパス(pathlib.Path)
    @param obj JSONとなるDictoinary
    """
    id = obj['id']
    fpath = dirpath.joinpath(id).with_suffix('.json')
    print(f'dump_json `{fpath}`')
    with fpath.open('w') as fp:
        json.dump(obj, fp)


def main():
    print('アクセストークンを入力してください:')
    token = input()

    # すべての記事とコメントを取得する。
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
    
    # jsonファイルを格納するディレクトリを作成する。
    pwd = pathlib.Path(__file__).parent.resolve()
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    result_dir = pwd.joinpath(timestamp)
    item_dir = result_dir.joinpath('item')
    comment_dir = result_dir.joinpath('comment')
    for dir_path in (result_dir, item_dir, comment_dir):
        dir_path.mkdir()

    # すべての記事とコメントをファイルとして保存する。
    for item in all_items:
        dump_json(item_dir, item)
    
    for comment in all_comments:
        dump_json(comment_dir, comment)


if __name__ == '__main__':
    main()