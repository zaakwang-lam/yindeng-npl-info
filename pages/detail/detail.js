const app = getApp();

Page({
  data: { item: null },

  onLoad(query) {
    const item = app.globalData.notices.find((row) => row.id === query.id) || null;
    this.setData({ item });
    if (!item) {
      wx.showToast({ title: "没找到这条", icon: "none" });
    }
  },

  onCopy() {
    const item = this.data.item;
    if (!item || !item.url) {
      wx.showToast({ title: "演示包没有原文链接", icon: "none" });
      return;
    }
    wx.setClipboardData({
      data: item.title + "\n" + item.url,
      success() {
        wx.showToast({ title: "链接已复制", icon: "none" });
      },
    });
  },
});
