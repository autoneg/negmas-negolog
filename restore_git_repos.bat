
REM Repository: projects/negmas-negolog
echo Restoring: projects/negmas-negolog
if exist "projects\negmas-negolog\.git" (
    echo   Directory already exists, skipping...
) else (
    REM Create parent directory if needed
    if not exist "projects" mkdir "projects"

    REM Clone the repository
    git clone "git@github.com:autoneg/negmas-negolog.git" "projects\negmas-negolog"
    if errorlevel 1 (
        echo   Failed to clone
    ) else (
        echo   Successfully cloned

        REM Checkout the original branch if not already on it
        cd "projects\negmas-negolog"
        git checkout "main" 2>nul
        if errorlevel 1 (
            echo   Could not checkout branch: main
        ) else (
            echo   Checked out branch: main
        )
        cd ..\..
    )
)
echo.

REM Repository: projects/negmas-negolog
echo Restoring: projects/negmas-negolog
if exist "projects\negmas-negolog\.git" (
    echo   Directory already exists, skipping...
) else (
    REM Create parent directory if needed
    if not exist "projects" mkdir "projects"
    
    REM Clone the repository
    git clone "git@github.com:autoneg/negmas-negolog.git" "projects\negmas-negolog"
    if errorlevel 1 (
        echo   Failed to clone
    ) else (
        echo   Successfully cloned
        
        REM Checkout the original branch if not already on it
        cd "projects\negmas-negolog"
        git checkout "main" 2>nul
        if errorlevel 1 (
            echo   Could not checkout branch: main
        ) else (
            echo   Checked out branch: main
        )
        cd ..\..
    )
)
echo.

