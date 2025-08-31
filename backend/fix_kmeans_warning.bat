@echo off
echo ==========================================================
echo            修复Windows下KMeans内存泄漏警告
echo ==========================================================
echo.

echo 🔧 设置环境变量解决KMeans警告...
set OMP_NUM_THREADS=1
echo ✅ 已设置 OMP_NUM_THREADS=1

echo.
echo 📋 当前环境变量:
echo OMP_NUM_THREADS=%OMP_NUM_THREADS%

echo.
echo 🚀 启动优化后的Flask应用...
echo 这将解决scikit-learn KMeans在Windows上的内存泄漏警告

python app.py

echo.
echo ==========================================================
echo 💡 说明:
echo - 设置 OMP_NUM_THREADS=1 可以避免KMeans内存泄漏
echo - 这是scikit-learn在Windows+MKL环境下的已知问题
echo - 设置后ML性能依然正常，只是减少了并行度
echo ==========================================================

pause