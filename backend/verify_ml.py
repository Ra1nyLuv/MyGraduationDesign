#!/usr/bin/env python3
"""
机器学习功能验证脚本
快速验证ML模块是否正确安装和配置
"""

import sys
import os

def test_imports():
    """测试ML模块导入"""
    print("🔍 测试ML模块导入...")
    
    try:
        # 测试核心库导入
        import numpy as np
        import pandas as pd
        import sklearn
        print("  ✅ 核心ML库导入成功")
        
        # 测试自定义模块导入
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from ml_services import (
            GradePredictionModel,
            LearningBehaviorClustering,
            PersonalizedRecommendation,
            AnomalyDetector
        )
        print("  ✅ 自定义ML模块导入成功")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ 导入失败: {str(e)}")
        return False
    except Exception as e:
        print(f"  ❌ 未知错误: {str(e)}")
        return False

def test_model_initialization():
    """测试模型初始化"""
    print("\n🛠️ 测试模型初始化...")
    
    try:
        from ml_services import (
            GradePredictionModel,
            LearningBehaviorClustering,
            PersonalizedRecommendation,
            AnomalyDetector
        )
        
        # 初始化所有模型
        predictor = GradePredictionModel()
        clustering = LearningBehaviorClustering()
        recommender = PersonalizedRecommendation()
        detector = AnomalyDetector()
        
        print("  ✅ 所有模型初始化成功")
        return True
        
    except Exception as e:
        print(f"  ❌ 模型初始化失败: {str(e)}")
        return False

def test_dependencies():
    """测试依赖库版本"""
    print("\n📦 检查依赖库版本...")
    
    try:
        import sklearn
        import numpy
        import pandas
        import joblib
        
        print(f"  - scikit-learn: {sklearn.__version__}")
        print(f"  - numpy: {numpy.__version__}")
        print(f"  - pandas: {pandas.__version__}")
        print(f"  - joblib: {joblib.__version__}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 版本检查失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("🚀 机器学习功能验证")
    print("=" * 50)
    
    # 运行所有测试
    tests = [
        test_dependencies,
        test_imports,
        test_model_initialization
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！ML功能已正确配置")
        return True
    else:
        print("⚠️ 部分测试失败，请检查配置")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)