@echo off
echo Starting the GitHub AI System pipeline...

echo Running crawl_trending.py (爬取GitHub热榜)...
python crawl_trending.py
if %errorlevel% neq 0 (
    echo Error occurred while running crawl_trending.py
    pause
    exit /b %errorlevel%
)

echo.
echo Running crawl_readme.py (补全README内容)...
python crawl_readme.py
if %errorlevel% neq 0 (
    echo Error occurred while running crawl_readme.py
    pause
    exit /b %errorlevel%
)

echo.
echo Running ai_analyze.py (AI智能分析)...
python ai_analyze.py
if %errorlevel% neq 0 (
    echo Error occurred while running ai_analyze.py
    pause
    exit /b %errorlevel%
)

echo.
echo Running build_graph.py (构建贡献者图谱)...
python build_graph.py
if %errorlevel% neq 0 (
    echo Error occurred while running build_graph.py
    pause
    exit /b %errorlevel%
)

echo.
echo Running main.py...
python main.py
if %errorlevel% neq 0 (
    echo Error occurred while running main.py
    pause
    exit /b %errorlevel%
)

echo.
echo All scripts executed successfully!
pause