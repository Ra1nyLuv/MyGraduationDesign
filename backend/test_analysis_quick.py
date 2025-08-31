#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能分析API测试脚本
验证聚类分析和异常检测API是否能正常返回数据
"""

import sys
import os
import requests
import json

def test_ml_apis():
    """测试ML分析API"""
    print("🧪 测试智能分析API")
    print("="*60)
    
    base_url = "http://localhost:5000"
    
    apis = [
        {
            'name': '聚类分析',
            'url': f"{base_url}/api/ml/cluster-analysis",
            'method': 'GET'
        },
        {
            'name': '异常检测',
            'url': f"{base_url}/api/ml/anomaly-detection", 
            'method': 'GET'
        }
    ]
    
    for api in apis:
        print(f"\n📋 测试 {api['name']} API")
        print("-" * 30)
        
        try:
            # 发送请求
            if api['method'] == 'GET':
                response = requests.get(api['url'], timeout=30)
            else:
                response = requests.post(api['url'], json={}, timeout=30)
            
            print(f"📤 请求: {api['method']} {api['url']}")
            print(f"📥 状态码: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ 响应成功")
                    print(f"📊 响应数据结构:")
                    
                    if data.get('success'):
                        print(f"   ✅ 成功状态: {data['success']}")
                        
                        if api['name'] == '聚类分析':
                            analysis = data.get('analysis', {})
                            if analysis:
                                print(f"   📈 总用户数: {analysis.get('total_users', 0)}")
                                cluster_dist = analysis.get('cluster_distribution', {})
                                print(f"   🔗 聚类数量: {len(cluster_dist)}")
                                for cluster_id, cluster_info in cluster_dist.items():
                                    print(f"      聚类{cluster_id}: {cluster_info.get('name', '未知')} ({cluster_info.get('count', 0)}人)")
                            else:
                                print(f"   ⚠️ 无聚类分析数据")
                        
                        elif api['name'] == '异常检测':
                            results = data.get('results', {})
                            if results:
                                print(f"   📈 总用户数: {results.get('total_users', 0)}")
                                print(f"   🚨 异常用户数: {results.get('anomaly_count', 0)}")
                                print(f"   📊 异常率: {results.get('anomaly_rate', 0):.1f}%")
                                
                                anomalies = results.get('anomalies', [])
                                if anomalies:
                                    print(f"   🔍 异常详情:")
                                    for i, anomaly in enumerate(anomalies[:3]):  # 只显示前3个
                                        print(f"      {i+1}. 用户{anomaly.get('user_id')}: 严重程度={anomaly.get('severity')}")
                            else:
                                print(f"   ⚠️ 无异常检测数据")
                    else:
                        print(f"   ❌ API返回失败: {data.get('error', '未知错误')}")
                
                except json.JSONDecodeError:
                    print(f"   ❌ 响应不是有效的JSON格式")
                    print(f"   📄 原始响应: {response.text[:200]}...")
            
            else:
                print(f"❌ 请求失败: HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"💥 错误信息: {error_data.get('error', '未知错误')}")
                except:
                    print(f"💥 原始错误: {response.text[:200]}...")
        
        except requests.exceptions.ConnectionError:
            print(f"❌ 连接失败: 请确保Flask服务器正在运行")
            print(f"💡 启动命令: python app.py")
        except requests.exceptions.Timeout:
            print(f"❌ 请求超时: 服务器响应时间过长")
        except Exception as e:
            print(f"❌ 请求异常: {str(e)}")

if __name__ == "__main__":
    test_ml_apis()