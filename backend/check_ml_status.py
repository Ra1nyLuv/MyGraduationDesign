#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速ML状态检查工具
帮助诊断"模型训练失败: 训练失败"问题
"""

import sys
import os

def check_status():
    """检查ML系统状态"""
    print("🔍 快速ML状态检查")
    print("="*50)
    
    # 1. 检查环境
    print("1️⃣ 检查Python环境...")
    print(f"   Python版本: {sys.version}")
    print(f"   工作目录: {os.getcwd()}")
    
    # 2. 检查依赖库
    print("\n2️⃣ 检查依赖库...")
    required_libs = ['numpy', 'pandas', 'sklearn', 'flask', 'pymysql']
    missing = []
    
    for lib in required_libs:
        try:
            __import__(lib)
            print(f"   ✅ {lib}")
        except ImportError:
            print(f"   ❌ {lib}")
            missing.append(lib)
    
    if missing:
        print(f"\n   ⚠️ 缺少库: {', '.join(missing)}")
        print("   安装命令: pip install " + " ".join(missing))
        return False
    
    # 3. 检查ML模块
    print("\n3️⃣ 检查ML模块...")
    try:
        sys.path.insert(0, os.getcwd())
        from ml_services import GradePredictionModel, LearningBehaviorClustering, AnomalyDetector
        print("   ✅ ML模块导入成功")
        
        # 测试初始化
        predictor = GradePredictionModel()
        clustering = LearningBehaviorClustering()
        detector = AnomalyDetector()
        print("   ✅ 模型初始化成功")
        
    except Exception as e:
        print(f"   ❌ ML模块问题: {str(e)}")
        return False
    
    # 4. 检查数据库连接
    print("\n4️⃣ 检查数据库连接...")
    try:
        from app import app, db, User
        
        with app.app_context():
            user_count = User.query.count()
            print(f"   ✅ 数据库连接正常")
            print(f"   📊 用户数量: {user_count}")
            
            if user_count < 3:
                print(f"   ⚠️ 用户数量不足: {user_count} < 3")
                print("   💡 需要至少3个用户才能进行模型训练")
                return False
                
    except Exception as e:
        print(f"   ❌ 数据库连接问题: {str(e)}")
        return False
    
    # 5. 检查模型训练
    print("\n5️⃣ 测试模型训练...")
    try:
        with app.app_context():
            users = User.query.options(
                db.joinedload(User.synthesis_grades),
                db.joinedload(User.homework_statistic),
                db.joinedload(User.discussion_participation),
                db.joinedload(User.video_watching_details)
            ).all()
            
            print(f"   📊 加载了 {len(users)} 个用户数据")
            
            # 快速测试预测模型
            predictor = GradePredictionModel()
            success = predictor.train_model(users)
            print(f"   📈 预测模型训练: {'✅ 成功' if success else '❌ 失败'}")
            
            if not success:
                print("   ⚠️ 预测模型训练失败，可能是数据质量问题")
                return False
                
    except Exception as e:
        print(f"   ❌ 模型训练测试失败: {str(e)}")
        return False
    
    print("\n🎉 所有检查通过！ML系统状态正常")
    return True

def show_solutions():
    """显示解决方案"""
    print("\n🔧 常见问题解决方案:")
    print("="*50)
    
    print("问题1: 依赖库缺失")
    print("解决: pip install scikit-learn numpy pandas flask pymysql")
    
    print("\n问题2: 用户数量不足")
    print("解决: 确保数据库中至少有3个用户数据")
    
    print("\n问题3: ML模块导入失败")
    print("解决: 检查ml_services目录是否存在")
    print("     检查__init__.py文件是否正确")
    
    print("\n问题4: 数据库连接失败")
    print("解决: 检查.env文件配置")
    print("     确保MySQL服务正在运行")
    
    print("\n问题5: 前端显示'训练失败'")
    print("解决: 重启Flask服务器: python app.py")
    print("     清空浏览器缓存并重新登录")
    print("     查看浏览器开发者工具的网络请求")

def main():
    """主函数"""
    print("🩺 ML系统快速诊断工具")
    print("="*60)
    
    success = check_status()
    
    if success:
        print("\n✅ 系统状态正常！")
        print("\n📝 如果前端仍显示'训练失败'：")
        print("1. 重启Flask服务器: python app.py")
        print("2. 刷新浏览器页面")
        print("3. 重新登录管理员账户")
        print("4. 点击'运行模型训练'按钮")
    else:
        show_solutions()

if __name__ == "__main__":
    main()