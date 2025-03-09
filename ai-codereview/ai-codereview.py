
import argparse
import os
import sys
from openai import OpenAI
from jinja2 import Environment, FileSystemLoader, select_autoescape
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setting up the Jinja2 environment
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
        print(f"Error loading template: {e}")
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
        print("Output: ", chat_completion.choices[0].message.content)
        print("Usage: ", chat_completion.usage)
    except Exception as e:
        print(f"Error accessing OpenAI API: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parsed_args = parse_arguments()
    main(parsed_args)
