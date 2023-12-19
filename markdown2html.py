#!/usr/bin/python3
import sys
import os
import markdown
import hashlib
import re
from markdown.inlinepatterns import SimpleTagPattern

class CustomMarkdownExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns.register(BoldPattern(r'\*\*(.+?)\*\*'), 'bold', 175)
        md.inlinePatterns.register(BoldPattern(r'__(.+?)__'), 'bold', 175)
        md.inlinePatterns.register(MD5Pattern(r'\[\[(.+?)\]\]'), 'md5', 175)
        md.inlinePatterns.register(RemoveCPattern(r'\(\((.+?)\)\)'), 'remove_c', 175)
        md.parser.blockprocessors.register(ListProcessor(md.parser), 'custom_list', 25)
        md.parser.blockprocessors.register(ParagraphProcessor(md.parser), 'custom_paragraph', 175)

class ListProcessor(markdown.blockprocessors.ListProcessor):
    def __init__(self, parser):
        super().__init__(parser)

class ParagraphProcessor(markdown.blockprocessors.BlockProcessor):
    def test(self, parent, block):
        return True

    def run(self, parent, blocks):
        block = blocks.pop(0)
        p_tag = markdown.util.etree.Element('p')
        p_tag.text = block
        parent.append(p_tag)

class BoldPattern(SimpleTagPattern):
    def __init__(self, pattern):
        super().__init__(pattern, 'b')

class MD5Pattern(markdown.inlinepatterns.Pattern):
    def handleMatch(self, m):
        text = m.group(2)
        hashed_text = hashlib.md5(text.encode('utf-8')).hexdigest()
        return markdown.util.etree.Element('p', attrib={'class': 'md5'}).text, f'{hashed_text}'

class RemoveCPattern(markdown.inlinepatterns.Pattern):
    def handleMatch(self, m):
        text = m.group(2)
        text_without_c = re.sub(r'c', '', text, flags=re.IGNORECASE)
        return markdown.util.etree.Element('p', attrib={'class': 'remove_c'}).text, text_without_c

def convert_markdown_to_html(input_file, output_file):
    with open(input_file, 'r') as md_file:
        md_content = md_file.read()

    md_extensions = ['markdown.extensions.extra', CustomMarkdownExtension()]
    html_content = markdown.markdown(md_content, extensions=md_extensions)

    with open(output_file, 'w') as html_file:
        html_file.write(html_content)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.stderr.write("Usage: ./markdown2html.py <input_file.md> <output_file.html>\n")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    if not os.path.exists(input_file):
        sys.stderr.write(f"Missing {input_file}\n")
        sys.exit(1)

    convert_markdown_to_html(input_file, output_file)
