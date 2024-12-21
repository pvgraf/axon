import cv2
import imutils
import time
import multiprocessing as mp
from typing import Tuple, List


class Detector:
    def __init__(
        self, conn_in: mp.connection.Connection,
        conn_out: mp.connection.Connection
    ) -> None:
        """
        Initializes the Detector.

        :param conn_in: Connection for receiving frames from another process.
        :param conn_out: Connection for sending detection
            results to another process.
        """
        self.conn_in = conn_in
        self.conn_out = conn_out
        self.counter = 0
        self.prev_frame = None

    def run(self) -> None:
        """
        Main method executed in the detector process.
        It receives frames, processes them, and sends detection results.
        """
        while True:
            # Receive frame from the input connection
            frame = self.conn_in.recv()

            # Check for termination signal
            if frame is None:
                self.conn_out.send(None)  # Signal that processing is done
                break

            start_time = time.time()  # Start time for processing

            # Convert the frame to grayscale
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if self.counter == 0:
                self.prev_frame = gray_frame  # Initialize the first frame
                self.counter += 1
            else:
                # Compute the difference between the current frame and
                # the previous frame
                diff = cv2.absdiff(gray_frame, self.prev_frame)
                thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
                thresh = cv2.dilate(thresh, None, iterations=2)

                # Find contours in the thresholded image
                cnts = cv2.findContours(
                    thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
                )
                cnts = imutils.grab_contours(cnts)

                # Initialize a list to hold detections
                detections: List[Tuple[int, int, int, int]] = []
                for contour in cnts:
                    # Compute the bounding rectangle for each detected contour
                    (x, y, w, h) = cv2.boundingRect(contour)
                    # Add the bounding rectangle coordinates to the detections
                    # list
                    detections.append((x, y, w, h))

                # Update previous frame
                self.prev_frame = gray_frame
                self.counter += 1

                # Send the frame and detections to the output connection
                self.conn_out.send((frame, detections))

            # Measure processing time
            end_time = time.time()
            print(
                "Detector processing time: ",
                f"{(end_time - start_time) * 1000:.2f} ms",
            )
