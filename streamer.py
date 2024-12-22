import cv2
from multiprocessing.connection import Connection
from pydantic import BaseModel, Field

import logger

logger = logger.get_logger(__name__)


class StreamerConfig(BaseModel):
    """
    Configuration class for the Streamer, including parameters for video
        streaming and connection details.

    Attributes:
        conn (Connection): Connection object for data exchange between
            processes.
        video_path (str): An string representing the path or identifier of
            the video to be streamed.
    """

    # Connection object for receiving or sending data in multiprocessing
    # context
    conn: Connection
    video_path: str = Field()

    class Config:
        """
        Pydantic configuration class.

        Attributes:
            arbitrary_types_allowed (bool): If set to True, allows fields
                to be of arbitrary types,
            including non-Pydantic types, like `multiprocessing.Connection`.
        """

        # Allow the use of arbitrary types in the model, which is necessary
        # for `Connection` type
        arbitrary_types_allowed = True


class Streamer:
    def __init__(self, config: StreamerConfig) -> None:
        """
        Initializes the Streamer.

        :param config: StreamerConfig object containing configuration settings.
        """
        self.video_path = config.video_path
        self.conn = config.conn
        logger.info(
            "Streamer initialized with video path: %s", self.video_path
        )

    def run(self) -> None:
        """
        Main method executed in the streamer process.
        It reads frames from the video file and sends them to
        the connected process.
        """
        logger.info("Starting video streaming from: %s", self.video_path)

        # Open the video file
        cap = cv2.VideoCapture(self.video_path)

        # Check if the video was opened successfully
        if not cap.isOpened():
            logger.error(
                "Error: Could not open video file: %s", self.video_path
            )
            # Send None to indicate failure
            self.conn.send(None)
            self.conn.close()
            return

        # Read frames from the video
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.info("End of video stream reached.")
                break

            self.conn.send(frame)
            # logger.debug("Frame sent to the connected process.")

        # Release the video capture object
        cap.release()
        logger.info("Video capture released.")

        # Signal that the stream is finished
        self.conn.send(None)
        logger.info("Signaled that the video stream is finished.")
        self.conn.close()
