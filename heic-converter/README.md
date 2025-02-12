# Containerized HEIC to JPG Converter

A Docker container that efficiently converts HEIC images to JPG format. This tool handles batch conversion of HEIC files (commonly used by Apple devices) to the more widely compatible JPG format, while preserving directory structure and metadata.

## Features

- 🚀 Fast parallel processing
- 📁 Preserves directory structure
- 🔄 Automatic cleanup
- 🎛️ Configurable quality settings
- 📊 Progress tracking
- 🔒 Safe error handling
- 🖼️ Metadata preservation

## Prerequisites

- Docker
- Docker Compose (optional, but recommended)

## Quick Start

1. Clone this repository:
```bash
git clone https://github.com/yourusername/heic-converter
cd heic-converter
```

2. Place your HEIC files in the `data` directory:
```bash
mkdir -p data
cp /path/to/your/photos/*.HEIC data/
```

3. Run the converter:
```bash
./run.sh
```

That's it! Your converted JPG files will be in the same directory as your HEIC files.

## Project Structure

```
heic-converter/
├── Dockerfile              # Container definition
├── docker-compose.yml      # Docker Compose configuration
├── requirements.txt        # Python dependencies
├── heic_converter.py       # Main conversion script
├── run.sh                  # Convenience script
└── data/                   # Directory for your HEIC files
```

## Usage Options

### Using the Shell Script

Basic usage with default settings:
```bash
./run.sh
```

Custom quality setting (1-100):
```bash
QUALITY=90 ./run.sh
```

Custom number of worker threads:
```bash
WORKERS=8 ./run.sh
```

Custom input directory:
```bash
INPUT_DIR=/path/to/photos ./run.sh
```

Combine multiple settings:
```bash
QUALITY=90 WORKERS=8 INPUT_DIR=/path/to/photos ./run.sh
```

### Using Docker Directly

Build the image:
```bash
docker build -t heic-converter .
```

Basic usage:
```bash
docker run -v $(pwd)/data:/app/data heic-converter /app/data
```

With custom settings:
```bash
docker run -v $(pwd)/data:/app/data heic-converter /app/data -q 90 -w 8 --remove-originals
```

### Using Docker Compose

Basic usage:
```bash
docker-compose up
```

With environment variables:
```bash
QUALITY=90 WORKERS=8 docker-compose up
```

## Configuration Options

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `QUALITY` | 50 | JPG output quality (1-100) |
| `WORKERS` | 4 | Number of parallel conversion threads |
| `INPUT_DIR` | ./data | Directory containing HEIC files |

## Container Details

The container is built on Python 3.9-slim and includes:
- Essential system libraries for image processing
- Python packages for HEIC handling
- Optimized for size and performance

## Performance

Performance depends on:
- Number of CPU cores available
- Input/output disk speed
- Image sizes
- Quality setting

Typical performance on a 4-core system:
- ~2-3 seconds per image at quality 50
- ~3-4 seconds per image at quality 90

## Memory Usage

Memory usage scales with:
- Number of worker threads
- Image sizes
- Quality settings

Recommended minimum: 512MB RAM
Recommended for large batches: 1GB+ RAM

## Troubleshooting

### Common Issues

1. **Permission Denied**
```bash
chmod +x run.sh
```

2. **No Space Left**
```bash
docker system prune
```

3. **Container Crashes**
```bash
# Reduce number of workers
WORKERS=2 ./run.sh
```

## Best Practices

1. **Backup Your Files**
   - Always keep backups of original files
   - Test with a small batch first

2. **Resource Management**
   - Adjust workers based on CPU cores
   - Monitor system resources
   - Clean up Docker resources regularly

3. **Large Batches**
   - Process in smaller chunks
   - Use lower quality for initial tests
   - Monitor disk space

## Development

Want to contribute? Great! Here's how:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

### Testing Changes

```bash
# Build with no cache
docker build --no-cache -t heic-converter .

# Run with test files
docker run -v $(pwd)/test_data:/app/data heic-converter /app/data
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Python and Pillow
- HEIC support via pillow-heif
- Progress tracking with tqdm

## Support

Create an issue if you:
- Find a bug
- Want a new feature
- Have questions

---

Made with ❤️ by [BinGi]
