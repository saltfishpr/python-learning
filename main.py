import argparse
import logging
import sys
from datetime import timedelta
import cv2
import easyocr
import pandas as pd
from fuzzywuzzy import fuzz

# Initialize EasyOCR reader
reader = easyocr.Reader(["en"])

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def adjust_roi_interactively(frame, initial_roi):
    """Interactive ROI adjustment using mouse"""
    roi = initial_roi.copy()
    drawing = False
    start_x, start_y = 0, 0
    end_x, end_y = 0, 0

    def draw_rectangle(event, x, y, flags, param):
        nonlocal start_x, start_y, end_x, end_y, drawing
        if event == cv2.EVENT_LBUTTONDOWN:
            drawing = True
            start_x, start_y = x, y
        elif event == cv2.EVENT_MOUSEMOVE:
            if drawing:
                end_x, end_y = x, y
        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            # Ensure minimum ROI size
            if abs(end_x - start_x) < 10 or abs(end_y - start_y) < 10:
                end_x = start_x + 100
                end_y = start_y + 100

    cv2.namedWindow("Adjust ROI")
    cv2.setMouseCallback("Adjust ROI", draw_rectangle)

    while True:
        display_frame = frame.copy()

        roi[0] = min(start_x, end_x)  # left
        roi[1] = min(start_y, end_y)  # top
        roi[2] = max(start_x, end_x)  # right
        roi[3] = max(start_y, end_y)  # bottom
        cv2.rectangle(display_frame, (roi[0], roi[1]), (roi[2], roi[3]), (0, 255, 0), 2)
        cv2.imshow("Adjust ROI", display_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 13:  # Enter key
            break
        elif key == 27:  # ESC key
            roi = initial_roi
            break

    cv2.destroyWindow("Adjust ROI")
    return roi


def select_roi(video_path):
    """Select ROI from the first frame of the video"""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"Could not open video {video_path}")
        return None

    ret, frame = cap.read()
    if not ret:
        logger.error("Could not read video frame")
        return None

    initial_roi = [50, 1520, 150, 1870]  # x1, y1, x2, y2
    adjusted_roi = adjust_roi_interactively(frame, initial_roi)

    logger.info(
        f"Selected ROI: left={adjusted_roi[0]}, top={adjusted_roi[1]}, right={adjusted_roi[2]}, bottom={adjusted_roi[3]}"
    )

    cap.release()
    return adjusted_roi


def preprocess_image(frame):
    """Preprocess image for better OCR accuracy"""
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    # Apply median blur to reduce noise
    filtered = cv2.medianBlur(thresh, 3)
    return filtered


def is_match(text, player_id, threshold=80):
    """Check if text matches player_id using fuzzy matching"""
    return fuzz.partial_ratio(text.lower(), player_id.lower()) >= threshold


def process_video(
    video_path, output_path, roi, player_id, frame_interval=100, show_progress=True
):
    """Process video with the selected ROI
    Args:
        video_path: Path to input video
        output_path: Path to output CSV
        roi: Region of interest coordinates [x1, y1, x2, y2]
        player_id: Player ID to track
        frame_interval: Time interval between processed frames in milliseconds
        show_progress: Whether to show processing progress window
    """
    # Initialize variables
    kill_data = []

    # Open video file
    logger.info(f"Processing video: {video_path}")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"Could not open video {video_path}")
        return

    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = 0

    # Calculate frame skip based on interval
    frame_skip = max(1, int(fps * frame_interval / 1000))
    logger.info(
        f"Processing 1 frame every {frame_skip} frames (interval: {frame_interval}ms)"
    )

    last_text = ""

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame_count += 1

        # Skip frames
        if frame_count % frame_skip != 0:
            continue

        # Calculate current timestamp
        timestamp = str(timedelta(seconds=frame_count / fps))

        # Show processing progress if enabled
        if show_progress:
            progress = frame_count / int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) * 100
            display_frame = frame.copy()
            cv2.rectangle(
                display_frame, (roi[0], roi[1]), (roi[2], roi[3]), (0, 255, 0), 2
            )
            cv2.putText(
                display_frame,
                f"Processing: {progress:.1f}%",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )
            cv2.imshow("Processing", display_frame)
            cv2.waitKey(1)

        try:
            # Extract ROI
            roi_frame = frame[roi[1] : roi[3], roi[0] : roi[2]]

            # Only process if there's significant change
            results = reader.readtext(roi_frame)
            text = " ".join([result[1] for result in results])

            logger.debug(f"Frame {frame_count} OCR text: {text}")

            # Skip if text is similar to previous frame
            # TODO 可以优化
            if fuzz.ratio(text, last_text) > 90:
                continue
            last_text = text

            # Check for kill information using fuzzy matching
            if is_match(text, player_id):
                kill_data.append({"timestamp": timestamp, "kill_text": text.strip()})

        except Exception as e:
            logger.warning(f"OCR failed on frame {frame_count}: {str(e)}")
            continue

    # Release video capture
    cap.release()

    # Save results to CSV
    if kill_data:
        df = pd.DataFrame(kill_data)
        df.to_csv(output_path, index=False)
        logger.info(f"Saved {len(kill_data)} kills to {output_path}")
    else:
        logger.info("No kills found")


def main():
    """Main function to process PUBG video and track kills"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="PUBG Kill Tracker")
    parser.add_argument("--input", required=True, help="Input video file path")
    parser.add_argument("--output", required=True, help="Output CSV file path")
    parser.add_argument("--player_id", required=True, help="Player ID to track")
    parser.add_argument(
        "--frame_interval",
        type=int,
        default=100,
        help="Time interval between processed frames in milliseconds (default: 100)",
    )
    parser.add_argument(
        "--show_progress", action="store_true", help="Show processing progress window"
    )
    args = parser.parse_args()

    # Step 1: Select ROI
    roi = select_roi(args.input)
    if roi is None:
        logger.error("Failed to select ROI")
        return

    # Step 2: Process video with selected ROI
    process_video(
        args.input,
        args.output,
        roi,
        args.player_id,
        args.frame_interval,
        args.show_progress,
    )


if __name__ == "__main__":
    main()
