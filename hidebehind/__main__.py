from hidebehind.image import ImageSecret
import argparse
from sys import stdin, stdout, argv


def main():
    print(argv)
    parser = argparse.ArgumentParser(prog='hide')
    parser.add_argument('mode', choices=('embed', 'extract', 'put', 'get'), nargs=1, help='abc')
    parser.add_argument('--cover', '-c', default='-', help='Dest of the embedded image OR original image.')
    parser.add_argument('--secret', '-s', default='-', help='The secret to be embedded in the cover file.')
    parser.add_argument('--output', '-o', default='-', help='Dest for embedded image OR extracted secret.')

    args = parser.parse_args()

    if args.mode[0] in ('embed', 'put'):
        cover_file = args.cover
        output_file = args.output

        if args.secret == '-' and args.cover == '-':
            raise Exception("You didn't specified the cover file nor the secret file. Use --cover OR --secret OR both. "
                            "See --help")

        if args.secret == '-':
            secret_contents = stdin.buffer.read()
        else:
            with open(args.secret, 'rb') as secret_file:
                secret_contents = secret_file.read()

        if args.cover == '-':
            cover_file = stdin.buffer

        if args.output == '-':
            output_file = stdout.buffer

        ImageSecret(cover_file).embed(secret_contents).save(output_file)
    else:
        cover_file = stdin.buffer if args.cover == '-' else args.cover

        secret = ImageSecret(cover_file).extract()

        # Output the secret
        if args.output == '-':
            stdout.buffer.write(secret)
        else:
            with open(args.output, 'wb') as output_file:
                output_file.write(secret)


if __name__ == '__main__':
    main()
