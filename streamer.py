import cv2
import multiprocessing as mp


class Streamer:
    """
    A class for streaming video data from a specified video file.
    """

    def __init__(self, video_path: str, detector_queue: mp.Queue):
        """
        Initializes the Streamer with the given video path and detector queue.

        Args:
            video_path (str): The path to the video file.
            detector_queue (mp.Queue): A multiprocessing queue for sending
                frames to the detector.
        """
        self.video_path = video_path
        self.detector_queue = detector_queue

    def run(self) -> None:
        """
        Starts reading the video file and sending frames to the detector queue.
        """
        # Attempt to open the video file
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            self.detector_queue.put(None)
            raise RuntimeError(f"Error: Unable to open video file {self.video_path}")

        # Continuously read frames from the video until the end
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Send the frame to the detector queue
            self.detector_queue.put(frame)

        # Release the video capture object and signal completion
        cap.release()

        # Signal that there are no more frames to process
        self.detector_queue.put(None)
