
set base_dir="Y:\git\DFLogTool"
set conda_home="C:\Users\Stranjyr\Anaconda3"
call pyinstaller ^
    HoverflyDataflashCombiner.spec

    @REM --onefile ^
    @REM --name HoverflyDataflashCombiner ^
    @REM --add-data="%base_dir%\log_parser\editor.kv;log_parser" ^
    @REM --add-binary="%conda_home%\pkgs\mkl-2021.3.0-haa95532_524\Library\bin\mkl_intel_thread.1.dll;." ^
    @REM -c ^
    @REM %base_dir%/gui.py