import sys
import struct
def _bin_splitter(filehandle):
    marker = b'\xA3\x95'
    blocksize = 4096
    current = b''
    result = b''
    for block in iter(lambda: filehandle.read(blocksize), b''):
        current += block
        while True:
            markerpos = current.find(marker)
            if markerpos == -1:
                break
            result = current[:markerpos]
            current = current[markerpos + len(marker):]
            yield result
    yield current

if __name__ == "__main__":
    filename = sys.argv[1]
    with open(filename, 'rb') as fh:
        for line in _bin_splitter(fh):
            if line != b'':
                if line[-2:] != b'\x00\x00':
                    print(line)
                if line[0] == 128:
                    (__, fmt_type, fmt_len, name, fmt_str, lables) = struct.unpack("BBB4s16s64s", line[:87])
                    print(fmt_type, fmt_len, name.decode('ascii'), fmt_str.decode('ascii'), lables.decode('ascii'))
