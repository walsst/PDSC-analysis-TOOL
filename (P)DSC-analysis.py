import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io
import os

st.set_page_config(page_title="DSC数据分析工具", page_icon="📊", layout="wide")

# 应用标题
st.title("📊 DSC数据分析工具")
st.markdown("上传DSC数据文件，自动分析并生成图表")

# 侧边栏 - 文件上传和设置
with st.sidebar:
    st.header("文件上传")
    uploaded_file = st.file_uploader("选择CSV文件", type=['csv'])
    
    st.header("分析设置")
    show_peak = st.checkbox("显示峰值", value=True)
    show_grid = st.checkbox("显示网格", value=True)
    chart_style = st.selectbox("图表样式", ['默认', 'seaborn', 'ggplot', 'dark_background'])

# 主内容区
if uploaded_file is not None:
    try:
        # 读取数据
        try:
            df = pd.read_csv(uploaded_file, encoding='utf-8')
        except:
            try:
                df = pd.read_csv(uploaded_file, encoding='gbk')
            except:
                df = pd.read_csv(uploaded_file, encoding='latin1')
        
        # 重命名列
        if len(df.columns) >= 3:
            df.columns = ['Time', 'Temperature', 'HeatFlow'][:len(df.columns)]
        
        # 查找峰值
        max_heatflow_idx = df['HeatFlow'].idxmax()
        max_time = df.loc[max_heatflow_idx, 'Time']
        max_temp = df.loc[max_heatflow_idx, 'Temperature']
        max_heatflow = df.loc[max_heatflow_idx, 'HeatFlow']
        
        # 显示文件信息和统计
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("文件名", uploaded_file.name)
            st.metric("数据点数", len(df))
        with col2:
            st.metric("峰值温度", f"{max_temp:.2f} °C")
            st.metric("峰值热流", f"{max_heatflow:.3f} mW")
        with col3:
            st.metric("时间范围", f"{df['Time'].min():.1f} - {df['Time'].max():.1f} s")
            st.metric("温度范围", f"{df['Temperature'].min():.2f} - {df['Temperature'].max():.2f} °C")
        
        # 设置图表样式
        if chart_style != '默认':
            plt.style.use(chart_style)
        
        # 创建两个图表
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # 时间-热流曲线
        ax1.plot(df['Time'], df['HeatFlow'], 'b-', linewidth=1.5, label='Heat Flow')
        if show_peak:
            ax1.scatter(max_time, max_heatflow, color='red', s=100, zorder=5, 
                       label=f'Peak: {max_heatflow:.3f} mW at {max_temp:.2f}°C')
            ax1.axvline(x=max_time, color='red', linestyle='--', alpha=0.5)
            ax1.axhline(y=max_heatflow, color='red', linestyle='--', alpha=0.5)
        
        ax1.set_xlabel('Time (s)', fontsize=12)
        ax1.set_ylabel('Heat Flow (mW)', fontsize=12)
        ax1.set_title('Time vs Heat Flow', fontsize=14, fontweight='bold')
        if show_grid:
            ax1.grid(True, alpha=0.3)
        ax1.legend(loc='best')
        
        # 温度-热流曲线
        ax2.plot(df['Temperature'], df['HeatFlow'], 'g-', linewidth=1.5, label='Heat Flow')
        if show_peak:
            ax2.scatter(max_temp, max_heatflow, color='red', s=100, zorder=5, 
                       label=f'Peak: {max_heatflow:.3f} mW')
        
        ax2.set_xlabel('Temperature (°C)', fontsize=12)
        ax2.set_ylabel('Heat Flow (mW)', fontsize=12)
        ax2.set_title('Temperature vs Heat Flow', fontsize=14, fontweight='bold')
        if show_grid:
            ax2.grid(True, alpha=0.3)
        ax2.legend(loc='best')
        
        plt.tight_layout()
        
        # 显示图表
        st.pyplot(fig)
        
        # 数据预览
        with st.expander("查看数据"):
            st.dataframe(df)
        
        # 下载选项
        col1, col2, col3 = st.columns(3)
        with col1:
            # 下载图表
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
            st.download_button(
                label="下载图表 (PNG)",
                data=buf.getvalue(),
                file_name=f"{os.path.splitext(uploaded_file.name)[0]}_chart.png",
                mime="image/png"
            )
        
        with col2:
            # 下载CSV
            csv = df.to_csv(index=False)
            st.download_button(
                label="下载数据 (CSV)",
                data=csv,
                file_name=f"{os.path.splitext(uploaded_file.name)[0]}_processed.csv",
                mime="text/csv"
            )
            
        with col3:
            # 下载报告
            report = f"""DSC数据分析报告
=================

文件名: {uploaded_file.name}
分析时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

峰值信息:
--------
峰值时间: {max_time:.1f} s
峰值温度: {max_temp:.2f} °C
峰值热流: {max_heatflow:.3f} mW

数据统计:
--------
数据点数: {len(df)}
时间范围: {df['Time'].min():.1f} - {df['Time'].max():.1f} s
温度范围: {df['Temperature'].min():.2f} - {df['Temperature'].max():.2f} °C
热流范围: {df['HeatFlow'].min():.3f} - {df['HeatFlow'].max():.3f} mW
热流平均值: {df['HeatFlow'].mean():.3f} mW
热流标准差: {df['HeatFlow'].std():.3f} mW
"""
            st.download_button(
                label="下载报告 (TXT)",
                data=report,
                file_name=f"{os.path.splitext(uploaded_file.name)[0]}_report.txt",
                mime="text/plain"
            )
        
    except Exception as e:
        st.error(f"处理文件时出错: {str(e)}")
else:
    st.info("👈 请在左侧上传DSC数据文件（CSV格式）")
    
    # 示例说明
    with st.expander("查看数据格式要求"):
        st.markdown("""
        ### 数据格式要求
        
        CSV文件应包含以下三列（顺序不限，但程序会自动识别）：
        
        1. **时间 (Time)** - 单位：秒
        2. **温度 (Temperature)** - 单位：摄氏度
        3. **热流 (HeatFlow)** - 单位：毫瓦
        
        ### 示例数据格式：
        
        ```csv
        Time,Temperature,HeatFlow
        0,29.982,-0.793509
        1,29.991,-0.765195
        2,30.000,-0.731899
        ...
        ```
        
        ### 支持的文件编码：
        - UTF-8
        - GBK (中文编码)
        - Latin-1
        """)

# 页脚
st.markdown("---")
st.markdown("**DSC数据分析工具** | 自动检测热流峰值并生成分析图表")