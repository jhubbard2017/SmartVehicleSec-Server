# -*- coding: utf-8 -*-
#
# module for retrieving camera stream bytes to send from server to clients
#

import cv2
from threading import Thread

from securityserverpy.sock import UDPSock
from securityserverpy import _logger


class VideoStreamer(object):
    """manages and controls camera stream data"""

    _STREAM_MIN_AREA = 500

    def __init__(self, camera, ip_address, port, no_hardware):
        """set the video object from the camera number

        Default camera # is 0. This simply enables usb camera to be used by openCV
        """
        self._camera = camera
        self.stream = cv2.VideoCapture(self._camera)
        self.no_hardware = no_hardware
        self.firstframe = None
        self._stream_running = False
        self.sock = UDPSock(ip_address, port)

    def start_stream(self):
        """starts the stream for the camera"""
        if not self.no_hardware:
            if not self._stream_running:
                self._stream_running = True
                stream_thread = Thread(target=self._stream_thread)
                stream_thread.start()
                return True
        else:
            return True

        return False


    def _stream_thread(self):
        if not self.no_hardware:
            while self._stream_running:
                status, data, _ = self.stream.get_frame()
                if status:
                    self.sock.send_data(data)
                else:
                    self.sock.send_data(404)


    def stop_stream(self):
        """stops the stream for the camera"""
        if self._stream_running:
            self._stream_running = False

        return not self._stream_running

    def release_stream(self):
        self.stream.release()

    def get_frame(self):
        """reads a frame from the camera stream and converts it to bytes to send

        returns:
            bytes
        """
        success, image = self.stream.read()
        gray_image = self.get_gray_frame(image)
        if self.firstframe is None:
            self.firstframe = gray_image
        else:
            motion_detected = self.motion_detected(gray_image)
        ret, image_jpeg = cv2.imencode('.jpg', image)
        return success, image_jpeg.tobytes(), motion_detected

    def get_gray_frame(self, frame):
        """converts frame to grayscale

        args:
            frame: image

        returns:
            image
        """
        frame = imutils.resize(frame, width=500)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        return gray

    def motion_detected(self, frame):
        """compares frames and determines of motion has been detected or not

        The first frame is considered a `no motion` frame. Comparing each of the new frames to the first frame
        will allow us to determine if motion has been detected.
            - If one of the contours in the threshold of the frame is greater than VideoStreamer._STREAM_MIN_AREA,
                    then motion has been detected
            - If one of the contours in the threshold of the frame is smaller than VideoStreamer._STREAM_MIN_AREA,
                    then motion has not been detected

        args:
            frame: image object

        returns:
            bool
        """
        detected = False
        # compute the absolute difference between the current frame and
        # first frame
        frameDelta = cv2.absdiff(self.firstframe, gray)
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

        # dilate the thresholded image to fill in holes, then find contours
        # on thresholded image
        thresh = cv2.dilate(thresh, None, iterations=2)
        (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                     cv2.CHAIN_APPROX_SIMPLE)

        # loop over the contours
        for c in cnts:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < VideoStreamer._STREAM_MIN_AREA:
                continue

            # compute the bounding box for the contour, draw it on the frame,
            # and update the text
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            detected = True

        return detected

    @property
    def stream_running(self):
        return self._stream_running

    @stream_running.setter
    def stream_running(self, value):
        pass
