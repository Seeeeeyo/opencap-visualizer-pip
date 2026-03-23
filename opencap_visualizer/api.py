#!/usr/bin/env python3
"""
OpenCap Visualizer Python API

Provides programmatic access to video generation functionality from biomechanics files.
"""

import asyncio
import os
import tempfile
import json
from pathlib import Path
from playwright.async_api import async_playwright
from typing import List, Dict, Optional, Union

# Configuration
DEFAULT_OUTPUT_FILENAME = "animation_video.mp4"
DEFAULT_VIEWPORT_SIZE = {"width": 1920, "height": 1080}
DEFAULT_FRAME_RATE = 30
DEFAULT_TIMEOUT = 120000  # 2 minutes in milliseconds


class OpenCapVisualizer:
    """
    Python API for generating videos from OpenCap biomechanics data.
    
    This class provides programmatic access to the same functionality available
    through the command-line interface, allowing you to generate videos directly
    from Python code.
    """
    
    def __init__(self, verbose: bool = False):
        """
        Initialize the OpenCap Visualizer.
        
        Args:
            verbose (bool): Enable verbose logging output. Default: False
        """
        self.browser = None
        self.page = None
        self.verbose = verbose
    
    def _log(self, message: str):
        """Helper to log messages only if verbose mode is enabled."""
        if self.verbose:
            print(message)
    
    def _process_subject_colors(self, color_input: List[str], num_subjects: int) -> Optional[List[str]]:
        """Process and validate subject colors, returning hex color strings."""
        
        # Color name to hex mapping (matching Session.vue's availableColors)
        color_names = {
            'red': '#ff0000',
            'green': '#00ff00', 
            'blue': '#0000ff',
            'yellow': '#ffff00',
            'magenta': '#ff00ff',
            'cyan': '#00ffff',
            'orange': '#ff8000',
            'purple': '#8000ff',
            'white': '#ffffff',
            'gray': '#808080',
            'grey': '#808080',
            'lightred': '#ff8080',
            'lightgreen': '#80ff80',
            'lightblue': '#8080ff',
            'lightpink': '#ff80ff',
            'lightcyan': '#80ffff',
            'lightorange': '#ffa040'
        }
        
        processed_colors = []
        
        for color in color_input:
            # Convert to lowercase for name matching
            color_lower = color.lower()
            
            # Check if it's a predefined color name
            if color_lower in color_names:
                processed_colors.append(color_names[color_lower])
            # Check if it's a valid hex color
            elif self._is_valid_hex_color(color):
                # Ensure it starts with #
                hex_color = color if color.startswith('#') else f'#{color}'
                processed_colors.append(hex_color.upper())
            else:
                self._log(f"Warning: Invalid color '{color}', skipping")
                continue
        
        if not processed_colors:
            return None
        
        # If we have fewer colors than subjects, cycle through them
        if len(processed_colors) < num_subjects:
            # Extend the list by cycling through existing colors
            original_colors = processed_colors.copy()
            while len(processed_colors) < num_subjects:
                processed_colors.extend(original_colors)
            # Trim to exact number needed
            processed_colors = processed_colors[:num_subjects]
        
        return processed_colors
    
    def _is_valid_hex_color(self, color: str) -> bool:
        """Check if a string is a valid hex color."""
        # Remove # if present
        hex_part = color[1:] if color.startswith('#') else color
        
        # Check if it's 3 or 6 characters and all hex digits
        if len(hex_part) == 3:
            return all(c in '0123456789ABCDEFabcdef' for c in hex_part)
        elif len(hex_part) == 6:
            return all(c in '0123456789ABCDEFabcdef' for c in hex_part)
        else:
            return False
    
    def _categorize_files(self, input_files: List[str]) -> Dict[str, List[str]]:
        """
        Categorize input files by type.
        
        Args:
            input_files: List of file paths
            
        Returns:
            Dictionary with categorized file lists
        """
        categorized = {
            'json': [],
            'osim': [],
            'mot': [],
            'trc': [],
            'force_mot': [],
            'motion_mot': []
        }
        
        for file_path in input_files:
            file_lower = file_path.lower()
            
            if file_lower.endswith('.json'):
                categorized['json'].append(file_path)
            elif file_lower.endswith('.osim'):
                categorized['osim'].append(file_path)
            elif file_lower.endswith('.mot'):
                # Check if it's a force file or motion file
                if self._is_force_mot_file(file_path):
                    categorized['force_mot'].append(file_path)
                else:
                    categorized['motion_mot'].append(file_path)
            elif file_lower.endswith('.trc'):
                categorized['trc'].append(file_path)
        
        return categorized
    
    def _is_force_mot_file(self, file_path: str) -> bool:
        """
        Check if a .mot file is a force file based on filename and content.
        
        Args:
            file_path: Path to the .mot file
            
        Returns:
            True if it's a force file, False otherwise
        """
        file_name = os.path.basename(file_path).lower()
        
        # First check: filename contains "force"
        if 'force' in file_name:
            return True
        
        # Second check: examine column headers
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            header_ended = False
            for line in lines:
                line = line.strip()
                
                if line == 'endheader':
                    header_ended = True
                    continue
                
                if not header_ended:
                    continue
                
                # This is the column headers line
                column_headers = line.split()
                
                # Check for force-related column names
                force_keywords = [
                    'force', 'ground_force', 'grf',
                    'force_vx', 'force_vy', 'force_vz',
                    'force_px', 'force_py', 'force_pz',
                    'moment', 'torque', 'cop'
                ]
                
                has_force_columns = any(
                    any(keyword in header.lower() for keyword in force_keywords)
                    for header in column_headers
                )
                
                return has_force_columns
        
        except Exception as e:
            self._log(f"Warning: Could not read {file_path} to determine type: {e}")
        
        return False

    async def generate_video(
        self,
        input_files: Union[str, List[str]],
        output_path: str = DEFAULT_OUTPUT_FILENAME,
        *,
        vue_app_path: Optional[str] = None,
        dev_server_url: Optional[str] = None,
        width: int = DEFAULT_VIEWPORT_SIZE["width"],
        height: int = DEFAULT_VIEWPORT_SIZE["height"],
        timeout_seconds: int = DEFAULT_TIMEOUT // 1000,
        loops: int = 1,
        camera: Optional[str] = None,
        center_subjects: bool = True,
        zoom: float = 0.8,
        colors: Optional[List[str]] = None,
        model: str = 'LaiArnold',
        interactive: bool = False,
        show_markers: bool = True,
        show_forces: bool = True,
        marker_size: float = 10.0,
        force_scale: float = 0.001
    ) -> bool:
        """
        Generate a video from biomechanics data files.
        
        Args:
            input_files (str or list): Path(s) to data file(s). Can be a single file path
                or list of file paths. Supports:
                - JSON files (pre-processed motion data)
                - .osim + .mot pairs (OpenSim models with motion)
                - .trc files (motion capture marker data) *
                - .mot files (force/motion data - auto-detected) *
                
                * Note: .trc and standalone .mot file support is currently being integrated.
                For full compatibility, use with JSON files or .osim/.mot pairs.
                
            output_path (str): Output video file path. Default: "animation_video.mp4"
            vue_app_path (str, optional): Absolute path to built Vue app's index.html
            dev_server_url (str, optional): URL of custom Vue server
            width (int): Video width in pixels. Default: 1920
            height (int): Video height in pixels. Default: 1080  
            timeout_seconds (int): Timeout in seconds for loading. Default: 120
            loops (int): Number of animation loops to record. Default: 1
                Note: For short animations (<3 seconds), loops will be automatically 
                increased to ensure a minimum 3-second video duration.
            camera (str, optional): Camera view position. Options include:
                - Original views: 'top', 'bottom', 'front', 'back', 'left', 'right'
                - Anatomical views: 'anterior', 'posterior', 'sagittal', 'superior', etc.
            center_subjects (bool): Enable automatic centering on subjects. Default: True
            zoom (float): Zoom factor (>1.0 zooms out, <1.0 zooms in). Default: 1.5
            colors (list, optional): Subject colors as hex strings or color names
            model (str): Geometry model folder: 'LaiArnold' (default) or 'Hu_ISB_shoulder'
            interactive (bool): Open browser interactively (no recording). Default: False
            show_markers (bool): Show markers from .trc files. Default: True
            show_forces (bool): Show forces from .mot files. Default: True
            marker_size (float): Size of marker spheres. Default: 10.0
            force_scale (float): Scale factor for force arrows. Default: 0.001
            
        Returns:
            bool: True if successful, False otherwise
            
        Examples:
            >>> visualizer = OpenCapVisualizer()
            >>> await visualizer.generate_video("data.json", "output.mp4")
            
            >>> # OpenSim files (fully supported)
            >>> await visualizer.generate_video(
            ...     ["model.osim", "motion.mot"],
            ...     "opensim_video.mp4",
            ...     camera="anterior",
            ...     loops=2
            ... )
            
            >>> # Multiple JSON files for comparison
            >>> await visualizer.generate_video(
            ...     ["subject1.json", "subject2.json"],
            ...     "comparison.mp4",
            ...     colors=["red", "blue"]
            ... )
        """
        # Convert single file to list
        if isinstance(input_files, str):
            input_files = [input_files]
        
        # Categorize files by type
        categorized_files = self._categorize_files(input_files)
        
        # Import the actual implementation from cli module
        from .cli import VisualizerCLI
        
        cli = VisualizerCLI()
        cli.verbose = self.verbose
        
        viewport_size = {"width": width, "height": height}
        timeout_ms = timeout_seconds * 1000
        
        # Prepare file lists for the CLI
        files_to_process = []
        
        # Add JSON files
        files_to_process.extend(categorized_files['json'])
        
        # Add .osim/.mot pairs
        if categorized_files['osim'] and categorized_files['motion_mot']:
            # Combine .osim and .mot files (assuming they're paired in order)
            min_pairs = min(len(categorized_files['osim']), len(categorized_files['motion_mot']))
            for i in range(min_pairs):
                files_to_process.extend([categorized_files['osim'][i], categorized_files['motion_mot'][i]])
        
        # Add standalone .trc and force .mot files
        files_to_process.extend(categorized_files['trc'])
        files_to_process.extend(categorized_files['force_mot'])
        
        # Note about automatic loop adjustment for short animations
        if self.verbose and loops > 0:
            self._log(f"Requested {loops} loop(s). Note: loops may be automatically increased for short animations to ensure minimum 3-second video duration.")
        
        # Use the CLI method (keeping existing name for compatibility)
        # Note: show_markers, show_forces, marker_size, force_scale are handled by the Vue app
        return await cli.create_video_from_json(
            json_file_paths=files_to_process,
            output_video_path=output_path,
            vue_app_path=vue_app_path,
            viewport_size=viewport_size,
            timeout_ms=timeout_ms,
            dev_server_url=dev_server_url,
            loop_count=loops,
            camera_view=camera,
            center_subjects=center_subjects,
            zoom_factor=zoom,
            subject_colors=colors,
            model_folder=model,
            interactive_mode=interactive,
            quiet_mode=not self.verbose
        )

    def generate_video_sync(
        self,
        input_files: Union[str, List[str]],
        output_path: str = DEFAULT_OUTPUT_FILENAME,
        **kwargs
    ) -> bool:
        """
        Synchronous wrapper for generate_video().
        
        This is a convenience method that runs the async generate_video() method
        in a new event loop, making it easier to use from non-async code.
        
        Args:
            Same as generate_video()
            
        Returns:
            bool: True if successful, False otherwise
            
        Examples:
            >>> visualizer = OpenCapVisualizer()
            >>> success = visualizer.generate_video_sync("data.json", "output.mp4")
            >>> if success:
            ...     print("Video generated successfully!")
            
                    >>> # With OpenSim files
        >>> success = visualizer.generate_video_sync(
        ...     ["model.osim", "motion.mot"],
        ...     "opensim_video.mp4",
        ...     camera="anterior"
        ... )
        """
        return asyncio.run(self.generate_video(input_files, output_path, **kwargs))


