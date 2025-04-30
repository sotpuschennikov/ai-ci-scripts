
import argparse
import os
import re
import sys
import logging
from openai import OpenAI
from jinja2 import Environment, FileSystemLoader, select_autoescape

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

env = Environment(
    loader=FileSystemLoader(searchpath="./"),
    autoescape=select_autoescape(['j2'])
)


def parse_arguments():
    parser = argparse.ArgumentParser(description='Codereview from AI')
    parser.add_argument('--base-url', help='API base URL', type=str)
    parser.add_argument('--context', help='Context', type=str, default='You are a devops engineer. Help me with scripting')
    parser.add_argument('--api-key', help='OpenAI key', type=str)
    parser.add_argument('--max-tokens', help='Model max tokens', type=int, default=10000)
    parser.add_argument('--model', help='Model type', type=str)
    parser.add_argument('--lang', help='Programming language of code', type=str, default='Python')
    parser.add_argument('--temperature', help='Temperature OpenAI API parameter', type=float, default=1.0)
    parser.add_argument('--template-file', help='Path to jinja2 template file', default='ai-codereview/prompt_template.j2')
    return parser.parse_args()


def load_prompt_template(args):
    try:
        template = env.get_template(args.template_file)
        return template
    except Exception as e:
        logger.error(f"Error loading template: {e}")
        sys.exit(1)


def main(args):
    client = OpenAI(api_key=str(args.api_key))
    if args.base_url:
        client.base_url = str(args.base_url)
    MODEL = str(args.model)
    template = load_prompt_template(args)
    prompt = template.render(LANG=str(args.lang), PROMPT_VAR=os.getenv('PROMPT_VAR'))

    try:
        chat_completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": str(args.context)},
                {"role": "user", "content": prompt},
            ],
            temperature=args.temperature,
            max_tokens=args.max_tokens,
        )
        output = re.sub(r'<think>.*?</think>', '', chat_completion.choices[0].message.content, flags=re.DOTALL)
        print('Output:', output)
        f = open("./output.txt", "a")
        f.write(re.sub(r'<think>.*?</think>', '', chat_completion.choices[0].message.content, flags=re.DOTALL))
        f.close()
        prompt_summary = 'Using markdown format briefly describe this review: ' + output
        chat_completion_summary = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": ""},
                {"role": "user", "content": prompt_summary },
            ],
            max_tokens=args.max_tokens,
            temperature=0.6,
        )
        summary = re.sub(r'<think>.*?</think>', '', chat_completion_summary.choices[0].message.content, flags=re.DOTALL)
        #print(summary)
        f = open("./summary.txt", "a")
        f.write(summary)
        f.close()
        #print("Usage: ", chat_completion.usage)
    except Exception as e:
        logger.info('Error accessing OpenAI API: %s', e)
        sys.exit(1)


if __name__ == "__main__":
    parsed_args = parse_arguments()
    main(parsed_args)
