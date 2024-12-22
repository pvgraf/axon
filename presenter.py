import cv2
import time
from multiprocessing.connection import Connection
from pydantic import BaseModel, Field

import logger

logger = logger.get_logger(__name__)


class PresenterConfig(BaseModel):
    """
    Configuration class for the Presenter,

    Attributes:
        conn (Connection): Connection object for data exchange between
            processes.
        enable_blurring (bool): Flag indicating whether blurring is enabled
            in the video stream.
    """
    conn: Connection
    enable_blurring: str = Field(default=True)

    class Config:
        """
        Pydantic configuration class.
        """
        # Allow the use of arbitrary types, such as multiprocessing.Connection
        arbitrary_types_allowed = True

    # The connection validation method can be added here for additional
    # checking (temporarily commented out)
    # @field_validator("conn")
    # @classmethod
    # def validate_connection(cls, conn):
    #     if not isinstance(conn, Connection):
    #         raise ValueError(
    #             "Connection must be an instance of "
    #             "multiprocessing.connection.Connection"
    #         )
    #     return conn


class Presenter:
    def __init__(self, config: PresenterConfig) -> None:
        """
        Initializes the Presenter.

        :param config: PresenterConfig object containing configuration
            settings.
        """
        self.conn = config.conn
        self.enable_blurring = config.enable_blurring
        logger.info(
            "Presenter initialized with blurring: %s", self.enable_blurring
        )

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
                    logger.info(
                        "Termination signal received. "
                        "Exiting presenter process."
                    )
                    break

                frame, detections = data
                logger.debug(
                    "Frame received with %d detections.", len(detections)
                )

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
                        # logger.debug("Applied blurring to detection at
                        # (%d, %d, %d, %d).", x, y, w, h)

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
