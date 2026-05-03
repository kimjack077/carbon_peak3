// frontend/src/utils/helpers.js
export const formatNumber = (value, decimals = 2) => {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return '-'
  return Number(value).toLocaleString('zh-CN', { maximumFractionDigits: decimals })
}

export const formatPercent = (value, decimals = 1) => {
  if (value === null || value === undefined) return '-'
  return `${(Number(value) * 100).toFixed(decimals)}%`
}

export const debounce = (fn, delay = 300) => {
  let timer = null
  return function(...args) {
    clearTimeout(timer)
    timer = setTimeout(() => fn.apply(this, args), delay)
  }
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

export const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms))