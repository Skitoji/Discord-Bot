import os
import subprocess
import sys
import zipfile
import requests
from pathlib import Path

def install_ffmpeg():
    """Descargar e instalar FFmpeg automáticamente"""
    print("📥 Descargando FFmpeg...")
    
    ffmpeg_dir = Path("C:/ffmpeg")
    ffmpeg_bin = ffmpeg_dir / "bin" / "ffmpeg.exe"
    
    # Si ya existe, no descargar
    if ffmpeg_bin.exists():
        print("✅ FFmpeg ya está instalado")
        add_to_path(str(ffmpeg_dir / "bin"))
        return True
    
    try:
        # URL de descarga
        url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        zip_path = Path("ffmpeg.zip")
        
        print(f"📥 Descargando desde {url}...")
        response = requests.get(url, stream=True)
        
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print("📦 Extrayendo archivos...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall("C:/")
        
        # Renombrar carpeta
        extracted = Path("C:/ffmpeg-master-latest-win64-gpl")
        if extracted.exists():
            extracted.rename(ffmpeg_dir)
        
        # Limpiar zip
        zip_path.unlink()
        
        # Agregar a PATH
        add_to_path(str(ffmpeg_dir / "bin"))
        
        print("✅ FFmpeg instalado correctamente en C:/ffmpeg")
        return True
        
    except Exception as e:
        print(f"❌ Error instalando FFmpeg: {e}")
        return False

def add_to_path(path):
    """Agregar directorio al PATH"""
    try:
        # Para Windows
        os.environ['PATH'] = path + os.pathsep + os.environ['PATH']
        
        # Intentar agregar permanentemente
        subprocess.run(
            f'setx PATH "{path};%PATH%"',
            shell=True,
            check=False
        )
        print(f"✅ {path} agregado al PATH")
    except Exception as e:
        print(f"⚠️ No se pudo agregar al PATH: {e}")

if __name__ == "__main__":
    install_ffmpeg()
