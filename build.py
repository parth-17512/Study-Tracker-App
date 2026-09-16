import os
import sys
import subprocess
import shutil
from pathlib import Path

def setup_icon():
    try:
        from PIL import Image
    except ImportError:
        print("Pillow is required to generate the icon. Please install it.")
        sys.exit(1)
        
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)
    
    icon_path = assets_dir / "studytrack.ico"
    # Source image from the AI generation
    source_img = Path(r"C:\Users\Parth singh\.gemini\antigravity-ide\brain\5c13d152-f2a8-4d9d-82f9-7d6ef60dda9a\studytrack_icon_1789573285385.jpg")
    
    if source_img.exists():
        img = Image.open(source_img)
        # Convert to RGBA to ensure proper icon transparency handling, even from jpg
        img = img.convert("RGBA")
        img.save(icon_path, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
        print(f"Created icon at {icon_path}")
    elif not icon_path.exists():
        print(f"Warning: Source image not found at {source_img}, and icon doesn't exist.")
    return icon_path

def build_app(mode="onedir"):
    print(f"\n--- Building StudyTrack ({mode}) ---")
    
    # Ensure pyinstaller is available
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller is not installed. Run: pip install pyinstaller")
        sys.exit(1)
        
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "StudyTrack",
        "--noconsole",
        "--clean",
        "--icon=assets/studytrack.ico",
        "main.py"
    ]
    
    if mode == "onedir":
        cmd.append("--onedir")
    elif mode == "onefile":
        cmd.append("--onefile")
        
    result = subprocess.run(cmd)
    if result.returncode == 0:
        print(f"\nBuild {mode} completed successfully!")
        if mode == "onedir":
            print(f"Executable: dist/StudyTrack/StudyTrack.exe")
        else:
            print(f"Executable: dist/StudyTrack.exe")
    else:
        print(f"\nBuild {mode} failed with return code {result.returncode}")
        sys.exit(result.returncode)

if __name__ == "__main__":
    setup_icon()
    
    # 1. Build ONEDIR as requested by the spec
    build_app("onedir")
    
    # 2. Build ONEFILE as requested by the spec
    build_app("onefile")
    
    print("\nPackaging Phase Complete.")
