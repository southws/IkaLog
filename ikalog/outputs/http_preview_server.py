#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2015 Takeshi HASEGAWA
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

from http.server import HTTPServer, SimpleHTTPRequestHandler
import time
import threading
import os

import cv2

# FIXME
connections = []
jpeg_latest = None


class PreviewHTTPRequestHandler(SimpleHTTPRequestHandler):

    def do_GET(self):
        global connections
        connections.append(self)

        self.send_response(200)
        self.send_header(
            'Content-type', 'multipart/x-mixed-replace; boundary=--frame_boundary')
        self.end_headers()

        self.new_image = True

        while True:
            time.sleep(0.1)

            if (not self.new_image) or (jpeg_latest is None):
                continue

            jpeg = jpeg_latest
            jpeg_length = len(jpeg_latest)
            self.new_image = False

            self.wfile.write('--frame_boundary\r\n'.encode('utf-8'))
            self.send_header('Content-type', 'image/jpeg')
            self.send_header('Content-length', str(jpeg_length))
            self.end_headers()
            self.wfile.write(jpeg)


class HTTPPreviewServer(object):

    last_update = 0

    def on_show_preview(self, context):
        result, jpeg = cv2.imencode('.jpg', context['engine']['frame'])
        if not result:
            return

        global jpeg_latest
        jpeg_latest = jpeg

        for con in connections:
            con.new_image = True

    def _server_thread(self):
        self.server = HTTPServer(('', 8888), PreviewHTTPRequestHandler)
        print('serving!')
        self.server.serve_forever()

    def __init__(self):
        thread = threading.Thread(target=self._server_thread, args=())
        thread.daemon = True
        thread.start()
