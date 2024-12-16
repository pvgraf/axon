import cv2
import time
import multiprocessing as mp


class Presenter:
    """
    A class for presenting processed video frames with detected contours.
    Optionally applies blurring to detected areas (enabled by default).
    """

    def __init__(
            self,
            presenter_queue: mp.Queue,
            enable_blurring: bool = True):
        """
        Initializes the Presenter with the provided queue and blurring option.

        Args:
            presenter_queue (mp.Queue): A multiprocessing queue for receiving
            frames with detections.
            enable_blurring (bool): Flag to enable or disable blurring
                of detections.
        """
        self.presenter_queue = presenter_queue
        self.enable_blurring = enable_blurring

    def run(self) -> None:
        """
        Displays video frames with detected contours and optionally blurs them.
        """
        while True:
            # Retrieve data from the presenter queue
            data = self.presenter_queue.get()
            if data is None:
                # Exit the loop if termination signal is received
                break

            frame, detections = data

            # Process detected contours
            for x, y, w, h in detections:
                # Draw bounding box for detected contour
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                if self.enable_blurring:
                    # Apply blurring to detected area
                    roi = frame[y:y+h, x:x+w]
                    blurred_roi = cv2.GaussianBlur(roi, (15, 15), 0)
                    frame[y:y+h, x:x+w] = blurred_roi

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
