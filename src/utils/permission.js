const sensitiveWords = [
  '暴力', '色情', '恐怖', '血腥', '杀人', '死亡', '脏话',
  '自杀', '绑架', '毒品', '赌博', '虐待'
]

export function checkContent(text) {
  for (const word of sensitiveWords) {
    if (text.includes(word)) return { pass: false, word }
  }
  return { pass: true }
}

export function getUserInfo() {
  const user = localStorage.getItem('user') || '未知用户'
  const isVip = localStorage.getItem('isVip') === 'true'

  const today = new Date().toDateString()
  const lastDate = localStorage.getItem('lastGenerateDate')
  let count = Number(localStorage.getItem('generateCount') || 0)

  if (lastDate !== today) {
    count = 0
    localStorage.setItem('lastGenerateDate', today)
    localStorage.setItem('generateCount', 0)
  }

  return {
    username: user,
    isVip,
    leftCount: isVip ? 999 : Math.max(0, 3 - count),
    generateCount: count
  }
}

export function addGenerateCount() {
  const count = Number(localStorage.getItem('generateCount') || 0)
  localStorage.setItem('generateCount', count + 1)
}

export function openVip() {
  localStorage.setItem('isVip', 'true')
}