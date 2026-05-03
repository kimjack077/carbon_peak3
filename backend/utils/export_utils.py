# backend/utils/export_utils.py
import io
import pandas as pd
from datetime import datetime

def generate_excel_report(data, scenario_name):
    """生成Excel格式的预测报告"""
    df = pd.DataFrame(data)

    # 重命名列
    df = df.rename(columns={
        'year': '年份',
        'data_type': '类型',
        'gdp': 'GDP(万元)',
        'energy_consumption': '能源消费(万吨标煤)',
        'co2_emission': 'CO2排放(万吨)'
    })

    # 类型转换
    df['类型'] = df['类型'].apply(lambda x: '历史' if x == 'historical' else '预测')

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='预测数据', index=False)

        # 获取工作表并设置格式
        workbook = writer.book
        worksheet = writer.sheets['预测数据']

        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#0F766E',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })

        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)

    output.seek(0)
    return output.getvalue()

def generate_summary_text(results, peak_info):
    """生成分析摘要文本"""
    peak_year = peak_info.get('year', '未知')
    peak_value = peak_info.get('value', 0)

    summary = f"""
    根据预测结果分析：

    1. 碳排放预计在 {peak_year} 年达到峰值，峰值排放量约为 {peak_value:.2f} 万吨CO2。

    2. 从历史趋势来看，碳排放呈现先上升后下降的典型达峰路径特征。

    3. 建议重点关注能源结构优化和效率提升，以实现更早的达峰目标。

    报告生成时间: {datetime.now().strftime('%Y年%m月%d日')}
    """
    return summary.strip()