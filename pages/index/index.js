const app = getApp();

Page({
  data: {
    keyword: "",
    regions: ["全部", "深圳", "重庆", "宁波", "甘肃", "全国", "广东"],
    region: "全部",
    list: [],
  },
  onLoad() { this.apply(); },
  onKeyword(e) { this.setData({ keyword: e.detail.value }); },
  onSearch() { this.apply(); },
  onRegion(e) {
    const region = e.currentTarget.dataset.region;
    this.setData({ region });
    this.apply(region, this.data.keyword);
  },
  apply(region, keyword) {
    const word = (keyword === undefined ? this.data.keyword : keyword || "").trim();
    const area = region || this.data.region;
    const list = app.globalData.notices.filter((item) => {
      const hitWord = !word || item.title.indexOf(word) >= 0 || item.assetType.indexOf(word) >= 0;
      const hitRegion = area === "全部" || item.region === area || item.title.indexOf(area) >= 0;
      return hitWord && hitRegion;
    });
    this.setData({ list });
  },
  onOpen(e) {
    wx.navigateTo({ url: "/pages/detail/detail?id=" + e.currentTarget.dataset.id });
  },
  goSubscribe() {
    wx.navigateTo({ url: "/pages/subscribe/subscribe" });
  },
});
