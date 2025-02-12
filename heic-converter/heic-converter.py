import os
import logging
import argparse
from pathlib import Path
from PIL import Image, UnidentifiedImageError
from pillow_heif import register_heif_opener
from concurrent.futures import ThreadPoolExecutor, as_completed
import shutil
from typing import Tuple, List, Generator
from dataclasses import dataclass
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

@dataclass
class ConversionStats:
    """Class to hold conversion statistics"""
    total_files: int = 0
    successful_conversions: int = 0
    failed_conversions: int = 0
    skipped_files: int = 0
    processed_directories: int = 0

class HeicConverter:
    """Class to handle HEIC to JPG conversion operations"""
    
    def __init__(self, input_dir: str, output_quality: int = 50, max_workers: int = 4, preserve_structure: bool = True):
        """
        Initialize the HEIC converter.
        
        Args:
            input_dir (str): Directory containing HEIC files
            output_quality (int): Quality of output JPG (1-100)
            max_workers (int): Number of parallel conversion threads
            preserve_structure (bool): Whether to preserve directory structure in output
        """
        self.input_dir = Path(input_dir)
        self.output_quality = max(1, min(100, output_quality))  # Clamp between 1-100
        self.max_workers = max_workers
        self.preserve_structure = preserve_structure
        self.stats = ConversionStats()
        self.converted_dir = self.input_dir / "ConvertedFiles"
        
        # Register HEIF opener at initialization
        register_heif_opener()
    
    def convert_single_file(self, heic_path: Path, jpg_path: Path) -> Tuple[Path, bool]:
        """
        Convert a single HEIC file to JPG format.
        
        Args:
            heic_path (Path): Path to the HEIC file
            jpg_path (Path): Path to save the converted JPG file
            
        Returns:
            Tuple[Path, bool]: Path to the HEIC file and conversion status
        """
        try:
            # Create the parent directory if it doesn't exist
            jpg_path.parent.mkdir(parents=True, exist_ok=True)
            
            with Image.open(heic_path) as image:
                image.save(jpg_path, "JPEG", quality=self.output_quality)
            
            # Preserve original timestamps
            heic_stat = os.stat(heic_path)
            os.utime(jpg_path, (heic_stat.st_atime, heic_stat.st_mtime))
            return heic_path, True
            
        except (UnidentifiedImageError, FileNotFoundError, OSError) as e:
            logging.error(f"Error converting '{heic_path.name}': {str(e)}")
            return heic_path, False

    def get_heic_files(self) -> Generator[Path, None, None]:
        """
        Get all HEIC files from the input directory recursively.
        
        Yields:
            Path: Path to each HEIC file found
        """
        for root_dir, _, files in os.walk(self.input_dir):
            root_path = Path(root_dir)
            if "ConvertedFiles" in root_path.parts:
                continue
                
            for file in files:
                if file.lower().endswith(('.heic', '.HEIC')):
                    yield root_path / file

    def get_output_path(self, heic_path: Path) -> Path:
        """
        Determine the output path for a converted file.
        
        Args:
            heic_path (Path): Path to the original HEIC file
            
        Returns:
            Path: Path where the converted JPG should be saved
        """
        if self.preserve_structure:
            # Calculate relative path from input directory
            rel_path = heic_path.relative_to(self.input_dir)
            # Create the same structure under ConvertedFiles
            return self.converted_dir / rel_path.parent / f"{rel_path.stem}.jpg"
        else:
            # Put all files in the root of ConvertedFiles
            return self.converted_dir / f"{heic_path.stem}.jpg"

    def setup_output_directory(self) -> None:
        """Create output directory if it doesn't exist"""
        self.converted_dir.mkdir(exist_ok=True)

    def convert_files(self) -> ConversionStats:
        """
        Convert all HEIC files to JPG format using parallel processing.
        
        Returns:
            ConversionStats: Statistics about the conversion process
        """
        if not self.input_dir.is_dir():
            raise FileNotFoundError(f"Directory '{self.input_dir}' does not exist.")

        # Setup output directory
        self.setup_output_directory()

        # Get list of all HEIC files
        heic_files = list(self.get_heic_files())
        self.stats.total_files = len(heic_files)

        if not heic_files:
            logging.info("No HEIC files found in the specified directory.")
            return self.stats

        # Prepare conversion tasks
        tasks = []
        for heic_path in heic_files:
            jpg_path = self.get_output_path(heic_path)
            
            if jpg_path.exists():
                logging.info(f"Skipping '{heic_path.name}' as JPG already exists.")
                self.stats.skipped_files += 1
                continue
                
            tasks.append((heic_path, jpg_path))

        # Convert files in parallel with progress bar
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self.convert_single_file, heic_path, jpg_path): heic_path
                for heic_path, jpg_path in tasks
            }
            
            with tqdm(total=len(tasks), desc="Converting files") as pbar:
                for future in as_completed(futures):
                    _, success = future.result()
                    if success:
                        self.stats.successful_conversions += 1
                    else:
                        self.stats.failed_conversions += 1
                    pbar.update(1)

        # Count processed directories
        processed_dirs = {heic_path.parent for heic_path, _ in tasks}
        self.stats.processed_directories = len(processed_dirs)

        return self.stats

    def cleanup(self, remove_originals: bool = False, move_to_main: bool = False) -> None:
        """
        Perform cleanup operations after conversion.
        
        Args:
            remove_originals (bool): Whether to remove original HEIC files
            move_to_main (bool): Whether to move converted files to main directory
        """
        if move_to_main:
            # Move converted files to main directory, preserving structure
            for jpg_file in self.converted_dir.rglob('*.jpg'):
                # Calculate relative path from ConvertedFiles
                rel_path = jpg_file.relative_to(self.converted_dir)
                target_path = self.input_dir / rel_path
                
                # Create target directory if needed
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                if target_path.exists():
                    target_path.unlink()
                shutil.move(str(jpg_file), str(target_path))
            
            # Remove empty directories in ConvertedFiles
            for dir_path in sorted(self.converted_dir.rglob('*'), reverse=True):
                if dir_path.is_dir() and not any(dir_path.iterdir()):
                    dir_path.rmdir()
            
            # Remove ConvertedFiles if empty
            if self.converted_dir.exists() and not any(self.converted_dir.iterdir()):
                self.converted_dir.rmdir()

        if remove_originals:
            # Remove original HEIC files only if conversion exists
            for heic_file in self.get_heic_files():
                jpg_path = (self.input_dir if move_to_main else self.converted_dir) / \
                          (heic_file.relative_to(self.input_dir).parent if self.preserve_structure else '') / \
                          f"{heic_file.stem}.jpg"
                          
                if jpg_path.exists():  # Only remove if conversion exists
                    heic_file.unlink()

