@echo off
echo ==========================================================
echo                ML模型训练问题诊断工具
echo ==========================================================
echo.

cd /d "e:\PyCharm\condaProjects\data_Visualization_Project_Design\backend"

echo 🔍 正在诊断ML模型训练问题...
echo.

echo 步骤1: 运行状态检查
python check_ml_status.py

echo.
echo 步骤2: 如果检查通过，请按以下步骤操作:
echo -------------------------------------------------------
echo 1. 重启Flask服务器
echo    命令: python app.py
echo.
echo 2. 等待服务器启动完成，看到以下信息:
echo    "Running on http://127.0.0.1:5000"
echo.
echo 3. 在浏览器中访问前端 (通常是 http://localhost:5173)
echo.
echo 4. 使用管理员账户登录 (用户名以admin开头)
echo.
echo 5. 进入管理员面板，点击"智能分析"标签页
echo.
echo 6. 点击"运行模型训练"按钮
echo.
echo 7. 查看训练结果
echo -------------------------------------------------------
echo.

echo 💡 调试技巧:
echo - 打开浏览器开发者工具 (F12)
echo - 查看Network标签页的请求响应
echo - 查看Console标签页的错误信息
echo - 观察Flask服务器控制台的日志输出
echo.

echo 📞 如果仍有问题，请提供以下信息:
echo - 浏览器控制台的错误信息
echo - Flask服务器的完整日志
echo - 点击训练按钮后的网络请求详情
echo.

echo ==========================================================
echo                   诊断完成
echo ==========================================================

pause