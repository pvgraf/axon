import multiprocessing as mp
import argparse
from pydantic import ValidationError

from streamer import Streamer, StreamerConfig
from detector import Detector, DetectorConfig
from presenter import Presenter, PresenterConfig
import logger

logger = logger.get_logger(__name__)


def main(video_path: str, blurring: bool, disable_validation: bool):
    """
    Main entry point for the video processing application.

    :param video_path: Path to the video file to be processed.
    :param blurring: Boolean flag indicating whether to apply
        blurring in the Presenter.
    :param disable_validation: Boolean flag to disable validation
        of configurations.
    """
    # Create pipes for interprocess communication
    detector_conn, presenter_conn = mp.Pipe(duplex=False)
    detector_conn2, streamer_conn = mp.Pipe(duplex=False)

    # Create and start the Streamer process
    try:
        if not disable_validation:
            streamer_config = StreamerConfig(
                conn=streamer_conn, video_path=video_path
            )
            detector_config = DetectorConfig(
                conn_in=detector_conn2, conn_out=presenter_conn
            )
            presenter_config = PresenterConfig(
                conn=detector_conn, enable_blurring=blurring
            )
        else:
            streamer_config = StreamerConfig.model_construct(
                conn=streamer_conn, video_path=video_path
            )
            detector_config = DetectorConfig.model_construct(
                conn_in=detector_conn2, conn_out=presenter_conn
            )
            presenter_config = PresenterConfig.model_construct(
                conn=detector_conn, enable_blurring=blurring
            )

        streamer = Streamer(streamer_config)
        streamer_process = mp.Process(target=streamer.run)
        streamer_process.start()

        detector = Detector(detector_config)
        detector_process = mp.Process(target=detector.run)
        detector_process.start()

        presenter = Presenter(presenter_config)
        presenter_process = mp.Process(target=presenter.run)
        presenter_process.start()

        # Wait for the processes to finish
        streamer_process.join()
        detector_process.join()
        presenter_process.join()

    except ValidationError as e:
        logger.error("Invalid configuration: %s", e)
    except Exception as e:
        logger.error("An unexpected error occurred: %s", e)
    finally:
        # Ensure that all processes are terminated if an error occurs
        if streamer_process is not None:
            streamer_process.terminate()
            streamer_process.join()
        if detector_process is not None:
            detector_process.terminate()
            detector_process.join()
        if presenter_process is not None:
            presenter_process.terminate()
            presenter_process.join()

        logger.info("All processes have been terminated.")


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

    parser.add_argument(
        "-d",
        "--disable_validation",
        action="store_true",
        help="Disable validation of pydantic module",
    )

    args = parser.parse_args()

    # Call the main function with the video path argument
    main(args.video, args.blurring, args.disable_validation)