def main():
    parser = argparse.ArgumentParser(
        description="Convert HEIC images to JPG format.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("input_dir", type=str, help="Directory containing HEIC images")
    parser.add_argument("-q", "--quality", type=int, default=50,
                        help="Output JPG quality (1-100, default: 50)")
    parser.add_argument("-w", "--workers", type=int, default=4,
                        help="Number of parallel workers (default: 4)")
    parser.add_argument("--remove-originals", action="store_true",
                        help="Remove original HEIC files after successful conversion")
    parser.add_argument("--move-to-main", action="store_true",
                        help="Move converted files to main directory")
    parser.add_argument("--flat-structure", action="store_true",
                        help="Don't preserve directory structure in output")

    args = parser.parse_args()

    try:
        converter = HeicConverter(
            args.input_dir,
            output_quality=args.quality,
            max_workers=args.workers,
            preserve_structure=not args.flat_structure
        )
        
        stats = converter.convert_files()
        
        # Perform cleanup if requested
        converter.cleanup(
            remove_originals=args.remove_originals,
            move_to_main=args.move_to_main
        )
        
        # Print final statistics
        logging.info("\nConversion Summary:")
        logging.info(f"Total files processed: {stats.total_files}")
        logging.info(f"Successfully converted: {stats.successful_conversions}")
        logging.info(f"Failed conversions: {stats.failed_conversions}")
        logging.info(f"Skipped files: {stats.skipped_files}")
        logging.info(f"Directories processed: {stats.processed_directories}")
        
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
