#!/usr/bin/env python3
"""Open an already-verified local PPTX in its associated desktop application."""
import argparse
import os
from pathlib import Path
import platform
import shutil
import subprocess


def open_pptx(path):
    path=Path(path).resolve()
    if not path.is_file() or path.suffix.lower() != '.pptx':
        raise ValueError('Expected an existing .pptx file')
    system=platform.system()
    if system=='Windows':
        os.startfile(str(path))
    else:
        command=shutil.which('open' if system=='Darwin' else 'xdg-open')
        if command is None:
            raise RuntimeError('No desktop file opener is available; use the printed absolute path')
        subprocess.run([command,str(path)],check=True,timeout=20,capture_output=True)
    return {'path':str(path),'status':'open-requested','note':'Desktop launch requested; this does not prove the application displayed the slide.'}


if __name__=='__main__':
    import json
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pptx')
    print(json.dumps(open_pptx(parser.parse_args().pptx),ensure_ascii=False))
