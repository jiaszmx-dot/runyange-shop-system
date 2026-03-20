Page({
  data: {
    stores: [],
    services: []
  },

  onLoad() {
    const app = getApp();
    wx.request({
      url: `${app.globalData.apiBase}/stores`,
      header: { Authorization: `Bearer ${wx.getStorageSync("token") || ""}` },
      success: (res) => {
        this.setData({ stores: res.data || [] });
      }
    });
    wx.request({
      url: `${app.globalData.apiBase}/services`,
      header: { Authorization: `Bearer ${wx.getStorageSync("token") || ""}` },
      success: (res) => {
        this.setData({ services: res.data || [] });
      }
    });
  },

  gotoBooking() {
    wx.navigateTo({ url: "/pages/booking/booking" });
  },

  gotoMember() {
    wx.navigateTo({ url: "/pages/member/member" });
  }
});
