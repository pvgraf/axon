import cv2
from multiprocessing.connection import Connection

import logger

logger = logger.get_logger(__name__)


class Streamer:
    def __init__(self, video_path: str, conn: Connection) -> None:
        """
        Initializes the Streamer.

        :param video_path: Path to the video file to be streamed.
        :param conn: Connection object for sending frames to another process.
        """
        self.video_path = video_path
        self.conn = conn
        logger.info("Streamer initialized with video path: %s", video_path)

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
            logger.error("Error: Could not open video file: %s", self.video_path)
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
