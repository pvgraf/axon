import multiprocessing as mp
import argparse

from streamer import Streamer
from detector import Detector
from presenter import Presenter


def main(video_path: str, blurring: bool):
    """
    Main entry point for the video processing application.

    :param video_path: Path to the video file to be processed.
    :param blurring: Boolean flag indicating whether to apply
        blurring in the Presenter.
    """
    # Create pipes for interprocess communication
    detector_conn, presenter_conn = mp.Pipe(duplex=False)
    detector_conn2, streamer_conn = mp.Pipe(duplex=False)

    # Create and start the Streamer process
    streamer = Streamer(video_path, streamer_conn)
    streamer_process = mp.Process(target=streamer.run)
    streamer_process.start()

    # Create and start the Detector process
    detector = Detector(detector_conn2, presenter_conn)
    detector_process = mp.Process(target=detector.run)
    detector_process.start()

    # Create and start the Presenter process
    presenter = Presenter(detector_conn, blurring)
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
        "-v", "--video", type=str, required=True,
        help="Path to the input video file"
    )

    parser.add_argument(
        "-b",
        "--blurring",
        action="store_true",
        help="Enable blurring of detected objects",
    )

    args = parser.parse_args()

    # Call the main function with the video path argument
    main(args.video, args.blurring)
