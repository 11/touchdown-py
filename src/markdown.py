import re
import json
from pprint import pformat
from pathlib import Path

import utils
from constants import tokens as tks
from errors import MarkdownSyntaxError


class Markdown:
    def __init__(self, file):
        self._filepath = Path(file)
        self._lineno = 0

        self._reader = None

    def __repr__(self):
        return f'File {self._filename} - Lines processed {self._lineno}'

    def __str__(self):
        return pformat(self.parse())

    def __iter__(self):
        self._reader = utils.read_file(self._filepath)
        return self

    def __next__(self):
        line = next(self._reader, None)
        if not line:
            raise StopIteration

        self._lineno += 1

        if re.match(tks['header'], line):
            return self._parse_header(line)
        elif re.match(tks['blockquote'], line):
            return self._parse_blockquote(line)
        elif re.match(tks['ordered_list'], line):
            return self._parse_ordered_list(self._reader)
        elif re.match(tks['unordered_list'], line):
            return self._parse_unordered_list(slef._reader)
        elif re.match(tks['image'], line):
            print('image')
        elif re.match(tks['codeblock'], self._reader):
            print('codeblock')
        else:
            print('paragraph')

    def file(self):
        return self._filepath

    def parse(self):
        if not self._filepath:
            raise FileNotFoundError

        return {
            'filename': self._filepath.name,
            'filepath': self._filepath,
            'content': [token for token in self],
        }

    def _parse_header(self, line):
        match = re.findall(tks['header'], line)
        if len(match) > 1:
            raise MarkdownSyntaxError(self._file, self._lineno, '')
        elif len(match) < 1:
            raise MarkdownSyntaxError(self._file, self._lineno, '')

        header, content = match[0]
        if not header or not content:
            return None

        return {
            'token': 'header',
            'tag': f'h{len(header)}',
            'content': content,
        }

    def _parse_blockquote(self, line):
        match = re.findall(tks['blockquote'], line)
        if len(match) > 1:
            raise MarkdownSyntaxError(self._file, self._lineno, '')
        elif len(match) < 1:
            raise MarkdownSyntaxError(self._file, self._lineno, '')

        blockquote, content = match[0]
        if not blockquote or not content:
            return None

        return {
            'token': 'blockquote',
            'tag': 'blockquote',
            'content': content,
        }

    def _parse_image(self, line):
        pass

    def _parse_codeblock(self, line, reader):
        match = re.findall(tks['codeblock'], line)
        if len(match) > 1:
            raise MarkdownSyntaxError(self._file, self._lineno, '')
        elif len(match) < 1:
            raise MarkdownSyntaxError(self._file, self._lineno, '')

        codeblock, content = match[0]
        if not codeblock or not content:
            return None

        return {
            'token': 'codeblock',
            'tag': 'pre',
            'content': content,
        }

    def _parse_list(self, reader, list_type, list_tag):
        reader.backstep() # reset the file generator back to the beginning of the ordered list

        output = {
            'element': list_type,
            'tag': list_tag,
            'content': [],
        }

        while (line := next(reader, None)):
            match = None
            if re.match(tks['ordered_list'], line):
                match = re.findall(tks['ordered_list'], line)
            else:
                reader.backstep()
                break

            if len(match) > 1 or len(match < 1):
                raise MarkdownSyntaxError(self._file, self._lineno, '')

            _, content = match[0]
            output['content'].append({
                'token': 'listitem',
                'tag': 'li',
                'content': content,
            })

        return output

    def _parse_ordered_list(self, reader):
        return self._parse_list(reader, 'ordered_list', 'ol')

    def _parse_unordered_list(self, line):
        return self._parse_list(reader, 'unordered_list', 'ul')

    def _parse_link(self, line, seek=0):
        pass

    def _parse_decoration(self, line, seek=0):
        pass

    def _parse_text(self, line):
        decors = set('*', '_', '~', '/', '`', '[')
        output = {
            'element': 'paragraph',
            'tag': 'p',
            'content': [],
        }

        start = 0
        end = 0
        while end < len(line):
            cur = line[idx]
            prev = line[idx-1] if idx > 0 else 0

            if prev != '\\' and cur in decors:
                # append plain text to output and reset sliding window
                text = { 'element': 'text', 'content': line[start:end] }
                output['content'].append(text)
                start = end

                if cur == '[':
                    link = self._parse_link(self, line, idx)
                    output['content'].append(link)
                else:
                    decor = self._parse_decoration(self, line, idx);
                    output['content'].append(decor)

            end += 1

        return output

