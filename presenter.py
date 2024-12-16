import cv2
import time
import multiprocessing as mp


class Presenter:
    """
    A class for presenting processed video frames with detected contours.
    """

    def __init__(self, presenter_queue: mp.Queue):
        """
        Initializes the Presenter with the provided queue.

        Args:
            presenter_queue (mp.Queue): A multiprocessing queue for receiving
            frames with detections.
        """
        self.presenter_queue = presenter_queue

    def run(self) -> None:
        """
        Displays video frames with detected contours.
        """
        while True:
            # Retrieve data from the presenter queue
            data = self.presenter_queue.get()
            if data is None:

                # Exit the loop if termination signal is received
                break

            frame, detections = data

            # Draw bounding boxes for detected contours
            for x, y, w, h in detections:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Get the current timestamp to display on the frame
            timestamp = time.strftime("%H:%M:%S")
            cv2.putText(
                frame,
                timestamp,
                (10, 30),
                cv2.FONT_HERSHEY_TRIPLEX,
                1,
                (255, 255, 255),
                2,
            )

            # Display the frame
            cv2.imshow("Video Stream", frame)

            # wait for 1 ms;
            # this is necessary for window events to work properly
            cv2.waitKey(1)

        # Clean up: close all OpenCV windows
        cv2.destroyAllWindows()