# Convenience functions for direct usage
async def create_video_async(
    input_files: Union[str, List[str]],
    output_path: str = DEFAULT_OUTPUT_FILENAME,
    **kwargs
) -> bool:
    """
    Asynchronous convenience function to generate a video without creating a class instance.
    
    Args:
        Same as OpenCapVisualizer.generate_video()
        
    Returns:
        bool: True if successful, False otherwise
        
    Example:
        >>> import opencap_visualizer as ocv
        >>> await ocv.create_video_async("data.json", "output.mp4", camera="anterior")
        
        >>> # With OpenSim files
        >>> await ocv.create_video_async(
        ...     ["model.osim", "motion.mot"],
        ...     "opensim_video.mp4",
        ...     camera="anterior"
        ... )
    """
    visualizer = OpenCapVisualizer(verbose=kwargs.pop('verbose', False))
    return await visualizer.generate_video(input_files, output_path, **kwargs)


def create_video(
    input_files: Union[str, List[str]], 
    output_path: str = DEFAULT_OUTPUT_FILENAME,
    **kwargs
) -> bool:
    """
    Synchronous convenience function to generate a video.
    
    Args:
        Same as OpenCapVisualizer.generate_video()
        
    Returns:
        bool: True if successful, False otherwise
        
    Example:
        >>> import opencap_visualizer as ocv
        >>> success = ocv.create_video("data.json", "output.mp4", camera="anterior")
        
        >>> # With OpenSim files
        >>> success = ocv.create_video(
        ...     ["model.osim", "motion.mot"],
        ...     "opensim_video.mp4",
        ...     camera="anterior"
        ... )
    """
    visualizer = OpenCapVisualizer(verbose=kwargs.pop('verbose', False))
    return visualizer.generate_video_sync(input_files, output_path, **kwargs) 