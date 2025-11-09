python -m nuitka ^
    --standalone ^
    --onefile ^
    --enable-plugin=pyside6 ^
    --include-package=qfluentwidgets ^
    --output-dir=dist ^
    --remove-output ^
    --follow-imports ^
    --assume-yes-for-downloads ^
    --lto=yes ^
    --windows-console-mode=disable ^
    --output-filename=PDFMerger.exe ^
    pdf_merger.py