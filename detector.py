import cv2
import imutils
import multiprocessing as mp
from typing import Optional, Tuple, List


class Detector:
    """
    A class for detecting motion in video frames.

    Note:
        The implementation is taken from the provided example;
        only the usage of the queue has been added.
    """

    def __init__(self, detector_queue: mp.Queue, presenter_queue: mp.Queue):
        """
        Initializes the Detector with the provided queues.

        Args:
            detector_queue (mp.Queue): A multiprocessing queue for receiving
                frames from the Streamer.
            presenter_queue (mp.Queue): A multiprocessing queue for sending
                frames to the Presenter.
        """
        self.detector_queue = detector_queue
        self.presenter_queue = presenter_queue
        self.counter = 0
        self.prev_frame: Optional[cv2.Mat] = None

    def run(self) -> None:
        """
        Processes video frames to detect motion and send detections
            to the presenter.
        """
        while True:
            # Retrieve a frame from the detector queue
            frame: Optional[cv2.Mat] = self.detector_queue.get()
            if frame is None:
                self.presenter_queue.put(None)
                break

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if self.counter == 0:
                self.prev_frame = gray_frame
                self.counter += 1
            else:
                diff = cv2.absdiff(gray_frame, self.prev_frame)
                thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
                thresh = cv2.dilate(thresh, None, iterations=2)
                cnts = cv2.findContours(
                    thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
                )
                cnts = imutils.grab_contours(cnts)

                detections: List[Tuple[int, int, int, int]] = []
                for contour in cnts:
                    # Compute the bounding rectangle for each detected contour
                    (x, y, w, h) = cv2.boundingRect(contour)
                    # Add the bounding rectangle coordinates to the detections
                    # list
                    detections.append((x, y, w, h))

                self.prev_frame = gray_frame
                self.counter += 1

                # Send the frame and detections to the presenter queue
                self.presenter_queue.put((frame, detections))
