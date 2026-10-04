#!/usr/bin/env python
"""Capture a genuine framebuffer from an existing loopback VNC server.

No desktop startup, input injection, credential handling or security changes.
Only unauthenticated, locally bound RFB 3.8 endpoints are supported.
"""
import argparse
from pathlib import Path
import socket
import struct
import time

from PIL import Image


def capture(port, output):
    with socket.create_connection(('127.0.0.1', port), timeout=10) as connection:
        connection.settimeout(10)
        deadline = time.monotonic() + 20

        def read(size):
            data = bytearray()
            while len(data) < size:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError('Framebuffer capture exceeded 20 seconds')
                connection.settimeout(min(10, remaining))
                block = connection.recv(size - len(data))
                if not block:
                    raise RuntimeError('Framebuffer connection ended before completion')
                data.extend(block)
            return bytes(data)

        if read(12) != b'RFB 003.008\n':
            raise RuntimeError('Require an existing RFB 3.8 server')
        connection.sendall(b'RFB 003.008\n')
        count = read(1)[0]
        if not count or 1 not in read(count):
            raise RuntimeError('This helper does not handle VNC credentials')
        connection.sendall(b'\1')
        if read(4) != b'\0' * 4:
            raise RuntimeError('Local framebuffer access denied')
        connection.sendall(b'\1')  # Shared: preserve the existing viewer.
        header = read(24)
        width, height = struct.unpack('>HH', header[:4])
        name_length = struct.unpack('>I', header[20:24])[0]
        if not width or not height or width * height > 20_000_000 or name_length > 4096:
            raise RuntimeError('Unexpected framebuffer dimensions or name')
        read(name_length)
        canvas = Image.new('RGB', (width, height))
        pixel_format = struct.pack('>BBBBHHHBBBxxx', 32, 24, 0, 1, 255, 255, 255, 16, 8, 0)
        connection.sendall(b'\0' * 4 + pixel_format)
        connection.sendall(struct.pack('>BBHi', 2, 0, 1, 0))  # Raw rectangles.
        connection.sendall(struct.pack('>BBHHHH', 3, 0, 0, 0, width, height))
        area = 0
        for _ in range(20):
            kind = read(1)[0]
            if kind == 2:  # Bell has no payload.
                continue
            if kind != 0:
                raise RuntimeError('Unexpected framebuffer message')
            rectangles = struct.unpack('>H', read(3)[1:])[0]
            if rectangles > 4096:
                raise RuntimeError('Unexpected rectangle count')
            for _ in range(rectangles):
                x, y, w, h, encoding = struct.unpack('>HHHHi', read(12))
                if encoding != 0 or x + w > width or y + h > height or not w or not h:
                    raise RuntimeError('Unexpected raw framebuffer rectangle')
                canvas.paste(Image.frombytes('RGB', (w, h), read(w * h * 4), 'raw', 'BGRX'), (x, y))
                area += w * h
            if area >= width * height:
                if output.is_symlink():
                    raise ValueError('Refuse a symlink output')
                canvas.save(output, format='PNG')
                return width, height
        raise RuntimeError('Full framebuffer was not delivered')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', required=True, type=int)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error('Invalid local VNC port')
    width, height = capture(args.port, args.output)
    print(f'Captured genuine {width}x{height} framebuffer: {args.output}')


if __name__ == '__main__':
    main()
