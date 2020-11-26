#!/usr/bin/env python3

import argparse
import logging
from pathlib import Path
import re
import sys


class FileEditor:
    def __init__(self, filename):
        self.filename = filename
        if not self.filename.exists():
            raise FileExistsError(f'{self.filename} does not exist.  Check your file path.')

    def read_contents(self):
        logging.debug('Reading contents of %s', str(self.filename))
        with open(str(self.filename)) as file:
            return [line for line in file]

    def write_contents(self, contents):
        logging.debug('Writing contents of %s', str(self.filename))
        with open(str(self.filename), 'w') as file:
            file.writelines(contents)

    def run(self, new_version):
        logging.debug('Starting processing of %s', str(self.filename))
        edited_contents = [self.edit(line, new_version) for line in self.read_contents()]
        self.write_contents(edited_contents)
        logging.debug('Finished processing of %s', str(self.filename))

    def edit(self, line, new_version):
        raise NotImplementedError


class AiospamcInit(FileEditor):
    def __init__(self, project_path: Path):
        super().__init__(project_path / 'aiospamc' / '__init__.py')

    def edit(self, line, new_version):
        logging.debug('File: %s; Line: %s', str(self.filename), line)
        if re.match(r'^__version__[ \t]*=[ \t]*"\d+\.\d+\.\d+"', line):
            logging.info('Match found for %s', str(self.filename))
            new_line = re.sub(r'\d+\.\d+\.\d+', new_version, line)

            logging.info('Changed line')
            logging.info('\tOld: %s', repr(line))
            logging.info('\tNew: %s', repr(new_line))

            return new_line
        else:
            return line


class SphinxDocs(FileEditor):
    def __init__(self, project_path: Path):
        super().__init__(project_path / 'docs' / 'conf.py')

    def edit(self, line, new_version):
        if re.match(r"^version[ \t]*=[ \t]*'\d+\.\d+'", line):
            short_version = new_version.rpartition('.')[0]
            return re.sub(r'\d+\.\d+', short_version, line)
        elif re.match(r"^release[ \t]*=[ \t]*'\d+\.\d+\.\d+'", line):
            logging.info('Match found for %s', str(self.filename))
            new_line = re.sub(r'\d+\.\d+\.\d+', new_version, line)

            logging.info('Changed line')
            logging.info('\tOld: %s', repr(line))
            logging.info('\tNew: %s', repr(new_line))

            return new_line
        else:
            return line


class PyProject(FileEditor):
    def __init__(self, project_path: Path):
        super().__init__(project_path / 'pyproject.toml')

    def edit(self, line, new_version):
        if re.match(r'^version[ \t]*=[ \t]*"\d+\.\d+\.\d+"', line):
            logging.info('Match found for %s', str(self.filename))
            new_line = re.sub(r'\d+\.\d+\.\d+', new_version, line)

            logging.info('Changed line')
            logging.info('\tOld: %s', repr(line))
            logging.info('\tNew: %s', repr(new_line))

            return new_line
        else:
            return line


def main():
    parser = argparse.ArgumentParser(description='Increment project version')
    parser.add_argument('VERSION', help='Version string to write.')
    parser.add_argument('-p', '--path', default='.', help='Path to the root of the project.')
    parser.add_argument('-v', '--verbose', action='store_const', const=True, default=False, help='Enable debug logging.')
    args = parser.parse_args()

    if args.verbose is True:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logging.basicConfig(level=log_level, format='{message}', style='{')

    project_path = Path(args.path).resolve()
    if not project_path.exists():
        logging.error('Could not find project path at: %s', str(project_path))
        sys.exit(-1)

    logging.debug('Starting')

    files = [AiospamcInit(project_path), SphinxDocs(project_path), PyProject(project_path)]
    for file in files:
        file.run(args.VERSION)

    logging.debug('Done')


if __name__ == '__main__':
    main()
