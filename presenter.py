import cv2
import time
import multiprocessing as mp


class Presenter:
    def __init__(
        self, conn: mp.connection.Connection, enable_blurring: bool = True
    ) -> None:
        """
        Initializes the Presenter.

        :param conn: Connection for receiving processed data
            from another process.
        """
        self.conn = conn
        self.enable_blurring = enable_blurring

    def run(self) -> None:
        """
        Main method executed in the presenter process.
        It receives frames and detections, processes them,
        and displays the results.
        """
        while True:
            # Receive data from the input connection
            data = self.conn.recv()

            # Check for termination signal
            if data is None:
                break

            frame, detections = data
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
            cv2.imshow("Video Stream", frame)

            # Wait for the calculated time (in ms)
            cv2.waitKey(1)

        # Clean up and close all OpenCV windows
        cv2.destroyAllWindows()
