# SPDX-FileCopyrightText: Copyright (c) 2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import cv2
import logging
import matplotlib.pyplot as plt
import PIL.Image
import time
from typing import Optional
from nanoowl.tree import Tree
from nanoowl.tree_predictor import TreePredictor
from nanoowl.tree_drawing import draw_tree_output
from nanoowl.owl_predictor import OwlPredictor


def get_colors(count: int):
    cmap = plt.cm.get_cmap("rainbow", count)
    colors = []
    for i in range(count):
        color = cmap(i)
        color = [int(255 * value) for value in color]
        colors.append(tuple(color))
    return colors


def cv2_to_pil(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return PIL.Image.fromarray(image)


def process_video(
    video_path: str,
    output_path: str,
    image_encode_engine: str,
    prompt: str,
    output_fps: Optional[float] = None,
    resize_resolution: Optional[str] = None
):
    logging.info(f"Processing video: {video_path}")
    logging.info(f"Output path: {output_path}")
    logging.info(f"Prompt: {prompt}")

    # Initialize the predictor
    predictor = TreePredictor(
        owl_predictor=OwlPredictor(
            image_encoder_engine=image_encode_engine
        )
    )

    # Parse the prompt
    try:
        tree = Tree.from_prompt(prompt)
        clip_encodings = predictor.encode_clip_text(tree)
        owl_encodings = predictor.encode_owl_text(tree)
        prompt_data = {
            "tree": tree,
            "clip_encodings": clip_encodings,
            "owl_encodings": owl_encodings
        }
        logging.info("Parsed prompt: " + prompt)
    except Exception as e:
        logging.error(f"Error parsing prompt: {e}")
        return

    # Open the video file
    video = cv2.VideoCapture(video_path)
    if not video.isOpened():
        logging.error(f"Could not open video file: {video_path}")
        return

    # Get video properties
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = video.get(cv2.CAP_PROP_FPS)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Apply resize if specified
    if resize_resolution:
        width, height = map(int, resize_resolution.split("x"))

    # Use provided output FPS or original video FPS
    if output_fps is None:
        output_fps = fps

    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # You can change the codec as needed
    out = cv2.VideoWriter(output_path, fourcc, output_fps, (width, height))

    # Process the video
    frame_count = 0
    total_processing_time = 0

    while True:
        ret, frame = video.read()
        if not ret:
            break

        # Resize if needed
        if resize_resolution:
            frame = cv2.resize(frame, (width, height))

        # Convert to PIL image
        image_pil = cv2_to_pil(frame)

        # Process the frame
        t0 = time.perf_counter_ns()
        detections = predictor.predict(
            image_pil,
            tree=prompt_data['tree'],
            clip_text_encodings=prompt_data['clip_encodings'],
            owl_text_encodings=prompt_data['owl_encodings']
        )
        t1 = time.perf_counter_ns()
        dt = (t1 - t0) / 1e9
        total_processing_time += dt

        # Draw detections on the frame
        processed_frame = draw_tree_output(frame, detections, prompt_data['tree'])

        # Write the frame to the output video
        out.write(processed_frame)

        # Log progress
        frame_count += 1
        if frame_count % 10 == 0:
            logging.info(f"Processed {frame_count}/{total_frames} frames ({frame_count/total_frames*100:.1f}%)")

    # Release resources
    video.release()
    out.release()

    # Log summary
    avg_processing_time = total_processing_time / frame_count if frame_count > 0 else 0
    logging.info(f"Processing complete: {frame_count} frames processed")
    logging.info(f"Average processing time per frame: {avg_processing_time:.4f} seconds")
    logging.info(f"Output saved to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a video file with NanoOWL")
    parser.add_argument("--image_encode_engine", type=str, required=True, help="Path to the image encoder engine")
    parser.add_argument("--video_path", type=str, required=True, help="Path to the input video file")
    parser.add_argument("--output_path", type=str, required=True, help="Path to save the output video")
    parser.add_argument("--prompt", type=str, required=True, help="Detection prompt")
    parser.add_argument("--output_fps", type=float, help="Output video FPS (default: same as input)")
    parser.add_argument("--resize", type=str, help="Resize resolution as WIDTHxHEIGHT")
    parser.add_argument("--log_level", type=str, default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                        help="Logging level")

    args = parser.parse_args()

    # Configure logging
    numeric_level = getattr(logging, args.log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {args.log_level}")
    logging.basicConfig(level=numeric_level, format='%(asctime)s - %(levelname)s - %(message)s')

    # Process the video
    process_video(
        video_path=args.video_path,
        output_path=args.output_path,
        image_encode_engine=args.image_encode_engine,
        prompt=args.prompt,
        output_fps=args.output_fps,
        resize_resolution=args.resize
    )
