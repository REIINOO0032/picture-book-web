export function getAuthorIncome() {
  let data = localStorage.getItem('authorIncome')
  if (!data) {
    data = JSON.stringify({
      total: 0,
      vipShare: 0,
      readReward: 0
    })
    localStorage.setItem('authorIncome', data)
  }
  return JSON.parse(data)
}

export function addIncome(money) {
  const inc = getAuthorIncome()
  inc.total += money
  inc.vipShare += money * 0.5
  inc.readReward += money * 0.2
  localStorage.setItem('authorIncome', JSON.stringify(inc))
}

export function onUserBecomeVip() {
  addIncome(1.0)
}

export function onBookRead() {
  addIncome(0.1)
}