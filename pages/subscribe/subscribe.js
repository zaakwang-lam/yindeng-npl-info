// pages/subscribe/subscribe.js
Page({
  data: {
    plans: [
      { id: 1, name: '基础提醒', price: 29 },
      { id: 2, name: '高级筛选+导出', price: 69 },
      { id: 3, name: '全功能', price: 99 }
    ]
  },
  buy(e) {
    // TODO: virtual payment
  }
})
