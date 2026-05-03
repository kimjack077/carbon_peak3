// frontend/src/utils/export.js
import XLSX from 'xlsx-js-style'
import jsPDF from 'jspdf'

export const exportToExcel = (data, scenarioName) => {
  const ws = XLSX.utils.json_to_sheet(data.map(row => ({
    '年份': row.year,
    '类型': row.data_type === 'historical' ? '历史' : '预测',
    'GDP(万元)': row.gdp,
    '能源消费(万吨标煤)': row.energy_consumption,
    'CO2排放(万吨)': row.co2_emission
  })))

  // 设置样式
  const range = XLSX.utils.decode_range(ws['!ref'])
  for (let R = range.s.r; R <= range.e.r; ++R) {
    for (let C = range.s.c; C <= range.e.c; ++C) {
      const cell = ws[XLSX.utils.encode_cell({ r: R, c: C })]
      if (!cell) continue

      cell.s = {
        fill: R === 0 ? { fgColor: { rgb: '0F766E' } } : undefined,
        font: {
          bold: R === 0,
          color: R === 0 ? { rgb: 'FFFFFF' } : { rgb: '000000' }
        },
        alignment: { horizontal: 'center', vertical: 'center' },
        border: {
          top: { style: 'thin', color: { rgb: 'CCCCCC' } },
          bottom: { style: 'thin', color: { rgb: 'CCCCCC' } },
          left: { style: 'thin', color: { rgb: 'CCCCCC' } },
          right: { style: 'thin', color: { rgb: 'CCCCCC' } }
        }
      }
    }
  }

  ws['!cols'] = [
    { wch: 8 }, { wch: 8 }, { wch: 14 }, { wch: 18 }, { wch: 14 }
  ]

  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '预测数据')
  XLSX.writeFile(wb, `${scenarioName}_预测结果.xlsx`)
}

export const exportToPDF = async (chartImage, scenarioName, summary) => {
  const pdf = new jsPDF('p', 'mm', 'a4')
  const pageWidth = pdf.internal.pageSize.getWidth()

  // 标题
  pdf.setFontSize(18)
  pdf.setTextColor(15, 118, 110)
  pdf.text(`${scenarioName} - 碳达峰预测报告`, pageWidth / 2, 20, { align: 'center' })

  // 图表
  if (chartImage) {
    const imgData = chartImage
    const imgWidth = pageWidth - 20
    const imgHeight = 80
    pdf.addImage(imgData, 'PNG', 10, 35, imgWidth, imgHeight)
  }

  // 分析摘要
  pdf.setFontSize(12)
  pdf.setTextColor(50, 50, 50)
  pdf.text('分析摘要:', 10, 130)
  pdf.setFontSize(10)
  pdf.text(summary, 15, 140, { maxWidth: pageWidth - 30 })

  // 日期
  pdf.setFontSize(10)
  pdf.setTextColor(100, 100, 100)
  const date = new Date().toLocaleDateString('zh-CN')
  pdf.text(`生成日期: ${date}`, pageWidth / 2, 280, { align: 'center' })

  pdf.save(`${scenarioName}_预测报告.pdf`)
}

export const downloadBlob = (blob, filename) => {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}