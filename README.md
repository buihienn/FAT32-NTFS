# FAT32-NTFS Simulation

## Overview
This project is a simulation application that demonstrates the structure and working principles of FAT32 and NTFS file systems. It provides a user-friendly GUI to explore and perform basic operations on both file systems.

## Features
- Simulates the structure and functionality of FAT32 and NTFS file systems.
- User-friendly GUI built with PyQt6 and Qt Designer.
- Supports basic operations for both FAT32 and NTFS.

## Requirements
- Python 3.11 or higher
- PyQt6

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/FAT32-NTFS.git
   cd FAT32-NTFS
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Run the main application:
   ```bash
   python main.py
   ```
2. Use the GUI to explore and perform operations on FAT32 and NTFS file systems.

## File Structure
- `main.py`: Entry point of the application.
- `FAT32.py`: Implements FAT32 file system simulation.
- `NTFS.py`: Implements NTFS file system simulation.
- `gui.py` and `gui.ui`: GUI implementation using PyQt6 and Qt Designer.
- `choose_volume.py` and `menu.py`: Additional modules for volume selection and menu handling.
- `TreeDirectory.py`: Handles directory tree structure.
- `MFTEntry.py` and `NTFSAttribute.py`: NTFS-specific components.

## Authors
Developed by Bui Hien and Dau Gia Lam - Students of HCMUS.

## Timeline
- **March 2024 - April 2024**: Development and testing phase.
