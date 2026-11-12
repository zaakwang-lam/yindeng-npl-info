Page({
  data: {
    plans: [
      { name: "免费", price: "0", desc: "浏览公开标题，打开详情" },
      { name: "提醒", price: "29", desc: "按关键词留下筛选条件" },
      { name: "专业", price: "69", desc: "导出标题列表" },
      { name: "全功能", price: "99", desc: "提醒加导出" }
    ],
  },
  onChoose(e) {
    wx.showModal({
      title: "开发预览",
      content: e.currentTarget.dataset.name + "档还没接微信支付。先用界面给同行看。",
      showCancel: false,
      confirmText: "知道了",
      confirmColor: "#1A365D",
    });
  },
});
