import argparse
import os
import json
import itertools
import urllib.parse

import instaloader

def main(args):
    config = json.load(open(args.config_path)) if args.config_path and os.path.exists(args.config_path) else {}

    username = args.username or os.path.basename(urllib.parse.urlparse(config.get('instagram_url', '')).path.rstrip('/'))
    assert username

    topk = args.topk or config.get('instagram_topk', 0)
    assert topk

    os.makedirs(args.image_dir, exist_ok=True)

    L = instaloader.Instaloader(
        user_agent=args.user_agent,
        download_pictures=True,#args.download_media, 
        download_videos=args.download_media, 
        download_video_thumbnails=True,#args.download_media, 
        download_geotags=False, 
        download_comments=False, 
        save_metadata=False, 
        compress_json=False, 
        post_metadata_txt_pattern='', 
        dirname_pattern=args.image_dir, 
        filename_pattern=args.filename_pattern, 
    )

    posts = itertools.islice(instaloader.Profile.from_username(L.context, username).get_posts(), topk)

    dicts = []
    for post in posts:
        L.download_post(post, target=username)
        image_basename = os.path.basename(urllib.parse.urlparse(post.url).path)
        d = dict(
            url = args.instagram_post_url_pattern.format(shortcode = post.shortcode),
            image_basename = image_basename, 
            shortcode = post.shortcode,
            body = post.caption,
            date = post.date.isoformat(),
            date_utc = post.date_utc.isoformat()
        )
        dicts.append(d)

    print(json.dumps(dicts, indent=2, ensure_ascii=False), file=open(args.output_json_path, 'w'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--username')
    parser.add_argument('--config-path', '-c')
    parser.add_argument('--output-json-path', '-o', required=True)
    parser.add_argument('--image-dir', required=True)
    parser.add_argument('--topk', type=int)
    parser.add_argument('--download-media', action='store_true')
    parser.add_argument('--user-agent', default = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36')
    parser.add_argument('--instagram-post-url-pattern', default = 'https://instagram.com/p/{shortcode}')
    parser.add_argument('--filename-pattern', default = '{filename}')
    args = parser.parse_args()

    main(args)
