#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统启动脚本
用于启动整个课程学生信息管理系统
"""

import subprocess
import sys
import os
import time
import signal

# 全局变量存储进程引用
backend_process = None
frontend_process = None

def signal_handler(sig, frame):
    """处理Ctrl+C信号，优雅关闭所有服务"""
    print("\n\n正在停止所有服务...")
    stop_all_services()
    print("所有服务已停止")
    sys.exit(0)

def stop_all_services():
    """停止所有服务"""
    global backend_process, frontend_process
    
    if backend_process and backend_process.poll() is None:
        print("停止后端服务...")
        backend_process.terminate()
        try:
            backend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            backend_process.kill()
    
    if frontend_process and frontend_process.poll() is None:
        print("停止前端服务...")
        frontend_process.terminate()
        try:
            frontend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            frontend_process.kill()

def start_backend():
    """启动后端服务"""
    global backend_process
    print("启动后端服务...")
    backend_process = subprocess.Popen([
        sys.executable, 
        os.path.join("backend", "app.py")
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return backend_process

def start_frontend():
    """启动前端服务"""
    global frontend_process
    print("启动前端服务...")
    frontend_process = subprocess.Popen([
        "npm", "run", "dev"
    ], cwd=os.path.join("frontend"), 
       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return frontend_process

def main():
    """主函数"""
    global backend_process, frontend_process
    
    print("课程学生信息管理系统启动器")
    print("=" * 40)
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # 启动后端服务
        backend_process = start_backend()
        print(f"后端服务已启动 (PID: {backend_process.pid})")
        
        # 等待后端服务启动
        print("等待后端服务启动...")
        time.sleep(8)
        
        # 启动前端服务
        try:
            frontend_process = start_frontend()
            print(f"前端服务已启动 (PID: {frontend_process.pid})")
        except FileNotFoundError:
            print("未找到npm命令，请确保已安装Node.js和npm")
            print("前端服务启动失败，但后端服务仍在运行")
        
        print("\n系统启动完成！")
        print("后端API服务: http://localhost:5000")
        print("前端界面: http://localhost:5173")
        print("\n按 Ctrl+C 停止所有服务并退出")
        
        # 保持脚本运行
        while True:
            if backend_process and backend_process.poll() is not None:
                print("后端服务已意外停止")
                break
            if frontend_process and frontend_process.poll() is not None:
                print("前端服务已意外停止")
                break
            time.sleep(1)
            
    except Exception as e:
        print(f"启动过程中发生错误: {e}")
    finally:
        stop_all_services()

if __name__ == "__main__":
    main()