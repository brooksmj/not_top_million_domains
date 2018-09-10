import sys

if len(sys.argv) != 2:
    print('Usage: count_fields <filename>')
    print('Where filename has a log with fields to count')
    sys.exit()

else:
    with open(sys.argv[1]) as f:
        log = f.readline()
    for i, field in enumerate(log.split()):
        print('{}: {}'.format(i, field[0:50]))
