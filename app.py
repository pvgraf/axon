import multiprocessing as mp
import argparse

from streamer import Streamer
from detector import Detector
from presenter import Presenter


def main(video_path: str, blurring: bool):
    """
    Main function to initialize and run the streaming, detection,
    and presentation processes.

    This function sets up multiprocessing for video streaming, object
    detection, and visualization with options for blurring detected objects.

    Args:
        video_path (str):
            The file path to the input video that will be processed.
        blurring (bool):
            A flag indicating whether to apply blurring to detected objects.
            If True, detected objects will be blurred in the presenter output.
    """

    # Create queues for communication between processes
    detector_queue = mp.Queue()
    presenter_queue = mp.Queue()

    # Create and start the Streamer process
    streamer = Streamer(video_path, detector_queue)
    streamer_process = mp.Process(target=streamer.run)
    streamer_process.start()

    # Create and start the Detector process
    detector = Detector(detector_queue, presenter_queue)
    detector_process = mp.Process(target=detector.run)
    detector_process.start()

    # Create and start the Presenter process
    presenter = Presenter(presenter_queue, blurring)
    presenter_process = mp.Process(target=presenter.run)
    presenter_process.start()

    # Wait for the processes to finish
    streamer_process.join()
    detector_process.join()
    presenter_process.join()


if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(
        description="Motion Detection Application (AXON)"
    )

    parser.add_argument(
        "-v", "--video",
        type=str, required=True, help="Path to the input video file"
    )

    parser.add_argument(
        "-b", "--blurring",
        action='store_true', help="Enable blurring of detected objects"
    )

    args = parser.parse_args()

    # Call the main function with the video path argument
    main(args.video, args.blurring)
