import argparse
import json

def main(args):
    print(args.input_json_path)
    redirection = json.load(open(args.input_json_path))
    with open(args.output_md_path, 'w') as f:
        for r in redirection['redirects']:
            print('- [{source_url}]({target_url})'.format(source_url = r['url'], target_url = r['action_data']['url']), file = f)
    print(args.output_md_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-json-path', '-i')
    parser.add_argument('--output-md-path', '-o')
    args = parser.parse_args()

    main(args)
