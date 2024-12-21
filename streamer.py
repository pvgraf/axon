import cv2
from multiprocessing.connection import Connection


class Streamer:
    def __init__(self, video_path: str, conn: Connection) -> None:
        """
        Initializes the Streamer.

        :param video_path: Path to the video file to be streamed.
        :param conn: Connection object for sending frames to another process.
        """
        self.video_path = video_path
        self.conn = conn

    def run(self) -> None:
        """
        Main method executed in the streamer process.
        It reads frames from the video file and sends them to
        the connected process.
        """
        # Open the video file
        cap = cv2.VideoCapture(self.video_path)

        # Check if the video was opened successfully
        if not cap.isOpened():
            print(f"Error: Could not open video file: {self.video_path}")
            # Send None to indicate failure
            self.conn.send(None)
            self.conn.close()
            return

        # Read frames from the video
        while True:
            ret, frame = cap.read()
            if not ret:
                # Exit loop if no frame is returned
                break

            self.conn.send(frame)

        # Release the video capture object
        cap.release()

        # Signal that the stream is finished
        self.conn.send(None)
        self.conn.close()
