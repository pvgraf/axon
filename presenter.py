import cv2
import time
import multiprocessing as mp

import logger

logger = logger.get_logger(__name__)


class Presenter:
    def __init__(
        self, conn: mp.connection.Connection, enable_blurring: bool = True
    ) -> None:
        """
        Initializes the Presenter.

        :param conn: Connection for receiving processed data
            from another process.
        :param enable_blurring: Flag to enable/disable blurring of
            detected areas.
        """
        self.conn = conn
        self.enable_blurring = enable_blurring
        logger.info("Presenter initialized with blurring: %s", self.enable_blurring)

    def run(self) -> None:
        """
        Main method executed in the presenter process.
        It receives frames and detections, processes them,
        and displays the results.
        """
        logger.info("Presenter process started.")
        while True:
            try:
                # Receive data from the input connection
                data = self.conn.recv()

                # Check for termination signal
                if data is None:
                    logger.info("Termination signal received. Exiting presenter process.")
                    break

                frame, detections = data
                logger.debug("Frame received with %d detections.", len(detections))

                # Draw bounding boxes for detections
                for x, y, w, h in detections:
                    cv2.rectangle(
                        frame, (x, y), (x + w, y + h), (0, 255, 0), 2
                    )

                    if self.enable_blurring:
                        # Apply blurring to detected area
                        roi = frame[y: y + h, x: x + w]
                        blurred_roi = cv2.GaussianBlur(roi, (15, 15), 0)
                        frame[y: y + h, x: x + w] = blurred_roi
                        # logger.debug("Applied blurring to detection at (%d, %d, %d, %d).", x, y, w, h)

                # Add timestamp to the frame
                timestamp = time.strftime("%H:%M:%S")
                cv2.putText(
                    frame,
                    timestamp,
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 255, 255),
                    2,
                )

                # Display the frame
                # logger.debug("Displaying frame.")
                cv2.imshow("Video Stream", frame)

                # Wait for the calculated time (in ms)
                cv2.waitKey(1)

            except Exception as e:
                logger.error("Error in presenter process: %s", str(e))

        # Clean up and close all OpenCV windows
        cv2.destroyAllWindows()
        logger.info("Presenter process finished and OpenCV windows destroyed.")
