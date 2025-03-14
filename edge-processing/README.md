## Refactored to take in video file instead of video
## Will be consumed by Jetson

## Jetson super nano 8GB

jetson-containers run --workdir /opt/nanoowl $(autotag nanoowl)

docker cp video file to container:$path

python video_processor.py --image_encode_engine /opt/nanoowl/data/owl_image_encoder_patch32.engine --video_path path/to/input.mp4 --output_path path/to/output.mp4 --prompt "Find all cars and people in the scene"
