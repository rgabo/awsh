from __future__ import unicode_literals, print_function

from prompt_toolkit import prompt


def main():
    while True:
        try:
            prompt('>>> ')
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == '__main__':
    main()
